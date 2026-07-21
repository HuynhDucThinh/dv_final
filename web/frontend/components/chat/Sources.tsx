'use client';

import { useMemo, useState } from 'react';
import { BookOpen, Check, ChevronDown, Copy } from 'lucide-react';
import type { DocumentChunk } from '@/lib/types';

interface SourcesTriggerProps {
  sources?: DocumentChunk[];
  onOpenAll?: (sources: DocumentChunk[]) => void;
  controlsId?: string;
  expanded?: boolean;
}

interface SourceListProps {
  sources?: DocumentChunk[];
}

export function dedupeSources(sources: DocumentChunk[] = []): DocumentChunk[] {
  const seen = new Set<string>();
  return sources.filter((source, index) => {
    const key = sourceKey(source, index);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function sourceKey(source: DocumentChunk, index: number): string {
  return String(source.metadata?.id || `${source.metadata?.source || 'source'}-${index}`);
}

function buildTitle(source: DocumentChunk): string {
  return source.metadata?.source || source.metadata?.law || 'Tài liệu tham khảo';
}

function buildMeta(source: DocumentChunk): string {
  const parts = [];
  if (source.metadata?.dieu) parts.push(`Điều ${source.metadata.dieu}`);
  if (source.metadata?.khoan) parts.push(`Khoản ${source.metadata.khoan}`);
  if (source.metadata?.diem) parts.push(`Điểm ${source.metadata.diem}`);
  return parts.join(' · ');
}

function excerpt(text: string, expanded: boolean): string {
  if (expanded || text.length <= 260) return text;
  return `${text.slice(0, 260).trim()}...`;
}

export function SourcesTrigger({
  sources = [],
  onOpenAll,
  controlsId,
  expanded = false,
}: SourcesTriggerProps) {
  const deduped = useMemo(() => dedupeSources(sources), [sources]);

  if (deduped.length === 0 || !onOpenAll) return null;

  return (
    <div className="mt-2 w-full">
      <button
        type="button"
        onClick={() => onOpenAll(deduped)}
        className="flex w-full items-center justify-between gap-3 rounded-xl border border-gray-200 bg-gray-50/70 px-3 py-2 text-left text-sm font-semibold text-gray-800 transition hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 dark:border-gray-700/50 dark:bg-gray-800/50 dark:text-gray-200 dark:hover:bg-gray-800"
        aria-expanded={expanded}
        aria-controls={controlsId}
        aria-label={`Mở ${deduped.length} nguồn tham khảo`}
      >
        <span className="inline-flex min-w-0 items-center gap-2">
          <BookOpen className="h-4 w-4 shrink-0" />
          <span className="truncate">nguồn tham khảo</span>
          <span
            className="inline-flex h-6 min-w-6 shrink-0 items-center justify-center rounded-full border border-gray-300/40 bg-gray-500/15 px-1.5 text-xs font-semibold text-gray-800 dark:border-gray-600/30 dark:text-gray-200"
            aria-hidden="true"
          >
            {deduped.length}
          </span>
        </span>
        <ChevronDown className={`h-4 w-4 shrink-0 transition-transform ${expanded ? 'rotate-90' : '-rotate-90'}`} />
      </button>
    </div>
  );
}

export function SourceList({ sources = [] }: SourceListProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const deduped = useMemo(() => dedupeSources(sources), [sources]);

  if (deduped.length === 0) return null;

  const copyCitation = async (source: DocumentChunk, key: string) => {
    const meta = [buildTitle(source), buildMeta(source)].filter(Boolean).join(' — ');
    await navigator.clipboard.writeText(`${meta}\n\n${source.content}`);
    setCopiedKey(key);
    window.setTimeout(() => setCopiedKey(null), 1800);
  };

  return (
    <section className="w-full" aria-label="Danh sách nguồn tham khảo">
      <div className="space-y-3">
        {deduped.map((source, index) => {
          const key = sourceKey(source, index);
          const isExpanded = expanded[key] ?? false;
          const meta = buildMeta(source);
          const canExpand = source.content.length > 260;
          return (
            <article
              key={key}
              className="rounded-xl border border-slate-200 bg-white p-3 text-left shadow-sm transition hover:border-gray-300 dark:border-white/10 dark:bg-slate-950/40 dark:hover:border-gray-600/50"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h4 className="truncate text-sm font-bold text-slate-900 dark:text-slate-100">
                    {buildTitle(source)}
                  </h4>
                  {meta && (
                    <p className="mt-1 text-xs font-semibold text-gray-700 dark:text-gray-300">
                      {meta}
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => copyCitation(source, key)}
                  className="shrink-0 rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 dark:hover:bg-white/10 dark:hover:text-gray-300"
                  aria-label="Sao chép trích dẫn"
                  title={copiedKey === key ? 'Đã sao chép' : 'Sao chép trích dẫn'}
                >
                  {copiedKey === key ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                </button>
              </div>

              <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600 dark:text-slate-300">
                “{excerpt(source.content, isExpanded)}”
              </p>

              {canExpand && (
                <button
                  type="button"
                  onClick={() => setExpanded(current => ({ ...current, [key]: !isExpanded }))}
                  className="mt-2 inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-semibold text-gray-700 transition hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 dark:text-gray-300 dark:hover:bg-gray-800"
                  aria-expanded={isExpanded}
                >
                  {isExpanded ? 'Thu gọn' : 'Xem nội dung'}
                  <ChevronDown className={`h-3.5 w-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                </button>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
