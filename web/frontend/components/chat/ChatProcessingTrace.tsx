'use client';

import { useId } from 'react';
import { Check, ChevronDown, Circle, Loader2, XCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

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

type StepKey = 'analyzing' | 'searching' | 'selecting' | 'generating';

const STEP_KEYS: StepKey[] = ['analyzing', 'searching', 'selecting', 'generating'];

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
  const { t } = useTranslation();
  const componentId = useId();

  if (stage === 'idle') return null;

  const activeIndex = ORDER[stage];
  const isDone = stage === 'completed';
  const isTerminal = isDone || stage === 'cancelled' || stage === 'error';
  const detailsId = `${componentId}-processing-trace`;
  const toggleLabel = collapsed ? t('chat.trace.showProcess') : t('chat.trace.hideProcess');

  // Summary text per stage
  function getSummary(): string {
    if (stage === 'analyzing') return t('chat.trace.summaryAnalyzing');
    if (stage === 'searching') return t('chat.trace.summarySearching');
    if (stage === 'selecting') return t('chat.trace.summarySelecting');
    if (stage === 'generating') return t('chat.trace.summaryGenerating');
    if (stage === 'completed') return t('chat.trace.summaryCompleted');
    if (stage === 'cancelled') return t('chat.trace.summaryCancelled');
    if (stage === 'error') return t('chat.trace.summaryError');
    return t('chat.trace.summarySearching');
  }

  // Step labels
  function getStepLabel(key: StepKey, status: 'default' | 'active' | 'done'): string {
    const map: Record<StepKey, Record<'default' | 'active' | 'done', string>> = {
      analyzing: {
        default: t('chat.trace.analyzing'),
        active: t('chat.trace.analyzingActive'),
        done: t('chat.trace.analyzingDone'),
      },
      searching: {
        default: t('chat.trace.searching'),
        active: t('chat.trace.searchingActive'),
        done: t('chat.trace.searchingDone'),
      },
      selecting: {
        default: t('chat.trace.selecting'),
        active: t('chat.trace.selectingActive'),
        done: t('chat.trace.selectingDone'),
      },
      generating: {
        default: t('chat.trace.generating'),
        active: t('chat.trace.generatingActive'),
        done: t('chat.trace.generatingDone'),
      },
    };
    return map[key][status];
  }

  if (collapsed) {
    return (
      <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50/70 px-3 py-2 text-sm text-slate-600 shadow-sm dark:border-white/10 dark:bg-white/5 dark:text-slate-300" aria-live="polite">
        <div className="flex items-center justify-between gap-3">
          <span className="inline-flex min-w-0 items-center gap-2 font-medium">
            <StatusIcon stage={stage} />
            <span className="truncate">{getSummary()}</span>
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
      aria-label={t('chat.trace.ariaLabel')}
      id={detailsId}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-slate-100">
            <StatusIcon stage={stage} />
            {getSummary()}
          </h3>
          <p className="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">
            {t('chat.trace.overview')}
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
        {STEP_KEYS.map((key, index) => {
          const complete = isDone || activeIndex > index;
          const active = !isTerminal && activeIndex === index;
          const status = complete ? 'done' : active ? 'active' : 'default';
          return (
            <li key={key} className="flex items-center gap-2 text-sm">
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
                {getStepLabel(key, status)}
              </span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
