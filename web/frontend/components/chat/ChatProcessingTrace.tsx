'use client';

import { useId } from 'react';
import { Check, ChevronDown, Circle, Loader2, XCircle } from 'lucide-react';

export type ChatProcessingStage =
  | 'idle'
  | 'analyzing'
  | 'searching'
  | 'selecting'
  | 'generating'
  | 'completed'
  | 'cancelled'
  | 'error';

interface ChatProcessingTraceProps {
  stage: ChatProcessingStage;
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
}

const STEPS: Array<{ key: ChatProcessingStage; label: string; doneLabel: string; activeLabel: string }> = [
  { key: 'analyzing', label: 'Phân tích yêu cầu', doneLabel: 'Đã phân tích yêu cầu', activeLabel: 'Đang phân tích yêu cầu' },
  { key: 'searching', label: 'Tra cứu dữ liệu hệ thống', doneLabel: 'Đã tra cứu dữ liệu hệ thống', activeLabel: 'Đang tra cứu dữ liệu hệ thống' },
  { key: 'selecting', label: 'Chọn lọc thông tin phù hợp', doneLabel: 'Đã chọn lọc thông tin phù hợp', activeLabel: 'Đang chọn lọc thông tin phù hợp' },
  { key: 'generating', label: 'Tổng hợp câu trả lời', doneLabel: 'Đã tổng hợp câu trả lời', activeLabel: 'Đang tổng hợp câu trả lời' },
];

const ORDER: Record<ChatProcessingStage, number> = {
  idle: -1,
  analyzing: 0,
  searching: 1,
  selecting: 2,
  generating: 3,
  completed: 4,
  cancelled: -1,
  error: -1,
};

function getSummary(stage: ChatProcessingStage): string {
  if (stage === 'analyzing') return 'Đang phân tích yêu cầu';
  if (stage === 'searching') return 'Đang tra cứu dữ liệu';
  if (stage === 'selecting') return 'Đang kiểm tra thông tin phù hợp';
  if (stage === 'generating') return 'Đang tổng hợp câu trả lời';
  if (stage === 'completed') return 'Tra cứu hoàn tất';
  if (stage === 'cancelled') return 'Đã dừng yêu cầu';
  if (stage === 'error') return 'Không thể hoàn tất yêu cầu';
  return 'Đang tra cứu dữ liệu';
}

function StatusIcon({ stage }: { stage: ChatProcessingStage }) {
  if (stage === 'completed') return <Check className="h-4 w-4 text-emerald-600" />;
  if (stage === 'cancelled' || stage === 'error') return <XCircle className="h-4 w-4 text-slate-500" />;
  return <Loader2 className="h-4 w-4 animate-spin text-gray-600 motion-reduce:animate-none" aria-hidden="true" />;
}

export function ChatProcessingTrace({
  stage,
  collapsed = true,
  onToggleCollapsed,
}: ChatProcessingTraceProps) {
  const componentId = useId();

  if (stage === 'idle') return null;

  const activeIndex = ORDER[stage];
  const isDone = stage === 'completed';
  const isTerminal = isDone || stage === 'cancelled' || stage === 'error';
  const detailsId = `${componentId}-processing-trace`;
  const toggleLabel = collapsed ? 'Xem quá trình' : 'Ẩn quá trình';

  if (collapsed) {
    return (
      <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50/70 px-3 py-2 text-sm text-slate-600 shadow-sm dark:border-white/10 dark:bg-white/5 dark:text-slate-300" aria-live="polite">
        <div className="flex items-center justify-between gap-3">
          <span className="inline-flex min-w-0 items-center gap-2 font-medium">
            <StatusIcon stage={stage} />
            <span className="truncate">{getSummary(stage)}</span>
          </span>
          {onToggleCollapsed && (
            <button
              type="button"
              onClick={onToggleCollapsed}
              className="inline-flex shrink-0 items-center gap-1 rounded-lg px-2 py-1 text-xs font-semibold text-gray-700 transition hover:bg-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 dark:text-gray-300 dark:hover:bg-gray-800"
              aria-expanded="false"
              aria-controls={detailsId}
            >
              {toggleLabel}
              <ChevronDown className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <section
      className="mt-3 rounded-2xl border border-gray-200 bg-gray-50 p-4 shadow-sm dark:border-gray-700/50 dark:bg-gray-800/50"
      aria-live="polite"
      aria-label="Tiến trình xử lý"
      id={detailsId}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-slate-100">
            <StatusIcon stage={stage} />
            {getSummary(stage)}
          </h3>
          <p className="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">
            Quá trình này chỉ mô tả các bước xử lý tổng quan.
          </p>
        </div>

        {onToggleCollapsed && (
          <button
            type="button"
            onClick={onToggleCollapsed}
            className="shrink-0 rounded-lg px-2 py-1 text-xs font-semibold text-gray-700 transition hover:bg-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 dark:text-gray-300 dark:hover:bg-gray-800"
            aria-expanded="true"
            aria-controls={detailsId}
          >
            {toggleLabel}
          </button>
        )}
      </div>

      <ol className="mt-3 space-y-2">
        {STEPS.map((step, index) => {
          const complete = isDone || activeIndex > index;
          const active = !isTerminal && activeIndex === index;
          return (
            <li key={step.key} className="flex items-center gap-2 text-sm">
              <span
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                  complete
                    ? 'border-emerald-500 bg-emerald-500 text-white'
                    : active
                      ? 'border-gray-500 bg-white text-gray-700 dark:bg-slate-950 dark:text-gray-200'
                      : 'border-slate-300 bg-white text-slate-400 dark:border-slate-700 dark:bg-slate-950'
                }`}
              >
                {complete ? <Check className="h-3 w-3" /> : active ? <Loader2 className="h-3 w-3 animate-spin motion-reduce:animate-none" /> : <Circle className="h-2 w-2 fill-current" />}
              </span>
              <span className={`${complete ? 'text-slate-700 dark:text-slate-200' : active ? 'font-semibold text-gray-800 dark:text-gray-200' : 'text-slate-500 dark:text-slate-400'}`}>
                {complete ? step.doneLabel : active ? step.activeLabel : step.label}
              </span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
