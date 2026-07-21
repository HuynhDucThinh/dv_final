'use client';

import React, { useState, useCallback } from 'react';
import { Check, Pencil, X, Play, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface ExecutionResult {
  success: boolean;
  stdout: string;
  stderr: string;
  images: string[];
  error?: string;
}

interface CodeApprovalBlockProps {
  code: string;
  blockIndex: number;
  messageId: string;
  sessionId?: string;
  onExecuted?: (result: ExecutionResult) => void;
}

/**
 * Block hiển thị code Python với khả năng:
 * 1. Xem code
 * 2. Chỉnh sửa trực tiếp (inline editor)
 * 3. Phê duyệt → Thực thi
 * 4. Hiển thị kết quả (stdout + biểu đồ)
 *
 * Nguyên tắc: Code chỉ thực thi khi người dùng bấm "Phê duyệt & Thực thi"
 */
export function CodeApprovalBlock({
  code,
  blockIndex,
  messageId,
  sessionId = 'unknown',
  onExecuted,
}: CodeApprovalBlockProps) {
  const [editedCode, setEditedCode] = useState(code);
  const [isEditing, setIsEditing] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [showResult, setShowResult] = useState(true);

  const handleApproveAndExecute = useCallback(async () => {
    setIsExecuting(true);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/api/analysis/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: editedCode,
          session_id: sessionId,
        }),
      });

      const data: ExecutionResult = await response.json();
      setResult(data);
      setShowResult(true);
      onExecuted?.(data);

      // Lưu log
      try {
        await fetch(`${API_BASE}/api/analysis/log`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            user_request: `[Code block ${blockIndex} executed]`,
            code: editedCode,
            execution_result: data.success ? data.stdout : (data.error || data.stderr),
            charts_count: data.images.length,
          }),
        });
      } catch {
        // log failure không chặn UX
      }
    } catch (err) {
      setResult({
        success: false,
        stdout: '',
        stderr: '',
        images: [],
        error: `Lỗi kết nối: ${err}`,
      });
    } finally {
      setIsExecuting(false);
    }
  }, [editedCode, sessionId, blockIndex, onExecuted]);

  const handleCancelEdit = () => {
    setEditedCode(code);
    setIsEditing(false);
  };

  return (
    <div className="my-3 rounded-xl border border-zinc-700 bg-zinc-900 overflow-hidden text-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-800 border-b border-zinc-700">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-zinc-400">python</span>
          {result && (
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              result.success
                ? 'bg-emerald-500/20 text-emerald-400'
                : 'bg-red-500/20 text-red-400'
            }`}>
              {result.success ? '✓ Thành công' : '✗ Lỗi'}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          {!result && !isExecuting && (
            <>
              {isEditing ? (
                <>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-zinc-700 text-zinc-300 hover:bg-zinc-600 transition-colors"
                    title="Lưu chỉnh sửa"
                  >
                    <Check className="w-3 h-3" /> Lưu
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-zinc-700 text-zinc-400 hover:bg-zinc-600 transition-colors"
                    title="Hủy chỉnh sửa"
                  >
                    <X className="w-3 h-3" /> Hủy
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-zinc-700 text-zinc-300 hover:bg-zinc-600 transition-colors"
                  title="Chỉnh sửa code"
                >
                  <Pencil className="w-3 h-3" /> Chỉnh sửa
                </button>
              )}

              <button
                onClick={handleApproveAndExecute}
                disabled={isEditing}
                className="flex items-center gap-1.5 px-3 py-1 text-xs rounded-lg
                           bg-emerald-600 hover:bg-emerald-500 text-white font-semibold
                           disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Phê duyệt và chạy code"
              >
                <Play className="w-3 h-3" />
                Phê duyệt &amp; Thực thi
              </button>
            </>
          )}

          {isExecuting && (
            <div className="flex items-center gap-1.5 px-3 py-1 text-xs text-zinc-400">
              <Loader2 className="w-3 h-3 animate-spin" />
              Đang thực thi...
            </div>
          )}

          {result && (
            <button
              onClick={() => setShowResult(!showResult)}
              className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-zinc-700 text-zinc-300 hover:bg-zinc-600 transition-colors"
            >
              {showResult ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              Kết quả
            </button>
          )}
        </div>
      </div>

      {/* Code Display / Editor */}
      {isEditing ? (
        <textarea
          value={editedCode}
          onChange={(e) => setEditedCode(e.target.value)}
          className="w-full bg-zinc-950 text-zinc-200 font-mono text-xs p-4
                     resize-y outline-none border-0 min-h-[120px]"
          style={{ tabSize: 4 }}
          spellCheck={false}
        />
      ) : (
        <pre className="p-4 overflow-x-auto text-zinc-200 font-mono text-xs leading-relaxed">
          <code>{editedCode}</code>
        </pre>
      )}

      {/* Kết quả thực thi */}
      {result && showResult && (
        <div className="border-t border-zinc-700">
          {/* Stdout */}
          {result.stdout && (
            <div className="p-3 bg-zinc-950">
              <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1">Output</div>
              <pre className="text-emerald-400 font-mono text-xs whitespace-pre-wrap overflow-x-auto">
                {result.stdout}
              </pre>
            </div>
          )}

          {/* Error / Stderr */}
          {(result.error || result.stderr) && (
            <div className="p-3 bg-red-950/30">
              <div className="text-[10px] uppercase tracking-wider text-red-400 mb-1">Lỗi</div>
              <pre className="text-red-300 font-mono text-xs whitespace-pre-wrap overflow-x-auto">
                {result.error || result.stderr}
              </pre>
            </div>
          )}

          {/* Biểu đồ */}
          {result.images.length > 0 && (
            <div className="p-3 bg-zinc-950 space-y-3">
              <div className="text-[10px] uppercase tracking-wider text-zinc-500">
                Biểu đồ ({result.images.length})
              </div>
              {result.images.map((img, idx) => (
                <img
                  key={idx}
                  src={`data:image/png;base64,${img}`}
                  alt={`Biểu đồ ${idx + 1}`}
                  className="max-w-full rounded-lg border border-zinc-700"
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
