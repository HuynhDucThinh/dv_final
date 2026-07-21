'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Square, Loader2, BarChart3, ChevronDown, PanelLeft } from 'lucide-react';
import { CodeApprovalBlock, ExecutionResult } from './CodeApprovalBlock';

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface AnalysisMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  executionResults?: Record<string, ExecutionResult>;
}

const AVAILABLE_MODELS = [
  { id: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B (Groq ⚡)' },
  { id: 'gemma2-9b-it', label: 'Gemma 2 9B (Groq ⚡)' },
  { id: 'mixtral-8x7b-32768', label: 'Mixtral 8x7B (Groq ⚡)' },
  { id: 'gemini-2.0-flash-lite', label: 'Gemini 2.0 Flash-Lite' },
  { id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
  { id: 'gpt-4o-mini', label: 'GPT-4o Mini' },
];

const SESSION_ID = `analysis-${Date.now()}`;

/** Trích xuất các code block Python từ markdown */
function extractCodeBlocks(text: string): { code: string; index: number }[] {
  const regex = /```python\n([\s\S]*?)```/g;
  const blocks: { code: string; index: number }[] = [];
  let match;
  let index = 0;
  while ((match = regex.exec(text)) !== null) {
    blocks.push({ code: match[1].trim(), index: index++ });
  }
  return blocks;
}

/** Render nội dung tin nhắn — text thường + code blocks */
function MessageContent({
  message,
  onExecuted,
}: {
  message: AnalysisMessage;
  onExecuted: (messageId: string, blockIndex: number, result: ExecutionResult) => void;
}) {
  const content = message.content;
  const parts = content.split(/(```python[\s\S]*?```)/g);
  let blockIndex = 0;

  return (
    <div className="space-y-1">
      {parts.map((part, i) => {
        if (part.startsWith('```python')) {
          const code = part.replace(/^```python\n/, '').replace(/```$/, '').trim();
          const currentIndex = blockIndex++;
          return (
            <CodeApprovalBlock
              key={i}
              code={code}
              blockIndex={currentIndex}
              messageId={message.id}
              sessionId={SESSION_ID}
              onExecuted={(result) => onExecuted(message.id, currentIndex, result)}
            />
          );
        }
        if (part.trim()) {
          return (
            <div
              key={i}
              className="prose prose-invert prose-sm max-w-none text-gray-200 leading-relaxed"
              dangerouslySetInnerHTML={{
                __html: part
                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/\*(.*?)\*/g, '<em>$1</em>')
                  .replace(/`([^`]+)`/g, '<code class="bg-zinc-800 px-1 rounded text-emerald-300 text-xs">$1</code>')
                  .replace(/\n/g, '<br/>'),
              }}
            />
          );
        }
        return null;
      })}
    </div>
  );
}

export function AIAnalysisPage() {
  const [messages, setMessages] = useState<AnalysisMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[0].id);
  const [showModelPicker, setShowModelPicker] = useState(false);

  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText]);

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`;
  }, [input]);

  const handleExecuted = useCallback(
    (messageId: string, blockIndex: number, result: ExecutionResult) => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId
            ? {
                ...m,
                executionResults: {
                  ...m.executionResults,
                  [blockIndex]: result,
                },
              }
            : m
        )
      );
    },
    []
  );

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMsg: AnalysisMessage = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    setStreamingText('');

    const abort = new AbortController();
    abortRef.current = abort;

    const assistantId = `a-${Date.now()}`;

    try {
      const allMessages = [
        ...messages.map((m) => ({ role: m.role, content: m.content })),
        { role: 'user', content: text },
      ];

      const res = await fetch(`${API_BASE}/api/analysis/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: allMessages,
          model: selectedModel,
          session_id: SESSION_ID,
          streaming: true,
        }),
        signal: abort.signal,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader = res.body?.getReader();
      if (!reader) throw new Error('No body');

      const decoder = new TextDecoder();
      let full = '';
      let buf = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() || '';
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'token') {
              full += data.content;
              setStreamingText(full);
            } else if (data.type === 'done') {
              full = data.content || full;
            } else if (data.type === 'error') {
              full = `⚠️ Lỗi: ${data.content}`;
              setStreamingText(full);
            }
          } catch {
            /* skip */
          }
        }
      }

      const assistantMsg: AnalysisMessage = {
        id: assistantId,
        role: 'assistant',
        content: full,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Lưu log
      try {
        await fetch(`${API_BASE}/api/analysis/log`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: SESSION_ID,
            user_request: text,
            ai_response: full,
          }),
        });
      } catch {
        /* log failure non-blocking */
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        const errMsg: AnalysisMessage = {
          id: assistantId,
          role: 'assistant',
          content: `⚠️ Lỗi: ${(err as Error).message}`,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, errMsg]);
      }
    } finally {
      setIsLoading(false);
      setStreamingText('');
      abortRef.current = null;
    }
  }, [input, isLoading, messages, selectedModel]);

  const handleStop = () => {
    abortRef.current?.abort();
    setIsLoading(false);
    setStreamingText('');
  };

  const SUGGESTIONS = [
    'Phân tích phân phối giá xe theo hãng',
    'Vẽ biểu đồ hộp (boxplot) so sánh giá xe theo nhiên liệu',
    'Thống kê số lượng xe theo năm sản xuất',
    'Tìm các mẫu xe có giá cao nhất và thấp nhất',
    'Phân tích tương quan giữa năm sản xuất và giá xe',
  ];

  const selectedModelLabel = AVAILABLE_MODELS.find((m) => m.id === selectedModel)?.label || selectedModel;

  return (
    <div className="flex flex-col h-full bg-[#0f0f0f] text-white">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-zinc-800 bg-[#111] flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
            <BarChart3 className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Phân tích Dữ liệu AI</h2>
            <p className="text-[10px] text-zinc-500 uppercase tracking-wider">Car Data Assistant</p>
          </div>
        </div>

        {/* Model picker */}
        <div className="relative">
          <button
            onClick={() => setShowModelPicker((v) => !v)}
            className="flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg bg-zinc-800 border border-zinc-700
                       hover:bg-zinc-700 transition-colors text-zinc-300"
          >
            <span className="max-w-[140px] truncate">{selectedModelLabel}</span>
            <ChevronDown className="w-3 h-3 flex-shrink-0" />
          </button>
          {showModelPicker && (
            <div className="absolute right-0 top-full mt-1 z-50 bg-zinc-900 border border-zinc-700
                            rounded-xl shadow-xl overflow-hidden min-w-[200px]">
              {AVAILABLE_MODELS.map((m) => (
                <button
                  key={m.id}
                  onClick={() => { setSelectedModel(m.id); setShowModelPicker(false); }}
                  className={`w-full text-left px-4 py-2.5 text-xs transition-colors ${
                    m.id === selectedModel
                      ? 'bg-blue-600/20 text-blue-300'
                      : 'text-zinc-300 hover:bg-zinc-800'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && !streamingText && (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-xl">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-white mb-1">Trợ lý Phân tích Dữ liệu</h3>
              <p className="text-sm text-zinc-500 mb-6 max-w-sm mx-auto">
                Hỏi về dữ liệu ô tô Việt Nam — AI sẽ viết code Python, bạn xem xét và phê duyệt trước khi chạy.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg mx-auto text-left">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => { setInput(s); textareaRef.current?.focus(); }}
                    className="px-3 py-2.5 text-xs text-zinc-300 bg-zinc-800/80 border border-zinc-700
                               rounded-xl hover:bg-zinc-700 hover:border-zinc-600 transition-all text-left"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-1' : ''}`}>
                {msg.role === 'user' ? (
                  <div className="bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm">
                    {msg.content}
                  </div>
                ) : (
                  <div className="bg-zinc-800/60 border border-zinc-700/50 rounded-2xl rounded-tl-sm px-4 py-3">
                    <MessageContent message={msg} onExecuted={handleExecuted} />
                  </div>
                )}
              </div>
            </div>
          ))}

          {streamingText && (
            <div className="flex justify-start">
              <div className="max-w-[85%] bg-zinc-800/60 border border-zinc-700/50 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">
                  {streamingText}
                  <span className="inline-block w-1.5 h-4 bg-blue-400 ml-0.5 animate-pulse rounded-sm" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} className="h-2" />
        </div>
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-zinc-800 bg-[#111] px-4 py-3">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-2 bg-zinc-900 border border-zinc-700 rounded-2xl px-4 py-3
                          focus-within:border-blue-500/60 transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
              }}
              placeholder="Hỏi về dữ liệu ô tô hoặc yêu cầu phân tích..."
              rows={1}
              disabled={isLoading}
              className="flex-1 bg-transparent text-sm text-white placeholder:text-zinc-500
                         resize-none outline-none max-h-[180px]"
            />
            {isLoading ? (
              <button
                onClick={handleStop}
                className="p-2 rounded-xl bg-red-600 hover:bg-red-500 text-white transition-colors flex-shrink-0"
              >
                <Square className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="p-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition-colors
                           disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            )}
          </div>
          <p className="text-[10px] text-zinc-600 text-center mt-1.5">
            Code AI tạo ra sẽ ở trạng thái "Chờ duyệt" — chỉ thực thi khi bạn bấm "Phê duyệt &amp; Thực thi"
          </p>
        </div>
      </div>
    </div>
  );
}
