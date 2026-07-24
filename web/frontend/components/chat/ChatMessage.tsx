'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Car, BookOpen, Copy, Check, ThumbsUp, ThumbsDown, RotateCcw, Undo2, FileText, File, Image as ImageIcon, Loader2, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { Message, DocumentChunk, MessageAttachment } from '@/lib/types';
import { ChatProcessingTrace } from './ChatProcessingTrace';
import { dedupeSources, SourcesTrigger } from './Sources';
import { CHAT_CONTENT_WIDTH_CLASS, CHAT_ROW_WIDTH_CLASS } from './layout';
import { InteractiveCodeBlock } from './InteractiveCodeBlock';

export type { Message, DocumentChunk } from '@/lib/types';

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
  onRefine?: (prompt: string) => void;
  onOpenContext?: (context: DocumentChunk[]) => void;
  onFeedbackSubmit?: (messageId: string, type: 1 | -1, reason?: string, comment?: string) => void;
  onRetry?: () => void;
  isSourcesPanelOpen?: boolean;
  sessionId?: string; // Truyền xuống InteractiveCodeBlock
  onSendExecutionResult?: (code: string, output: string) => void; // Callback gửi kết quả cho AI
}

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

function FileActionApprovalCard({ actionId }: { actionId: string }) {
  const [status, setStatus] = useState<'idle' | 'loading' | 'approved' | 'rejected' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleApprove = async () => {
    setStatus('loading');
    try {
      const approveRes = await fetch(`${API_BASE}/api/file-operations/${actionId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!approveRes.ok) {
        let errDetail = `Lỗi ${approveRes.status}`;
        try {
          const err = await approveRes.json();
          errDetail = err.detail || errDetail;
        } catch {
          // ignore
        }
        throw new Error(errDetail);
      }

      const executeRes = await fetch(`${API_BASE}/api/file-operations/${actionId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!executeRes.ok) {
        let errDetail = `Lỗi ${executeRes.status}`;
        try {
          const err = await executeRes.json();
          errDetail = err.detail || errDetail;
        } catch {
          // ignore
        }
        throw new Error(errDetail);
      }

      setStatus('approved');
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(err.message || 'Lỗi khi thực thi thao tác file');
    }
  };

  const handleReject = async () => {
    setStatus('loading');
    try {
      const res = await fetch(`${API_BASE}/api/file-operations/${actionId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, decision: 'reject', reason: 'Người dùng từ chối' }),
      });
      if (!res.ok) {
        let errDetail = `Lỗi ${res.status}`;
        try {
          const err = await res.json();
          errDetail = err.detail || errDetail;
        } catch {
          // ignore
        }
        throw new Error(errDetail);
      }
      setStatus('rejected');
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(err.message || 'Lỗi khi từ chối thao tác');
    }
  };

  if (status === 'approved') {
    return (
      <div className="mt-3.5 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold flex items-center gap-2">
        <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
        <span>Thao tác file đã được phê duyệt và ghi thành công xuống ổ đĩa.</span>
      </div>
    );
  }

  if (status === 'rejected') {
    return (
      <div className="mt-3.5 p-3.5 rounded-xl bg-gray-500/10 border border-gray-500/30 text-gray-600 dark:text-gray-400 text-xs font-semibold flex items-center gap-2">
        <X className="w-4 h-4 text-gray-500 flex-shrink-0" />
        <span>Thao tác file đã bị từ chối.</span>
      </div>
    );
  }

  return (
    <div className="mt-3.5 p-4 rounded-xl bg-gray-50 dark:bg-[#1E1E1E] border border-amber-500/40 shadow-sm space-y-3 text-xs">
      <div className="flex items-center justify-between font-semibold text-amber-600 dark:text-amber-400">
        <span className="text-xs uppercase tracking-wider font-bold">Yêu cầu phê duyệt thao tác file</span>
        <span className="font-mono text-[11px] bg-amber-500/15 text-amber-700 dark:text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">
          ID: {actionId.slice(0, 8)}...
        </span>
      </div>

      <p className="text-gray-600 dark:text-gray-300 text-[12px] leading-relaxed">
        AI vừa tạo một yêu cầu quản lý file trong dự án. Vui lòng <strong>phê duyệt</strong> để thực hiện ghi đè lên đĩa hoặc <strong>từ chối</strong> để hủy.
      </p>

      {status === 'error' && (
        <div className="text-rose-500 text-xs font-medium">
          Lỗi: {errorMessage}
        </div>
      )}

      <div className="flex items-center gap-2.5 pt-1">
        <button
          onClick={handleApprove}
          disabled={status === 'loading'}
          className="flex-1 py-2 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs flex items-center justify-center gap-1.5 transition-all shadow-sm"
        >
          {status === 'loading' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Check className="w-3.5 h-3.5" />
          )}
          <span>Phê duyệt (Approve)</span>
        </button>

        <button
          onClick={handleReject}
          disabled={status === 'loading'}
          className="py-2 px-4 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 disabled:opacity-50 text-gray-700 dark:text-gray-300 font-medium text-xs flex items-center justify-center gap-1.5 transition-colors border border-gray-300 dark:border-gray-700"
        >
          <X className="w-3.5 h-3.5" />
          <span>Từ chối</span>
        </button>
      </div>
    </div>
  );
}

export function ChatMessage({ message, isStreaming = false, onRefine, onOpenContext, onFeedbackSubmit, onRetry, isSourcesPanelOpen = false, sessionId, onSendExecutionResult }: ChatMessageProps) {
  const { t } = useTranslation();
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(
    message.feedback === 1 ? 'up' : message.feedback === -1 ? 'down' : null
  );
  const [showNegativeForm, setShowNegativeForm] = useState(false);
  const [reason, setReason] = useState('Sai thông tin');
  const [comment, setComment] = useState('');
  const [selectedCitation, setSelectedCitation] = useState<DocumentChunk | null>(null);
  const [isProcessCollapsed, setIsProcessCollapsed] = useState(true);

  React.useEffect(() => {
    setFeedback(message.feedback === 1 ? 'up' : message.feedback === -1 ? 'down' : null);
  }, [message.feedback]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFeedbackClick = (type: 'up' | 'down') => {
    if (type === 'up') {
      setFeedback(feedback === 'up' ? null : 'up');
      setShowNegativeForm(false);
      if (feedback !== 'up' && onFeedbackSubmit) {
        onFeedbackSubmit(message.id, 1);
      }
    } else {
      if (feedback === 'down') {
        setFeedback(null);
        setShowNegativeForm(false);
      } else {
        setFeedback('down');
        setShowNegativeForm(true);
      }
    }
  };

  const submitNegativeFeedback = () => {
    if (onFeedbackSubmit) {
      onFeedbackSubmit(message.id, -1, reason, comment);
    }
    setShowNegativeForm(false);
  };

  // Dùng displayContent để hiển thị trong UI (ẩn extracted text), content gửi cho LLM
  const rawDisplayText = (message.displayContent ?? message.content) || '';

  // Trích xuất <suggestions>...</suggestions> tag từ response của AI
  const suggestionsMatch = !isUser ? rawDisplayText.match(/<suggestions>([ -\uFFFF]*?)<\/suggestions>/) : null;
  const suggestedQuestions: string[] = suggestionsMatch
    ? suggestionsMatch[1].split('|').map(s => s.trim()).filter(Boolean)
    : [];
  const displayText = rawDisplayText.replace(/<suggestions>[ -\uFFFF]*?<\/suggestions>/g, '').trim() || rawDisplayText;

  // Parse <cite id="...">...</cite> into markdown link format (chỉ áp dụng cho assistant)
  const processedContent = isUser
    ? displayText
    : (displayText.replace(
        /<cite\s+id=["']([^"']+)["']>([^<]+)<\/cite>/gi,
        '[$2](#cite-$1)'
      ) || '');

  // Extract Action ID (VD: Action ID: `6426c588-a4ed-4da9-882a-d9c8e188d99b`)
  const actionIdMatch = !isUser ? processedContent.match(/Action ID[:\s*`*]+([a-f0-9-]{12,})/i) : null;
  const actionId = actionIdMatch ? actionIdMatch[1] : null;

  return (
    <div id={`message-${message.id}`} className={`group py-5 px-4 message-animate ${showNegativeForm ? 'relative z-[150]' : ''}`}>
      <div className={`${CHAT_ROW_WIDTH_CLASS} flex ${isUser ? 'flex-row-reverse gap-2.5' : 'flex-row gap-4'}`}>

        {/* Avatar */}
        <div className="flex-shrink-0 mt-1">
          {isUser ? (
            <div className="w-8 h-8 rounded-full flex items-center justify-center border border-gray-200 dark:border-white/10 bg-gray-100 dark:bg-[#171717] shadow-sm">
              <User className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </div>
          ) : (
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center border border-gray-200 dark:border-white/10 bg-gray-100 dark:bg-[#171717] shadow-sm"
            >
              <Car className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </div>
          )}
        </div>

        {/* Content */}
        <div className={`flex-1 min-w-0 flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          {/* Bubble */}
          <div
            className={`${
              isUser
                ? 'inline-block max-w-[92%] sm:max-w-[88%] rounded-2xl rounded-tr-sm text-gray-800 dark:text-gray-200'
                : `${CHAT_CONTENT_WIDTH_CLASS} text-gray-800 dark:text-gray-200`
            }`}
          >
            {/* File attachment cards — chỉ hiển thị với user message */}
            {isUser && message.attachments && message.attachments.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2 justify-end">
                {message.attachments.map(att => (
                  <AttachmentCard key={att.id} attachment={att} />
                ))}
              </div>
            )}

            {!isUser && message.processingStage && (
              <ChatProcessingTrace
                stage={message.processingStage}
                collapsed={isProcessCollapsed}
                onToggleCollapsed={() => setIsProcessCollapsed(current => !current)}
              />
            )}

            {/* Message bubble */}
            {processedContent && (
            <div className={`${
              isUser
                ? 'px-5 py-3.5 bg-gray-100 dark:bg-[#2F2F2F]'
                : ''
            } rounded-2xl ${isUser ? 'rounded-tr-sm' : 'mt-2'}`}>
              <div className={`prose dark:prose-invert max-w-full text-[15px] leading-[1.75]
                prose-p:my-3 prose-p:leading-[1.75]
                prose-ul:my-3 prose-ol:my-3 prose-li:my-1.5 prose-li:leading-[1.75]
                prose-headings:font-bold prose-headings:tracking-tight
                prose-h1:text-[1.35rem] prose-h1:mt-6 prose-h1:mb-3
                prose-h2:text-[1.15rem] prose-h2:mt-5 prose-h2:mb-2.5
                prose-h3:text-[1rem] prose-h3:mt-4 prose-h3:mb-2
                prose-strong:font-semibold
                prose-code:rounded-md prose-code:bg-gray-100 prose-code:dark:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:text-[13px] prose-code:font-mono prose-code:text-rose-600 prose-code:dark:text-rose-400 prose-code:before:content-none prose-code:after:content-none
                prose-pre:p-0 prose-pre:bg-transparent prose-pre:rounded-none
                prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:bg-blue-50 prose-blockquote:dark:bg-blue-950/20 prose-blockquote:pl-4 prose-blockquote:py-1 prose-blockquote:rounded-r-lg prose-blockquote:not-italic prose-blockquote:text-gray-700 prose-blockquote:dark:text-gray-300
                prose-table:w-full prose-th:bg-gray-100 prose-th:dark:bg-gray-800 prose-th:text-gray-700 prose-th:dark:text-gray-200 prose-th:font-semibold prose-th:text-sm prose-td:text-sm
                prose-hr:border-gray-200 prose-hr:dark:border-gray-700
                ${isStreaming ? 'typing-cursor' : ''} ${
                isUser
                  ? 'prose-p:text-gray-800 dark:prose-p:text-gray-200 prose-strong:text-gray-900 dark:prose-strong:text-white prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-headings:text-gray-900 dark:prose-headings:text-white prose-li:text-gray-800 dark:prose-li:text-gray-200'
                  : 'prose-p:text-gray-800 dark:prose-p:text-gray-200 prose-headings:text-gray-900 dark:prose-headings:text-gray-50 prose-strong:text-gray-900 dark:prose-strong:text-gray-100 prose-li:text-gray-800 dark:prose-li:text-gray-200 prose-a:text-blue-600 dark:prose-a:text-blue-400'
              }`}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  urlTransform={(url) => url}
                  components={{
                    // --- Images (Allow Base64 PNGs) ---
                    img({ src, alt }: any) {
                      if (!src) return null;
                      return (
                        <span className="block my-4 overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700/80 shadow-md bg-white dark:bg-[#1E1E1E] p-2">
                          <img
                            src={src}
                            alt={alt || 'Biểu đồ'}
                            className="w-full max-h-[500px] object-contain rounded-lg"
                          />
                        </span>
                      );
                    },
                    // --- Headings ---
                    h1({ children }: any) {
                      return (
                        <h1 className="not-prose text-[1.25rem] font-extrabold text-gray-900 dark:text-gray-50 mt-6 mb-3 pb-2.5 border-b-2 border-indigo-400 dark:border-indigo-500 uppercase tracking-wide">
                          {children}
                        </h1>
                      );
                    },
                    h2({ children }: any) {
                      return (
                        <h2 className="not-prose text-[1rem] font-extrabold text-gray-900 dark:text-gray-100 mt-5 mb-2.5 pb-1.5 border-b border-gray-300 dark:border-gray-700 uppercase tracking-widest">
                          {children}
                        </h2>
                      );
                    },
                    h3({ children }: any) {
                      return (
                        <h3 className="not-prose text-[0.92rem] font-bold text-gray-800 dark:text-gray-200 mt-4 mb-1.5 uppercase tracking-wide">
                          {children}
                        </h3>
                      );
                    },
                    // --- Strong / Bold ---
                    strong({ children }: any) {
                      return (
                        <strong className="font-bold text-gray-900 dark:text-gray-100">
                          {children}
                        </strong>
                      );
                    },
                    // --- Lists ---
                    ul({ children }: any) {
                      return (
                        <ul className="not-prose my-3 space-y-1.5 pl-1 chat-ul">{children}</ul>
                      );
                    },
                    ol({ children }: any) {
                      return (
                        <ol className="not-prose my-3 space-y-1.5 pl-1 chat-ol">{children}</ol>
                      );
                    },
                    li({ children, ordered }: any) {
                      if (ordered) {
                        return (
                          <li className="flex items-start gap-2.5 leading-[1.75] text-[15px] text-gray-800 dark:text-gray-200 chat-ol-li">
                            <span className="chat-ol-num flex-shrink-0 min-w-[1.4rem] text-right font-semibold text-gray-500 dark:text-gray-400 text-[14px] mt-0.5" aria-hidden="true" />
                            <span className="flex-1 min-w-0">{children}</span>
                          </li>
                        );
                      }
                      return (
                        <li className="flex items-start gap-2.5 leading-[1.75] text-[15px] text-gray-800 dark:text-gray-200">
                          <span className="flex-shrink-0 mt-[0.6rem] w-[5px] h-[5px] rounded-full bg-gray-500 dark:bg-gray-400" aria-hidden="true" />
                          <span className="flex-1 min-w-0">{children}</span>
                        </li>
                      );
                    },
                    // --- Links ---
                    a: ({ node, ...props }) => {
                      const href = props.href || '';
                      if (href.startsWith('#cite-')) {
                        const citeId = href.replace('#cite-', '');
                        return (
                          <a
                            {...props}
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              const citedContext = message.contextUsed?.find(c => c.metadata?.id === citeId);
                              if (citedContext) setSelectedCitation(citedContext);
                            }}
                            className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium underline decoration-blue-400/60 dark:decoration-blue-500/50 decoration-dashed underline-offset-4 cursor-pointer transition-colors"
                          >
                            {props.children}
                          </a>
                        );
                      }
                      return (
                        <a
                          {...props}
                          className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline underline-offset-2 decoration-blue-400/50 transition-colors font-medium"
                          target="_blank"
                          rel="noopener noreferrer"
                        />
                      );
                    },
                    // --- Code ---
                    code({ node, inline, className, children, ...props }: any) {
                      const match = /language-(\w+)/.exec(className || '');
                      if (!inline && match) {
                        const rawCode = String(children).replace(/\n$/, '');
                        const effectiveSessionId = sessionId || message.id;
                        return (
                          <InteractiveCodeBlock
                            key={`code-${message.id}-${rawCode.slice(0, 30)}`}
                            initialCode={rawCode}
                            language={match[1]}
                            sessionId={effectiveSessionId}
                            onSendResult={onSendExecutionResult}
                          />
                        );
                      }
                      return (
                        <code className={`not-prose px-1.5 py-0.5 rounded-md text-[13px] font-mono bg-gray-100 dark:bg-gray-800 text-rose-600 dark:text-rose-400 ${className ?? ''}`} {...props}>
                          {children}
                        </code>
                      );
                    },
                    // --- Table ---
                    table({ children }: any) {
                      return (
                        <div className="not-prose overflow-x-auto my-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
                          <table className="min-w-full text-sm border-collapse">{children}</table>
                        </div>
                      );
                    },
                    thead({ children }: any) {
                      return <thead className="bg-gray-100 dark:bg-gray-800">{children}</thead>;
                    },
                    tbody({ children }: any) {
                      return <tbody className="divide-y divide-gray-100 dark:divide-gray-800">{children}</tbody>;
                    },
                    tr({ children }: any) {
                      return <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/40 transition-colors">{children}</tr>;
                    },
                    th({ children }: any) {
                      return (
                        <th className="px-4 py-3 text-left font-bold text-gray-700 dark:text-gray-200 text-[12px] uppercase tracking-widest whitespace-nowrap border-b-2 border-gray-200 dark:border-gray-700">
                          {children}
                        </th>
                      );
                    },
                    td({ children }: any) {
                      return (
                        <td className="px-4 py-2.5 text-gray-700 dark:text-gray-300 text-[14px] align-top">
                          {children}
                        </td>
                      );
                    },
                     // --- Blockquote (GitHub-style alerts) ---
                     blockquote({ children, node }: any) {
                       // Lấy raw text từ AST để detect alert type
                       const getNodeText = (n: any): string => {
                         if (!n) return '';
                         if (n.type === 'text') return n.value || '';
                         if (Array.isArray(n.children)) return n.children.map(getNodeText).join('');
                         return '';
                       };
                       const rawText = node ? getNodeText(node).trim() : '';

                       if (/^\[!IMPORTANT\]/i.test(rawText)) return (
                         <div className="not-prose my-3.5 border-l-4 border-red-500 bg-red-50 dark:bg-red-950/20 pl-4 pr-3 py-3 rounded-r-lg">
                           <span className="text-red-600 dark:text-red-400 font-bold text-[11px] uppercase tracking-widest flex items-center gap-1 mb-1.5">&#10071; Quan trọng</span>
                           <div className="text-gray-800 dark:text-gray-200 text-[14px] leading-relaxed [&>p]:my-1">{children}</div>
                         </div>
                       );
                       if (/^\[!WARNING\]/i.test(rawText)) return (
                         <div className="not-prose my-3.5 border-l-4 border-amber-500 bg-amber-50 dark:bg-amber-950/20 pl-4 pr-3 py-3 rounded-r-lg">
                           <span className="text-amber-600 dark:text-amber-400 font-bold text-[11px] uppercase tracking-widest flex items-center gap-1 mb-1.5">⚠️ Cảnh báo</span>
                           <div className="text-gray-800 dark:text-gray-200 text-[14px] leading-relaxed [&>p]:my-1">{children}</div>
                         </div>
                       );
                       if (/^\[!TIP\]/i.test(rawText)) return (
                         <div className="not-prose my-3.5 border-l-4 border-emerald-500 bg-emerald-50 dark:bg-emerald-950/20 pl-4 pr-3 py-3 rounded-r-lg">
                           <span className="text-emerald-600 dark:text-emerald-400 font-bold text-[11px] uppercase tracking-widest flex items-center gap-1 mb-1.5">✅ Gợi ý</span>
                           <div className="text-gray-800 dark:text-gray-200 text-[14px] leading-relaxed [&>p]:my-1">{children}</div>
                         </div>
                       );
                       if (/^\[!NOTE\]/i.test(rawText)) return (
                         <div className="not-prose my-3.5 border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/20 pl-4 pr-3 py-3 rounded-r-lg">
                           <span className="text-blue-600 dark:text-blue-400 font-bold text-[11px] uppercase tracking-widest flex items-center gap-1 mb-1.5">📋 Ghi chú</span>
                           <div className="text-gray-800 dark:text-gray-200 text-[14px] leading-relaxed [&>p]:my-1">{children}</div>
                         </div>
                       );
                       // Default blockquote
                       return (
                         <blockquote className="not-prose border-l-[3px] border-blue-400 dark:border-blue-500 bg-blue-50/60 dark:bg-blue-950/25 pl-4 pr-3 py-2.5 my-3.5 rounded-r-lg text-gray-700 dark:text-gray-300 text-[14.5px] leading-relaxed">
                           {children}
                         </blockquote>
                       );
                     },
                     // --- HR ---
                     hr() {
                       return (
                         <div className="my-5 flex items-center gap-3">
                           <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent" />
                           <span className="text-[10px] text-gray-400 dark:text-gray-500 font-medium tracking-widest uppercase">&#9670;</span>
                           <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent" />
                         </div>
                       );
                     },
                    // --- Paragraph ---
                    p({ children }: any) {
                      return <p className="my-3 leading-[1.8] text-[15px] text-gray-800 dark:text-gray-200">{children}</p>;
                    },
                  }}
                >
                  {processedContent}
                </ReactMarkdown>
              </div>
            </div>
            )}

            {/* Thẻ Phê duyệt Thao tác File (Không dùng Emoji) */}
            {actionId && !isUser && (
              <FileActionApprovalCard actionId={actionId} />
            )}

            {/* Gợi ý câu hỏi tiếp theo — chỉ hiện sau khi streaming xong và có suggestions */}
            {!isUser && !isStreaming && suggestedQuestions.length > 0 && onRefine && (
              <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800/60">
                <p className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-2">
                  💡 Câu hỏi gợi ý
                </p>
                <div className="flex flex-wrap gap-2">
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => onRefine(q)}
                      className="text-[12px] px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-500/30 hover:bg-blue-100 dark:hover:bg-blue-500/20 transition-all hover:shadow-sm text-left"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* --- USER ONLY UI --- */}
          {isUser && (
            <div className="flex items-center justify-end gap-1.5 mt-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 w-full max-w-[88%] pr-1">
              <span className="text-[10px] text-gray-400 dark:text-gray-500 font-medium mr-1 tracking-wide">
                {!isNaN(Number(message.id)) ? new Date(Number(message.id)).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : ''}
              </span>
              <button
                onClick={handleCopy}
                title={copied ? t('chat.copiedAction', 'Đã chép') : t('chat.copyAction', 'Sao chép')}
                className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              {onRefine && (
                <button
                  onClick={() => onRefine(message.content)}
                  title="Gửi lại"
                  className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
                >
                  <Undo2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}

          {/* --- ASSISTANT ONLY UI --- */}
          {!isUser && (
            <>
              {/* Quick action row */}
              <div className="mt-2 flex flex-wrap items-center gap-1">
                <span className="text-[10px] text-gray-400 dark:text-gray-500 font-medium mr-2 tracking-wide">
                  {!isNaN(Number(message.id)) ? new Date(Number(message.id)).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : ''}
                </span>
                <button
                  onClick={handleCopy}
                  title={copied ? t('chat.copiedAction', 'Đã chép') : t('chat.copyAction', 'Sao chép')}
                  className="quick-action-btn flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-medium text-gray-500 dark:text-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                >
                  {copied
                    ? <Check className="w-3.5 h-3.5 text-emerald-500" />
                    : <Copy className="w-3.5 h-3.5" />
                  }
                  <span>{copied ? t('chat.copiedAction', 'Đã chép') : t('chat.copyAction', 'Sao chép')}</span>
                </button>

                {onRefine && (
                  <button
                    onClick={() => onRefine('Giải thích đơn giản hơn với ví dụ thực tế')}
                    title={t('chat.explainAction', 'Giải thích lại')}
                    className="quick-action-btn flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-medium text-gray-500 dark:text-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>{t('chat.explainAction', 'Giải thích lại')}</span>
                  </button>
                )}

                {onRetry && (message.processingStage === 'error' || message.processingStage === 'cancelled') && (
                  <button
                    onClick={onRetry}
                    title={t('chat.retryAction', 'Thử lại')}
                    className="quick-action-btn flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-medium text-gray-500 dark:text-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                  >
                    <Undo2 className="w-3.5 h-3.5" />
                    <span>{t('chat.retryAction', 'Thử lại')}</span>
                  </button>
                )}

                <div className="w-px h-3.5 bg-gray-200 mx-1" />

                <button
                  onClick={() => handleFeedbackClick('up')}
                  title="Câu trả lời hữu ích"
                  className={`quick-action-btn p-1.5 rounded-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 ${feedback === 'up' ? 'text-emerald-500' : 'text-gray-400'}`}
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <div className="relative">
                  <button
                    onClick={() => handleFeedbackClick('down')}
                    title="Câu trả lời chưa tốt"
                    className={`quick-action-btn p-1.5 rounded-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 ${feedback === 'down' ? 'text-red-400' : 'text-gray-400'}`}
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                  </button>

                  {/* Negative Feedback Form */}
                  {showNegativeForm && (
                    <div className="absolute top-full mt-2 left-0 w-64 bg-white dark:bg-[#171717] border border-gray-200 dark:border-white/10 rounded-xl shadow-2xl z-[150] p-3">
                      <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">{t('chat.feedbackTitle', 'Vấn đề bạn gặp phải?')}</h4>
                      <select
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        className="w-full bg-gray-50 dark:bg-[#171717] border border-gray-200 dark:border-white/10 rounded-lg text-xs p-2 mb-2 text-gray-700 dark:text-gray-300 outline-none focus:border-gray-400 dark:focus:border-gray-500 transition-colors"
                      >
                        <option value="Sai thông số kỹ thuật">{t('chat.feedbackReason1', 'Sai thông số kỹ thuật')}</option>
                        <option value="Dữ liệu cũ/Không chính xác">{t('chat.feedbackReason2', 'Dữ liệu cũ/Không chính xác')}</option>
                        <option value="Không liên quan">{t('chat.feedbackReason3', 'Không liên quan')}</option>
                        <option value="Khác">{t('chat.feedbackReason4', 'Khác')}</option>
                      </select>
                      <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder={t('chat.feedbackPlaceholder', 'Góp ý thêm (không bắt buộc)...')}
                        className="w-full bg-gray-50 dark:bg-[#171717] border border-gray-200 dark:border-white/10 rounded-lg text-xs p-2 mb-2 min-h-[60px] text-gray-700 dark:text-gray-300 outline-none focus:border-gray-400 dark:focus:border-gray-500 resize-none custom-scrollbar transition-colors"
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => setShowNegativeForm(false)}
                          className="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                        >
                          {t('chat.feedbackCancel', 'Hủy')}
                        </button>
                        <button
                          onClick={submitNegativeFeedback}
                          className="px-3 py-1.5 text-xs bg-gray-800 hover:bg-gray-900 dark:bg-gray-200 dark:hover:bg-white text-white dark:text-gray-900 rounded-lg font-medium transition-colors"
                        >
                          {t('chat.feedbackSubmit', 'Gửi')}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className={CHAT_CONTENT_WIDTH_CLASS}>
                <SourcesTrigger
                  sources={message.contextUsed}
                  onOpenAll={onOpenContext}
                  controlsId="sources-panel"
                  expanded={isSourcesPanelOpen && dedupeSources(message.contextUsed || []).length > 0}
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Citation Modal */}
      {selectedCitation && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-gray-900/40 backdrop-blur-sm transition-opacity"
          onClick={() => setSelectedCitation(null)}
        >
          <div
            className="bg-white dark:bg-[#171717] rounded-xl shadow-2xl w-[90%] max-w-2xl overflow-hidden transform transition-all scale-100 border dark:border-white/10"
            onClick={e => e.stopPropagation()}
          >
            <div className="px-6 py-4 border-b border-gray-100 dark:border-white/10 flex justify-between items-center bg-gray-50/80 dark:bg-[#171717]/60">
              <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                Nguồn tham khảo
              </h3>
              <button
                onClick={() => setSelectedCitation(null)}
                className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-1 rounded-full hover:bg-gray-200 dark:hover:bg-[#3a3a3a]"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>

            <div className="p-6 max-h-[60vh] overflow-y-auto custom-scrollbar">
              <div className="mb-4">
                <div className="inline-block px-3 py-1 bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-500/20 rounded-full text-xs font-semibold mb-3">
                  {selectedCitation.metadata?.source || 'Tài liệu tham khảo'}
                </div>
                {(selectedCitation.metadata?.dieu || selectedCitation.metadata?.khoan) && (
                  <h4 className="text-md font-semibold text-gray-800 dark:text-gray-100 mb-2">
                    {selectedCitation.metadata?.dieu ? `Điều ${selectedCitation.metadata.dieu}` : ''}
                    {selectedCitation.metadata?.dieu && selectedCitation.metadata?.khoan ? ' - ' : ''}
                    {selectedCitation.metadata?.khoan ? `Khoản ${selectedCitation.metadata.khoan}` : ''}
                  </h4>
                )}
              </div>

              <div className="text-gray-600 dark:text-gray-300 leading-relaxed text-sm whitespace-pre-wrap bg-gray-50/50 dark:bg-[#171717]/60 p-4 rounded-lg border border-gray-100 dark:border-white/10">
                {selectedCitation.content}
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-100 dark:border-white/10 bg-gray-50 dark:bg-[#171717]/60 flex justify-end">
              <button
                onClick={() => setSelectedCitation(null)}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
// --- AttachmentCard: hiển file card trong chat (không show nội dung) ---
function AttachmentCard({ attachment }: { attachment: MessageAttachment }) {
  const isImage = attachment.mimeType.startsWith('image/');
  const isPdf = attachment.mimeType === 'application/pdf';

  function formatSize(bytes?: number) {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }

  const iconColor = isImage
    ? 'text-blue-500 bg-blue-50 dark:bg-blue-500/10'
    : isPdf
    ? 'text-red-500 bg-red-50 dark:bg-red-500/10'
    : 'text-orange-500 bg-orange-50 dark:bg-orange-500/10';

  return (
    <a
      href={attachment.publicUrl || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2.5 max-w-[240px] bg-white dark:bg-[#1c1c1c] border border-gray-200 dark:border-white/10 rounded-2xl px-3 py-2.5 hover:border-orange-300 dark:hover:border-orange-500/40 transition-all group shadow-sm"
    >
      {/* Preview / icon */}
      {isImage && (attachment.previewUrl || attachment.publicUrl) ? (
        <img
          src={attachment.previewUrl || attachment.publicUrl}
          alt={attachment.name}
          className="w-10 h-10 object-cover rounded-xl flex-shrink-0"
        />
      ) : (
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${iconColor}`}>
          {isImage ? <ImageIcon className="w-5 h-5" /> : isPdf ? <FileText className="w-5 h-5" /> : <File className="w-5 h-5" />}
        </div>
      )}

      {/* Info */}
      <div className="min-w-0">
        <p className="text-xs font-semibold text-gray-800 dark:text-gray-100 truncate group-hover:text-orange-500 dark:group-hover:text-orange-400 transition-colors" title={attachment.name}>
          {attachment.name}
        </p>
        {attachment.sizeBytes && (
          <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">{formatSize(attachment.sizeBytes)}</p>
        )}
      </div>
    </a>
  );
}
