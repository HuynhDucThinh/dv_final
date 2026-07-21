'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, PanelLeft, LibraryBig, Check, ChevronDown, Square, ArrowDown, X, Plus, Settings, Mic, Paperclip, FileText, Image as ImageIcon, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useSpeechRecognition } from '@/hooks/use-speech-recognition';
import { ProviderSelector } from './ProviderSelector';
import { AdvancedSettings, AdvancedConfig } from './AdvancedSettings';
import { InferenceSetupModal } from './InferenceSetupModal';
import { ChatMessage } from './ChatMessage';
import { Sidebar } from './Sidebar';
import { ChatEmptyState } from './ChatEmptyState';
import type { ChatProcessingStage } from './ChatProcessingTrace';
import { SourceList } from './Sources';
import { CHAT_CONTENT_WIDTH_CLASS, CHAT_ROW_WIDTH_CLASS } from './layout';
import { useChatSessions } from '@/hooks/use-chat-sessions';
import { useClickOutside } from '@/hooks/use-click-outside';
import { useAISettings } from '@/hooks/use-ai-settings';
import {
  isInferenceConfigured,
  setRoleByModel,
  toRuntimeInferenceConfig,
} from '@/lib/ai-settings';
import {
  ALL_LAWS_CATEGORY,
  CHAT_STORAGE_MODE,
  LAW_CATEGORIES,
} from '@/lib/constants';
import type { Message, DocumentChunk } from '@/lib/types';
import { useTranslation } from 'react-i18next';
import { useFileAttachments } from '@/hooks/use-file-attachments';
import { useSession } from '@/lib/auth-client';

export function ChatInterface() {
  const { t } = useTranslation();
  const { data: authSession } = useSession();
  // undefined = auth đang load, null = chưa đăng nhập, string = đã đăng nhập
  const userId = authSession === undefined ? undefined : (authSession?.user?.id ?? null);

  const {
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
  } = useChatSessions(userId);

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { settings: aiSettings, setSettings: setAISettings } = useAISettings();
  const model = aiSettings.roles.answer.model;
  const advancedConfig: AdvancedConfig = {
    temperature: aiSettings.temperature,
    maxTokens: aiSettings.maxTokens,
    topK: aiSettings.topK,
  };
  const setModel = (nextModel: string) =>
    setAISettings(current => setRoleByModel(current, 'answer', nextModel));
  const setAdvancedConfig = (config: AdvancedConfig) =>
    setAISettings(current => ({ ...current, ...config }));
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Mode chat: chỉ dùng car
  const chatMode = 'car' as const;
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  // Streaming state
  const [streamingText, setStreamingText] = useState('');
  const [streamingContext, setStreamingContext] = useState<DocumentChunk[]>([]);
  const [processingStage, setProcessingStage] = useState<ChatProcessingStage>('idle');
  const abortControllerRef = useRef<AbortController | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);

  // File attachments
  const { attachments, isUploading, addFiles, removeAttachment, clearAttachments, getFullTexts } = useFileAttachments();

  // States for mini-map
  const [activeMessageId, setActiveMessageId] = useState<string | null>(null);
  const [hoveredMessageId, setHoveredMessageId] = useState<string | null>(null);

  const [drawerContext, setDrawerContext] = useState<DocumentChunk[] | null>(null);

  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);

  const handleTouchStart = (e: React.TouchEvent) => setTouchStart(e.targetTouches[0].clientX);
  const handleTouchMove = (e: React.TouchEvent) => setTouchEnd(e.targetTouches[0].clientX);
  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    const distance = touchStart - touchEnd;
    if (distance > 50 && isSidebarOpen) setIsSidebarOpen(false); // Swipe left
    if (distance < -50 && !isSidebarOpen) setIsSidebarOpen(true); // Swipe right
    setTouchStart(0);
    setTouchEnd(0);
  };

  const userMessages = currentMessages.filter(m => m.role === 'user');

  useEffect(() => {
    if (!scrollContainerRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.id.replace('message-', '');
            const idx = currentMessages.findIndex(m => m.id === id);
            if (idx !== -1) {
              // Find the closest preceding user message
              for (let i = idx; i >= 0; i--) {
                if (currentMessages[i].role === 'user') {
                  setActiveMessageId(currentMessages[i].id);
                  break;
                }
              }
            }
          }
        });
      },
      {
        root: scrollContainerRef.current,
        rootMargin: '-49% 0px -49% 0px', // Exact center line
      }
    );

    currentMessages.forEach(msg => {
      const el = document.getElementById(`message-${msg.id}`);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [currentMessages]);

  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
      setIsAtBottom(scrollHeight - scrollTop - clientHeight < 50);

      if (scrollTop < 20 && userMessages.length > 0) {
        setActiveMessageId(userMessages[0].id);
      }
    }
  };

  // Auto-sync Drawer Context when activeMessageId changes (if Drawer is open)
  useEffect(() => {
    if (activeMessageId) {
      const userIndex = currentMessages.findIndex(m => m.id === activeMessageId);
      if (userIndex !== -1 && userIndex + 1 < currentMessages.length) {
        const nextMsg = currentMessages[userIndex + 1];
        if (nextMsg.role === 'assistant') {
          setDrawerContext(prev => {
            if (prev !== null) {
              if (nextMsg.contextUsed && nextMsg.contextUsed.length > 0) {
                return prev !== nextMsg.contextUsed ? nextMsg.contextUsed : prev;
              } else {
                return []; // Open but empty context
              }
            }
            return prev;
          });
        }
      }
    }
  }, [activeMessageId, currentMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentMessages.length, streamingText, isLoading]);

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  };

  const { isListening, isSupported, toggleListening } = useSpeechRecognition({
    onResult: (text) => {
      setInput((prev) => {
        const newVal = prev + text;
        if (textareaRef.current) {
          setTimeout(() => {
            if (textareaRef.current) {
              textareaRef.current.style.height = 'auto';
              textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
            }
          }, 10);
        }
        return newVal;
      });
    },
  });

  const handleMicClick = () => {
    if (isListening) {
      toggleListening();
      setTimeout(() => {
        if (textareaRef.current) {
          const finalValue = textareaRef.current.value;
          if (finalValue.trim()) {
            handleSubmit(undefined, finalValue);
          }
        }
      }, 500);
    } else {
      toggleListening();
    }
  };

  const handleAbort = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setProcessingStage('cancelled');
    }
  };

  const handleFeedbackSubmit = async (messageId: string, type: 1 | -1, reason?: string, comment?: string) => {
    if (!currentSessionId) return;
    const msgIndex = currentMessages.findIndex(m => m.id === messageId);
    if (msgIndex < 0) return;
    const aiMsg = currentMessages[msgIndex];
    let userQuery = '';
    for (let i = msgIndex - 1; i >= 0; i--) {
      if (currentMessages[i].role === 'user') {
        userQuery = currentMessages[i].content;
        break;
      }
    }

    // Save locally immediately
    updateMessage(currentSessionId, messageId, { feedback: type });

    if (CHAT_STORAGE_MODE === 'browser') {
      return;
    }

    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_id: messageId,
          session_id: currentSessionId,
          user_query: userQuery,
          ai_response: aiMsg.content,
          context_used: aiMsg.contextUsed,
          feedback_type: type,
          reason,
          comment,
        }),
      });
    } catch (e) {
      console.error('Feedback error:', e);
    }
  };

  const handleSubmit = async (e?: React.FormEvent, overrideText?: string) => {
    if (e) e.preventDefault();

    // Neu dang loading: Enter/Click = huy
    if (isLoading) {
      handleAbort();
      return;
    }

    const userText = (overrideText ?? input).trim();
    if (!userText && attachments.length === 0) return;
    if (!currentSessionId) return;

    // Lấy extracted text từ các file đính kèm
    let fullMessage = userText;
    if (attachments.length > 0) {
      const textMap = await getFullTexts();
      const fileContextParts: string[] = [];

      for (const att of attachments) {
        if (att.status !== 'done') continue;
        if (att.file.type.startsWith('image/') && att.publicUrl) {
          fileContextParts.push(`[Ảnh đính kèm: ${att.file.name}]\nURL: ${att.publicUrl}`);
        } else if (textMap.has(att.id)) {
          const text = textMap.get(att.id)!;
          fileContextParts.push(`[Nội dung file: ${att.file.name}]\n\"\"\"\n${text}\n\"\"\"`);
        } else if (att.publicUrl) {
          fileContextParts.push(`[File đính kèm: ${att.file.name}]\nURL: ${att.publicUrl}`);
        }
      }

      if (fileContextParts.length > 0) {
        fullMessage = fileContextParts.join('\n\n') + (userText ? `\n\nCâu hỏi: ${userText}` : '');
      }
    }

    setInput('');
    clearAttachments();
    if (textareaRef.current) textareaRef.current.style.height = '52px';

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: fullMessage,
      // displayContent: chỉ hiện câu hỏi người dùng gõ (ẩn extracted text)
      displayContent: userText || undefined,
      // attachments: danh sách file để hiện card trong chat
      attachments: attachments
        .filter(a => a.status === 'done')
        .map(a => ({
          id: a.id,
          name: a.file.name,
          mimeType: a.file.type,
          publicUrl: a.publicUrl,
          previewUrl: a.previewUrl,
          sizeBytes: a.file.size,
        })),
    };
    addMessage(userMessage);

    if (currentMessages.length === 0 && currentSessionId) {
      updateSessionTitle(currentSessionId, userText.length > 40 ? userText.substring(0, 40) + '...' : userText);
    }

    setIsLoading(true);
    setStreamingText('');
    setStreamingContext([]);
    setProcessingStage('analyzing');

    const controller = new AbortController();
    abortControllerRef.current = controller;

    let accumulated = '';
    let fullContext: DocumentChunk[] = [];
    let contextUsed: DocumentChunk[] = [];
    let aborted = false;
    let streamErrorMessage = '';

    try {
      const apiMessages = [...currentMessages, userMessage].map(m => ({ role: m.role, content: m.content }));
      setProcessingStage('searching');

      // ===== THÊM MỚI: Nếu mode Car, gọi analysis API thay vì document API =====
      if (chatMode === 'car') {
        // Đi qua Next.js proxy để tự động thêm X-User-Id header
        const carRes = await fetch('/api/chat/analysis', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: apiMessages,
            model: aiSettings.roles.answer.model,
            session_id: currentSessionId || 'unknown',
            session_title: currentMessages.length === 0
              ? (userText.length > 40 ? userText.substring(0, 40) + '...' : userText)
              : (sessions.find(s => s.id === currentSessionId)?.title || 'Cuộc trò chuyện mới'),
            inferenceConfig: toRuntimeInferenceConfig(aiSettings),
          }),
          signal: controller.signal,
        });
        if (!carRes.ok || !carRes.body) throw new Error('Phản hồi từ máy chủ không khả dụng');
        const carReader = carRes.body.getReader();
        const carDecoder = new TextDecoder();
        let carBuf = '';
        setProcessingStage('generating');
        while (true) {
          const { done, value } = await carReader.read();
          if (done) break;
          carBuf += carDecoder.decode(value, { stream: true });
          const lines = carBuf.split('\n');
          carBuf = lines.pop() || '';
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            try {
              const ev = JSON.parse(line.slice(6));
              if (ev.type === 'token') { accumulated += ev.content; setStreamingText(accumulated); }
              else if (ev.type === 'done') setProcessingStage('completed');
              else if (ev.type === 'error') { streamErrorMessage = ev.content; setProcessingStage('error'); }
            } catch { /* skip */ }
          }
        }
        // Flush message và return (không chạy code document bên dưới)
        const carContent = accumulated || (streamErrorMessage ? streamErrorMessage : 'Không có phản hồi từ AI.');
        addMessage({ id: (Date.now() + 1).toString(), role: 'assistant', content: carContent, processingStage: streamErrorMessage ? 'error' : 'completed' });
        return;
      }
      // ===== KẼT THÚC phần Car =====

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: apiMessages,
          model,
          sessionId: currentSessionId || 'unknown',
          sessionTitle: currentMessages.length === 0 ? (userText.length > 40 ? userText.substring(0, 40) + '...' : userText) : (sessions.find(s => s.id === currentSessionId)?.title || 'Cuộc trò chuyện mới'),
          messageId: userMessage.id,
          temperature: advancedConfig.temperature,
          maxTokens: advancedConfig.maxTokens,
          topK: advancedConfig.topK,
          candidateK: aiSettings.candidateK,
          cacheThreshold: aiSettings.cacheThreshold,
          maxSubqueries: aiSettings.maxSubqueries,
          historyMessages: aiSettings.historyMessages,
          contextTokenBudget: aiSettings.contextTokenBudget,
          maxCitations: aiSettings.maxCitations,
          llmTimeout: aiSettings.llmTimeout,
          streaming: aiSettings.streaming,
          useHistoryForRewriter: aiSettings.useHistoryForRewriter,
          enableQueryRewriter: aiSettings.enableQueryRewriter,
          enableReranker: aiSettings.enableReranker,
          enableSemanticCache: aiSettings.enableSemanticCache,
          enableMemory: aiSettings.enableMemory,
          inferenceConfig: toRuntimeInferenceConfig(aiSettings)
        }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error('Phản hồi từ máy chủ không khả dụng');
      }

      if (!aiSettings.streaming) {
        const data = await response.json();
        accumulated = data.text || '';
        contextUsed = (data.contextUsed || []).slice(0, aiSettings.maxCitations);
        setProcessingStage('completed');
        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: accumulated || 'Không có phản hồi từ AI.',
          contextUsed,
          processingStage: 'completed',
        });
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;

          try {
            const event = JSON.parse(raw);

            if (event.type === 'context') {
              fullContext = event.data || [];
              contextUsed = fullContext;
              setStreamingContext(fullContext);
              setProcessingStage('selecting');
            } else if (event.type === 'token') {
              accumulated += event.text;
              setProcessingStage('generating');

              const citedIds = Array.from(accumulated.matchAll(/<cite\s+id=["']([^"']+)["']>/g)).map(m => m[1]).slice(0, aiSettings.maxCitations);
              if (citedIds.length > 0) {
                const filteredContext = fullContext.filter(ctx =>
                  ctx.metadata?.id && citedIds.includes(ctx.metadata.id as string)
                );
                if (filteredContext.length > 0) {
                  setStreamingContext(filteredContext);
                  contextUsed = filteredContext;
                }
              }

              setStreamingText(accumulated);
            } else if (event.type === 'done') {
              setProcessingStage('completed');
            } else if (event.type === 'error') {
              streamErrorMessage = event.message || 'stream-error';
              setProcessingStage('error');
            }
          } catch {
            // Ignore JSON parse errors
          }
        }
      }

      // Flush vao messages
      const finalText = aborted
        ? `${accumulated}${accumulated ? '\n\n' : ''}Đã dừng yêu cầu.`
        : streamErrorMessage
          ? accumulated || (contextUsed.length > 0
              ? 'Đã tìm thấy nguồn tham khảo nhưng chưa thể tổng hợp câu trả lời. Bạn vẫn có thể xem các căn cứ bên dưới.'
              : 'Không thể hoàn tất câu trả lời lúc này. Vui lòng thử lại.')
          : accumulated;

      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: finalText || 'Không có phản hồi từ AI.',
        contextUsed,
        processingStage: streamErrorMessage ? 'error' : aborted ? 'cancelled' : 'completed',
      });

    } catch (error: unknown) {
      const isAbort = error instanceof DOMException
        ? error.name === 'AbortError'
        : error instanceof Error && error.name === 'AbortError';

      aborted = isAbort;
      if (isAbort) {
        setProcessingStage('cancelled');
        if (accumulated) {
          addMessage({
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `${accumulated}\n\nĐã dừng yêu cầu.`,
            contextUsed,
            processingStage: 'cancelled',
          });
        } else {
          addMessage({
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: 'Đã dừng yêu cầu.',
            contextUsed,
            processingStage: 'cancelled',
          });
        }
      } else {
        setProcessingStage('error');
        const content = contextUsed.length > 0
          ? 'Đã tìm thấy nguồn tham khảo nhưng chưa thể tổng hợp câu trả lời. Bạn vẫn có thể xem các căn cứ bên dưới.'
          : 'Không thể hoàn tất câu trả lời lúc này. Vui lòng thử lại.';
        addMessage({
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content,
          contextUsed,
          processingStage: 'error',
        });
      }
    } finally {
      setIsLoading(false);
      setStreamingText('');
      setStreamingContext([]);
      setProcessingStage('idle');
      abortControllerRef.current = null;
    }
  };

  const SessionSkeletonLoader = () => (
    <div className="animate-pulse flex flex-col gap-6 py-5 px-4 max-w-4xl mx-auto">
      {/* Fake User Message */}
      <div className="flex justify-end gap-3 w-full mt-4">
        <div className="h-10 w-64 bg-gray-200/80 dark:bg-gray-800/80 rounded-2xl rounded-tr-sm"></div>
        <div className="h-8 w-8 bg-gray-200/80 dark:bg-gray-800/80 rounded-full flex-shrink-0"></div>
      </div>

      {/* Fake AI Message */}
      <div className="flex justify-start gap-3 w-full">
        <div className="h-8 w-8 bg-blue-100/80 dark:bg-blue-900/40 rounded-full flex-shrink-0"></div>
        <div className="space-y-3 pt-1">
          <div className="h-3.5 w-64 bg-gray-200/80 dark:bg-gray-800/80 rounded"></div>
          <div className="h-3.5 w-48 bg-gray-200/80 dark:bg-gray-800/80 rounded"></div>
          <div className="h-3.5 w-80 bg-gray-200/80 dark:bg-gray-800/80 rounded"></div>
        </div>
      </div>
    </div>
  );

  // Tin nhan dang stream (hien thi realtime)
  const streamingMessage: Message | null = isLoading
    ? {
        id: 'streaming',
        role: 'assistant',
        content: streamingText,
        contextUsed: streamingContext.length > 0 ? streamingContext : undefined,
        processingStage,
      }
    : null;

  if (!isMounted) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ background: '#F8FAFC' }}>
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-blue-100 rounded-full" />
            <div className="w-12 h-12 border-4 border-blue-600 rounded-full border-t-transparent animate-spin absolute top-0 left-0" />
          </div>
          <span className="text-gray-400 font-medium text-sm animate-pulse">Khởi tạo hệ thống...</span>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex h-screen overflow-hidden font-sans relative selection:bg-blue-100 dark:selection:bg-blue-500/30 transition-colors bg-white dark:bg-[#212121]"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {isSidebarOpen && (
        <button
          type="button"
          aria-label="Đóng danh sách hội thoại"
          className="fixed inset-0 z-30 bg-slate-950/30 backdrop-blur-[1px] md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <div className={`fixed inset-y-0 left-0 z-40 h-full w-72 overflow-hidden transition-transform duration-300 ease-in-out md:relative md:z-20 md:flex-shrink-0 md:transition-all ${
        isSidebarOpen ? 'translate-x-0 md:w-64 md:opacity-100' : '-translate-x-full md:translate-x-0 md:w-14 md:opacity-100'
      }`}>
        <div className={`h-full w-72 transition-all duration-300 ${isSidebarOpen ? 'md:w-64' : 'md:w-14'}`}>
          {/* Full Sidebar */}
          <div className={`h-full w-72 md:w-64 transition-opacity duration-300 ${isSidebarOpen ? 'opacity-100 relative' : 'opacity-0 absolute pointer-events-none'}`}>
          <Sidebar
            sessions={sessions}
            currentSessionId={currentSessionId}
            onNewChat={handleNewChat}
            onSelectSession={(id) => {
              handleSelectSession(id);
              if (window.innerWidth < 768) setIsSidebarOpen(false);
            }}
            onDeleteSession={handleDeleteSession}
            onRenameSession={updateSessionTitle}
            onCloseSidebar={() => setIsSidebarOpen(false)}
            isSessionsListLoading={isSessionsListLoading}
          />
          </div>
          
          {/* Mini Sidebar (Icons Only) */}
          <div className={`hidden md:flex flex-col items-center py-3 w-14 h-full border-r border-gray-200 dark:border-gray-800 bg-[#F9F9F9] dark:bg-[#171717] absolute top-0 left-0 transition-opacity duration-300 ${isSidebarOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
            <button onClick={() => setIsSidebarOpen(true)} className="p-2 mb-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-200 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-colors" title="Mở sidebar">
              <PanelLeft className="w-5 h-5" />
            </button>
            <button onClick={handleNewChat} className="p-2 mb-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-200 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-colors" title="Đoạn chat mới">
              <Plus className="w-5 h-5" />
            </button>
            <div className="flex-1"></div>
            <Link href="/admin" className="p-2 mb-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-200 dark:hover:text-gray-200 dark:hover:bg-gray-800 transition-colors" title="Quản trị">
              <Settings className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0 relative h-full">
        <div className="flex items-center justify-between bg-white/80 dark:bg-[#171717]/80 backdrop-blur-md z-10 absolute top-0 left-0 right-0 px-4 py-3 border-b border-gray-200/60 dark:border-white/10 transition-colors">
          <div className="flex items-center gap-3">
            <span className="text-sm font-bold text-gray-800 tracking-tight md:hidden">VietCar AI</span>
          </div>
          <div className="text-[10.5px] font-bold text-gray-600 dark:text-gray-400 uppercase tracking-widest px-3 py-1 rounded-full md:block hidden bg-gray-100 dark:bg-gray-800">
            {t('chat.carSystemHeader', 'Hệ thống phân tích dữ liệu ô tô')}
          </div>
          {CHAT_STORAGE_MODE === 'browser' && (
            <div className="text-[10px] font-medium text-slate-500 dark:text-slate-400 px-2 py-1 rounded-full bg-slate-100 dark:bg-white/10">
              Lá»‹ch sá»­ chá»‰ lÆ°u trÃªn thiáº¿t bá»‹ nÃ y
            </div>
          )}
        </div>

        {/* History Mini-map Stack */}
        {userMessages.length > 0 && (
          <div className="absolute right-2 top-1/2 -translate-y-1/2 z-30 group hidden md:flex items-center">
            {/* The Tooltip / Popup */}
            <div className="absolute right-full pr-4 py-4 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 pointer-events-none group-hover:pointer-events-auto z-50">
              <div className="bg-white border border-gray-200/60 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.15)] rounded-2xl w-72 max-h-[60vh] overflow-hidden flex flex-col relative">
                <div className="overflow-y-auto custom-scrollbar p-2 relative z-10 bg-white">
                  {userMessages.map(msg => (
                    <button
                      key={msg.id}
                      onMouseEnter={() => setHoveredMessageId(msg.id)}
                      onMouseLeave={() => setHoveredMessageId(null)}
                      onClick={() => {
                        setActiveMessageId(msg.id);
                        document.getElementById(`message-${msg.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                      }}
                      className={`w-full text-left px-3 py-2.5 text-[13px] font-medium rounded-xl truncate transition-colors mb-0.5 last:mb-0 ${
                        activeMessageId === msg.id
                          ? 'text-gray-900 bg-gray-200 dark:text-gray-100 dark:bg-gray-700'
                          : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-800'
                      }`}
                      title={msg.content}
                    >
                      {msg.content}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* The Stack Lines */}
            <div className="flex flex-col items-center justify-center gap-1.5 py-4 w-8 cursor-pointer">
              {userMessages.map((msg, i) => {
                const isActive = msg.id === activeMessageId;
                const isHovered = msg.id === hoveredMessageId;
                const isHighlight = isActive || isHovered;
                return (
                  <div
                    key={msg.id}
                    className={`h-[2px] rounded-full transition-all duration-300 ${
                      isHighlight
                        ? 'bg-gray-700 dark:bg-gray-300 w-6'
                        : 'bg-gray-300 dark:bg-gray-600 w-4 group-hover:bg-gray-400 dark:group-hover:bg-gray-500 group-hover:w-5'
                    }`}
                  />
                );
              })}
            </div>
          </div>
        )}

        <div
          className="flex-1 overflow-y-auto pt-16 pb-40 custom-scrollbar"
          ref={scrollContainerRef}
          onScroll={handleScroll}
        >
          {currentMessages.length === 0 && !streamingMessage && !isSessionLoading ? (
            <ChatEmptyState onSelectSuggestion={prompt => setInput(prompt)} />
          ) : (
            <div className="pb-8">
              {isSessionLoading ? (
                <SessionSkeletonLoader />
              ) : (
                <>
                  {currentMessages.map((msg, index) => {
                    const previousUser = msg.role === 'assistant'
                      ? [...currentMessages.slice(0, index)].reverse().find(item => item.role === 'user')
                      : undefined;
                    return (
                      <ChatMessage
                        key={msg.id}
                        message={msg}
                        onRefine={(prompt) => handleSubmit(undefined, prompt)}
                        onRetry={previousUser ? () => handleSubmit(undefined, previousUser.content) : undefined}
                        onOpenContext={setDrawerContext}
                        onFeedbackSubmit={handleFeedbackSubmit}
                        isSourcesPanelOpen={drawerContext === msg.contextUsed}
                      />
                    );
                  })}
                  {/* Streaming message realtime */}
                  {streamingMessage && (
                    <ChatMessage
                      key="streaming"
                      message={streamingMessage}
                      isStreaming={true}
                      onRefine={(prompt) => handleSubmit(undefined, prompt)}
                      onOpenContext={setDrawerContext}
                      isSourcesPanelOpen={drawerContext === streamingMessage.contextUsed}
                    />
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="absolute bottom-0 left-0 right-0 pt-10 pb-4 px-4 bg-gradient-to-t from-white via-white to-transparent dark:from-[#212121] dark:via-[#212121]">
          <div className={`${CHAT_ROW_WIDTH_CLASS} flex gap-4`}>
            <div className="h-8 w-8 shrink-0" aria-hidden="true" />
            <div className={`${CHAT_CONTENT_WIDTH_CLASS} relative`}>
            {/* Scroll to bottom button */}
            {!isAtBottom && currentMessages.length > 0 && (
              <div className="absolute -top-14 left-1/2 -translate-x-1/2 z-20 fade-in slide-in-from-bottom-2 duration-200">
                <button
                  onClick={scrollToBottom}
                  className="w-10 h-10 bg-white dark:bg-[#171717] rounded-full flex items-center justify-center shadow-[0_2px_10px_rgba(0,0,0,0.1)] dark:shadow-none border border-gray-100 dark:border-white/10 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-all hover:shadow-[0_4px_14px_rgba(0,0,0,0.12)] active:scale-95"
                  title="Cuộn xuống"
                >
                  <ArrowDown className="w-5 h-5" />
                </button>
              </div>
            )}

            <div className="relative rounded-3xl bg-white dark:bg-[#171717] border border-gray-200/80 dark:border-white/10 shadow-xl shadow-blue-100/30 dark:shadow-none input-glow transition-all duration-300">

              {/* File preview chips */}
              {attachments.length > 0 && (
                <div className="flex flex-wrap gap-2 px-4 pt-3 pb-1">
                  {attachments.map(att => (
                    <div
                      key={att.id}
                      className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-xl px-2.5 py-1.5 text-xs max-w-[200px] group"
                    >
                      {att.file.type.startsWith('image/') && att.previewUrl ? (
                        <img src={att.previewUrl} alt={att.file.name} className="w-8 h-8 object-cover rounded-lg flex-shrink-0" />
                      ) : (
                        <div className="w-8 h-8 bg-orange-100 dark:bg-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileText className="w-4 h-4 text-orange-500" />
                        </div>
                      )}
                      <div className="min-w-0">
                        <p className="truncate font-medium text-gray-700 dark:text-gray-200" title={att.file.name}>{att.file.name}</p>
                        {att.status === 'uploading' && (
                          <p className="text-gray-400 flex items-center gap-1"><Loader2 className="w-2.5 h-2.5 animate-spin" />Đang tải...</p>
                        )}
                        {att.status === 'error' && <p className="text-red-400">Lỗi upload</p>}
                        {att.status === 'done' && att.hasText && <p className="text-green-500">Đã đọc nội dung</p>}
                        {att.status === 'done' && !att.hasText && att.file.type.startsWith('image/') && <p className="text-gray-400">Ảnh</p>}
                      </div>
                      <button
                        type="button"
                        onClick={() => removeAttachment(att.id)}
                        className="ml-auto flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex items-center gap-2 px-3 pt-3 pb-1">
                <div className="ml-auto flex min-w-0 flex-wrap items-center justify-end gap-2">
                  <AdvancedSettings config={advancedConfig} setConfig={setAdvancedConfig} />
                  <ProviderSelector model={model} setModel={setModel} />
                </div>
              </div>

              {/* File input ẩn */}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf,.txt,.doc,.docx"
                className="hidden"
                onChange={e => { if (e.target.files) { addFiles(e.target.files); e.target.value = ''; } }}
              />

              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInput}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                placeholder={isListening ? t('chat.listening', 'Đang nghe...') : isLoading ? t('chat.processing', 'Đang xử lý yêu cầu...') : chatMode === 'car' ? t('chat.placeholderCar', 'Hỏi về ô tô, giá xe, phân tích dữ liệu...') : t('chat.placeholder', 'Hỏi về xe, thông số kỹ thuật, hoặc tính năng...')}
                className="w-full resize-none bg-transparent pl-14 pr-24 py-3 focus:outline-none text-gray-700 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 leading-relaxed rounded-b-3xl text-[15px] custom-scrollbar"
                rows={1}
                style={{ minHeight: '52px', maxHeight: '160px' }}
              />

              {/* Nút upload file — bottom-left */}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
                title="Đính kèm file"
                className="absolute left-3 bottom-2.5 p-2 rounded-xl text-gray-400 hover:text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-500/10 transition-all disabled:opacity-40"
              >
                <Paperclip className="w-4 h-4" />
              </button>

              {/* Nut Send / Stop */}
              <div className="absolute right-2 bottom-2 flex items-center gap-1">
                {isSupported && !isLoading && (
                  <button
                    onClick={handleMicClick}
                    title={t('chat.micTooltip', 'Nhập bằng giọng nói')}
                    aria-label={t('chat.micTooltip', 'Nhập bằng giọng nói')}
                    className={`p-2.5 rounded-2xl transition-all flex items-center justify-center ${
                      isListening
                        ? 'text-red-500 bg-red-50 dark:bg-red-500/10 animate-pulse'
                        : 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    <Mic className="w-5 h-5" />
                  </button>
                )}
                
                {isLoading ? (
                  <button
                    onClick={handleAbort}
                    title={t('chat.stopTooltip', 'Dừng tạo câu trả lời (Enter)')}
                    aria-label={t('chat.stopTooltip', 'Dừng trả lời')}
                    className="p-2.5 text-white rounded-2xl transition-all shadow-md active:scale-95 flex items-center justify-center animate-pulse"
                    style={{ background: 'linear-gradient(135deg, #EF4444, #DC2626)' }}
                  >
                    <Square className="w-4 h-4 fill-white" />
                  </button>
                ) : (
                  <button
                    onClick={() => handleSubmit()}
                    disabled={!input.trim() && attachments.length === 0}
                    aria-label={t('chat.sendTooltip', 'Gửi câu hỏi')}
                    className={`p-2.5 text-white dark:text-gray-900 bg-gray-800 hover:bg-gray-900 dark:bg-gray-200 dark:hover:bg-white rounded-2xl disabled:opacity-40 transition-all shadow-md active:scale-95 flex items-center justify-center ${(input.trim() || attachments.length > 0) ? 'send-btn-ready' : ''}`}
                  >
                    <Send className="w-4 h-4 translate-x-px translate-y-px" />
                  </button>
                )}
              </div>
            </div>
            <p className="text-center mt-2.5 text-xs text-gray-500 font-medium tracking-wide">
              {t('chat.disclaimer', 'AI có thể cung cấp thông tin không chính xác. Hãy luôn kiểm tra lại dữ liệu quan trọng.')}
            </p>
            </div>
          </div>
        </div>
      </div>

      {!isInferenceConfigured(aiSettings) && (
        <InferenceSetupModal />
      )}

      {/* Context Drawer */}
      <div
        className={`absolute md:relative top-0 right-0 h-full bg-white dark:bg-[#171717] shadow-[0_0_40px_rgba(0,0,0,0.1)] dark:shadow-none transition-all duration-300 z-50 border-l border-gray-200/60 dark:border-white/10 flex-shrink-0 overflow-hidden
          ${drawerContext ? 'translate-x-0 md:w-[400px] w-full' : 'translate-x-full md:translate-x-0 md:w-0 w-full'}`}
        id="sources-panel"
      >
        {drawerContext && (
          <div className="flex flex-col h-full">
            <div className="h-14 flex items-center justify-between px-4 border-b border-gray-100 dark:border-white/10 bg-gray-50/50 dark:bg-[#171717]/50 flex-shrink-0 transition-colors">
              <span className="text-[11px] font-bold uppercase tracking-widest text-gray-700 dark:text-gray-400">
                {t('chat.sources', 'nguồn tham khảo')}
              </span>
              <button
                onClick={() => setDrawerContext(null)}
                className="p-1.5 rounded-lg text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-white/8 transition-colors"
                title="Đóng"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
              <div className="space-y-3">
                {drawerContext.length === 0 ? (
                  <p className="text-gray-500 dark:text-gray-400 text-[13px] text-center mt-10 italic">
                    {t('chat.noSources', 'Không có tài liệu trích dẫn cho đoạn chat này.')}
                  </p>
                ) : (
                  <SourceList sources={drawerContext} />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
