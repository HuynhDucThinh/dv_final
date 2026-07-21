'use client';

import { Car } from 'lucide-react';

interface ChatEmptyStateProps {
  onSelectSuggestion: (prompt: string) => void;
}

const SUGGESTIONS = [
  'Đánh giá thị trường ô tô điện tại Việt Nam trong năm nay.',
  'Những dòng xe SUV 7 chỗ nào bán chạy nhất phân khúc?',
  'So sánh giá lăn bánh các xe hạng B phổ biến?',
];

export function ChatEmptyState({ onSelectSuggestion }: ChatEmptyStateProps) {
  return (
    <div className="mx-auto flex min-h-full w-full max-w-3xl flex-col justify-center px-4 py-10 text-center">
      <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-orange-500 text-white shadow-lg shadow-orange-500/15">
        <Car className="h-8 w-8" />
      </div>
      <h1 className="text-2xl font-bold tracking-tight text-slate-950 dark:text-white sm:text-3xl">
        Phân tích Dữ liệu Ô tô
      </h1>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500 dark:text-slate-400 sm:text-base">
        Hỏi thông tin về giá bán, thông số kỹ thuật, và xu hướng thị trường xe ô tô tại Việt Nam.
      </p>

      <div className="mt-8 grid gap-2.5 sm:grid-cols-3">
        {SUGGESTIONS.map(prompt => (
          <button
            key={prompt}
            type="button"
            onClick={() => onSelectSuggestion(prompt)}
            className="rounded-2xl border border-slate-200 bg-white p-4 text-left text-sm font-semibold leading-6 text-slate-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 dark:border-white/10 dark:bg-white/5 dark:text-slate-200 dark:hover:bg-gray-800"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
