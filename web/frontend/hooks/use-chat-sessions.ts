/**
 * Hook quản lý toàn bộ logic chat sessions.
 * Tách từ ChatInterface.tsx để component chỉ lo render UI.
 */
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import type { ChatSession, Message } from '@/lib/types';
import { CHAT_STORAGE_MODE, STORAGE_KEYS } from '@/lib/constants';

const createSessionId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
};

interface DbMessage {
  id: string;
  role: string;
  content: string;
  contextUsed?: Message['contextUsed'];
}

const mapDbMessage = (m: DbMessage): Message => ({
  id: m.id,
  role: m.role as 'user' | 'assistant',
  content: m.content,
  contextUsed: m.contextUsed || []
});

interface DbSession {
  session_id: string;
  title?: string;
  updated_at?: string;
  message_count?: number | string;
}

interface LocalChatSnapshot {
  sessions: ChatSession[];
  messages: Record<string, Message[]>;
  activeSessionId: string | null;
}

const parseJsonItem = <T,>(value: string | null, fallback: T): T => {
  if (!value) return fallback;
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
};

const readLocalChatSnapshot = (): LocalChatSnapshot => ({
  sessions: parseJsonItem<ChatSession[]>(localStorage.getItem(STORAGE_KEYS.sessions), []),
  messages: parseJsonItem<Record<string, Message[]>>(localStorage.getItem(STORAGE_KEYS.messages), {}),
  activeSessionId: localStorage.getItem(STORAGE_KEYS.activeSessionId),
});

const sessionFromLocalMessages = (id: string, messages: Message[]): ChatSession => {
  const firstUserMessage = messages.find(message => message.role === 'user');
  const lastMessage = messages.at(-1);
  const titleSource = firstUserMessage?.content || 'Cuộc trò chuyện mới';
  return {
    id,
    title: titleSource.substring(0, 30) + (titleSource.length > 30 ? '...' : ''),
    lastMessage: lastMessage?.content || '',
    timestamp: Number(id) || Date.now(),
  };
};

const getLocalSessionsWithMessages = ({ sessions, messages }: LocalChatSnapshot): ChatSession[] => {
  const sessionById = new Map(sessions.map(session => [session.id, session]));
  return Object.entries(messages)
    .filter(([, sessionMessages]) => sessionMessages.length > 0)
    .map(([id, sessionMessages]) => sessionById.get(id) || sessionFromLocalMessages(id, sessionMessages));
};

const warnRecoverableSessionsIssue = (message: string, details?: unknown) => {
  if (process.env.NODE_ENV !== 'production') {
    console.warn(`[Chat Sessions] ${message}`, details ?? '');
  }
};

const chooseCompleteMessages = (cached: Message[] | undefined, dbMessages: Message[]) => {
  if (!cached || dbMessages.length >= cached.length) {
    return dbMessages;
  }
  return cached;
};

export function useChatSessions(userId?: string | null) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSessionLoading, setIsSessionLoading] = useState(false);
  const [isSessionsListLoading, setIsSessionsListLoading] = useState(true);
  const [messagesBySession, setMessagesBySession] = useState<Record<string, Message[]>>({});
  const [isMounted, setIsMounted] = useState(false);
  const sessionLoadSeqRef = useRef(0);

  const stateRef = useRef({ sessions, currentSessionId, messagesBySession });
  useEffect(() => {
    stateRef.current = { sessions, currentSessionId, messagesBySession };
  }, [sessions, currentSessionId, messagesBySession]);

  const currentMessages = currentSessionId
    ? messagesBySession[currentSessionId] || []
    : [];

  // --- Tạo session mới ---
  const handleNewChat = useCallback(() => {
    const { currentSessionId, messagesBySession } = stateRef.current;
    
    // Nếu đang ở session rỗng rồi thì không tạo thêm
    if (currentSessionId && (!messagesBySession[currentSessionId] || messagesBySession[currentSessionId].length === 0)) {
      return;
    }

    const newId = createSessionId();
    setCurrentSessionId(newId);
    localStorage.setItem(STORAGE_KEYS.activeSessionId, newId);
    setMessagesBySession(prev => ({ ...prev, [newId]: [] }));
  }, []);

  // --- Chọn session ---
  const handleSelectSession = useCallback(async (id: string) => {
    const { currentSessionId, messagesBySession } = stateRef.current;
    if (id === currentSessionId) return;

    const loadSeq = ++sessionLoadSeqRef.current;
    setCurrentSessionId(id);
    localStorage.setItem(STORAGE_KEYS.activeSessionId, id);

    if (CHAT_STORAGE_MODE === 'browser') {
      return;
    }

    const cachedMessages = messagesBySession[id];
    if (!cachedMessages) {
      setIsSessionLoading(true);
    }

    try {
      const res = await fetch(`/api/chat/session/${id}/messages`);
      if (res.ok) {
        const dbMsgs = await res.json() as DbMessage[];
        const dbMessages = dbMsgs.map(mapDbMessage);
        setMessagesBySession(prev => ({
          ...prev,
          [id]: chooseCompleteMessages(prev[id], dbMessages)
        }));
      } else if (!cachedMessages) {
        warnRecoverableSessionsIssue(`Messages API returned ${res.status}; keeping local state for session ${id}.`);
        setMessagesBySession(prev => ({ ...prev, [id]: [] }));
      }
    } catch (err) {
      warnRecoverableSessionsIssue(`Messages API is unavailable; keeping local state for session ${id}.`, err);
      if (!cachedMessages) {
        setMessagesBySession(prev => ({ ...prev, [id]: [] }));
      }
    } finally {
      if (sessionLoadSeqRef.current === loadSeq) {
        setIsSessionLoading(false);
      }
    }
  }, []);

  // --- Xóa session ---
  const handleDeleteSession = useCallback((id: string) => {
    if (CHAT_STORAGE_MODE === 'postgres') {
    // Gọi API xóa ở backend không đồng bộ
    fetch(`/api/chat/session/${id}`, { method: 'DELETE' })
      .then(res => {
        if (!res.ok) console.warn(`[Delete Session] Backend trả về ${res.status} cho session ${id}`);
      })
      .catch(err => {
        warnRecoverableSessionsIssue(`Delete session API is unavailable; removed local session ${id}.`, err);
      });

    // Cập nhật đồng thời cả sessions và messages trong cùng một lần render
    }

    const { currentSessionId, sessions, messagesBySession } = stateRef.current;
    const remaining = sessions.filter(s => s.id !== id);

    // Xóa messages của session bị xóa
    const nextMessages = { ...messagesBySession };
    delete nextMessages[id];
    setMessagesBySession(nextMessages);

    if (currentSessionId === id) {
      if (remaining.length > 0) {
        setCurrentSessionId(remaining[0].id);
        localStorage.setItem(STORAGE_KEYS.activeSessionId, remaining[0].id);
        setSessions(remaining);
      } else {
        // Tạo ID mới nếu không còn session nào, nhưng KHÔNG add vào sessions list
        const newId = createSessionId();
        nextMessages[newId] = [];
        setMessagesBySession({ ...nextMessages });
        setCurrentSessionId(newId);
        localStorage.setItem(STORAGE_KEYS.activeSessionId, newId);
        setSessions([]);
      }
    } else {
      setSessions(remaining);
    }
  }, []);

  // --- Thêm message vào session hiện tại ---
  const addMessage = useCallback((message: Message) => {
    if (!currentSessionId) return;
    setMessagesBySession(prev => ({
      ...prev,
      [currentSessionId]: [...(prev[currentSessionId] || []), message],
    }));

    setSessions(prev => {
      const idx = prev.findIndex(s => s.id === currentSessionId);
      // Dùng displayContent làm title nếu có (tránh lấy extracted text từ file)
      const displayText = message.displayContent || message.content;
      if (idx === -1) {
        return [{
          id: currentSessionId,
          title: displayText.substring(0, 40) + (displayText.length > 40 ? '...' : ''),
          lastMessage: displayText,
          timestamp: Date.now()
        }, ...prev];
      }
      return prev.map(s =>
        s.id === currentSessionId
          ? { ...s, lastMessage: displayText, timestamp: Date.now() }
          : s
      );
    });
  }, [currentSessionId]);

  // --- Cập nhật message ---
  const updateMessage = useCallback((sessionId: string, messageId: string, updates: Partial<Message>) => {
    setMessagesBySession(prev => {
      const sessionMessages = prev[sessionId];
      if (!sessionMessages) return prev;
      return {
        ...prev,
        [sessionId]: sessionMessages.map(m => m.id === messageId ? { ...m, ...updates } : m)
      };
    });
  }, []);

  // --- Cập nhật title session ---
  const updateSessionTitle = useCallback((sessionId: string, title: string) => {
    const trimmedTitle = title.substring(0, 30) + (title.length > 30 ? '...' : '');
    setSessions(prev =>
      prev.map(s =>
        s.id === sessionId
          ? { ...s, title: trimmedTitle }
          : s
      )
    );

    if (CHAT_STORAGE_MODE === 'postgres') {
      fetch(`/api/chat/session/${sessionId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: trimmedTitle }),
      }).catch(err => {
        warnRecoverableSessionsIssue(`Failed to update session title on backend for session ${sessionId}.`, err);
      });
    }
  }, []);

  // ================================================================
  // Auth-aware data loading
  // Triggers on mount AND every time userId changes (login / logout)
  // ================================================================
  useEffect(() => {
    // userId === undefined  → auth state still loading, wait
    if (userId === undefined) return;

    setIsMounted(true);

    // Helper: restore from localStorage (guest mode)
    const restoreLocalSnapshot = (snapshot: LocalChatSnapshot) => {
      const localSessions = getLocalSessionsWithMessages(snapshot)
        .sort((a, b) => b.timestamp - a.timestamp);
      setSessions(localSessions);
      setMessagesBySession(snapshot.messages);
      if (snapshot.activeSessionId && snapshot.messages[snapshot.activeSessionId]) {
        setCurrentSessionId(snapshot.activeSessionId);
        return;
      }
      if (localSessions.length > 0) {
        setCurrentSessionId(localSessions[0].id);
        localStorage.setItem(STORAGE_KEYS.activeSessionId, localSessions[0].id);
        return;
      }
      handleNewChat();
    };

    // ---- GUEST (not logged in): localStorage only ----
    if (!userId) {
      const snapshot = readLocalChatSnapshot();
      restoreLocalSnapshot(snapshot);
      setIsSessionLoading(false);
      setIsSessionsListLoading(false);
      return;
    }

    // ---- LOGGED IN: DB only, never localStorage ----
    // Clear any guest state lingering from before login
    setSessions([]);
    setMessagesBySession({});
    setCurrentSessionId(null);
    setIsSessionsListLoading(true);

    const loadFromDB = async () => {
      try {
        const res = await fetch('/api/chat/sessions');
        if (!res.ok) {
          const body = await res.text().catch(() => '');
          warnRecoverableSessionsIssue(`Sessions API returned ${res.status}.`, body.slice(0, 160));
          handleNewChat();
          return;
        }

        const dbSessions = await res.json() as DbSession[];
        if (!Array.isArray(dbSessions)) {
          warnRecoverableSessionsIssue('Sessions API unexpected payload.');
          handleNewChat();
          return;
        }

        const filteredSessions = dbSessions.filter(s => Number(s.message_count || 0) > 0);

        if (filteredSessions.length === 0) {
          // User has no sessions yet → start fresh
          handleNewChat();
          return;
        }

        const loadedSessions: ChatSession[] = filteredSessions.map(dbSession => ({
          id: dbSession.session_id,
          title: dbSession.title || 'Cuộc trò chuyện mới',
          lastMessage: '',
          timestamp: dbSession.updated_at ? new Date(dbSession.updated_at).getTime() : Date.now(),
        }));
        loadedSessions.sort((a, b) => b.timestamp - a.timestamp);
        const activeId = loadedSessions[0].id;

        setSessions(loadedSessions);
        setCurrentSessionId(activeId);

        // Load messages of the active session
        setIsSessionLoading(true);
        try {
          const msgRes = await fetch(`/api/chat/session/${activeId}/messages`);
          if (msgRes.ok) {
            const dbMsgs = await msgRes.json() as DbMessage[];
            setMessagesBySession({ [activeId]: dbMsgs.map(mapDbMessage) });
          } else {
            setMessagesBySession({ [activeId]: [] });
          }
        } catch {
          setMessagesBySession({ [activeId]: [] });
        }
        setIsSessionLoading(false);
      } catch (err) {
        warnRecoverableSessionsIssue('Sessions API unavailable.', err);
        handleNewChat();
      } finally {
        setIsSessionLoading(false);
        setIsSessionsListLoading(false);
      }
    };

    loadFromDB();
  }, [userId, handleNewChat]);

  // ================================================================
  // Persist to localStorage — ONLY for guests (userId is null/undefined)
  // Logged-in users: sessions live in DB, never written to localStorage
  // ================================================================
  useEffect(() => {
    if (!isMounted) return;
    if (userId) return; // Logged-in users: do NOT touch localStorage

    // Guest mode: save current state as cache
    const validSessions = sessions.filter(s => messagesBySession[s.id] && messagesBySession[s.id].length > 0);
    const validMessages: Record<string, Message[]> = {};
    validSessions.forEach(s => { validMessages[s.id] = messagesBySession[s.id]; });
    localStorage.setItem(STORAGE_KEYS.sessions, JSON.stringify(validSessions));
    localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(validMessages));
    if (currentSessionId) {
      localStorage.setItem(STORAGE_KEYS.activeSessionId, currentSessionId);
    }
  }, [sessions, messagesBySession, currentSessionId, isMounted, userId]);

  return {
    sessions,
    currentSessionId,
    currentMessages,
    isMounted,
    handleNewChat,
    handleSelectSession,
    handleDeleteSession,
    addMessage,
    updateMessage,
    updateSessionTitle,
    isSessionLoading,
    isSessionsListLoading,
  };
}
