import React, { useState, useRef, useCallback } from 'react';
import { Cpu, ChevronDown, Check } from 'lucide-react';
import { useClickOutside } from '@/hooks/use-click-outside';
import { AI_MODELS, AI_PROVIDERS } from '@/lib/constants';
import { useTranslation } from 'react-i18next';

interface ModelSelectorProps {
  model: string;
  setModel: (model: string) => void;
}

export function ProviderSelector({ model, setModel }: ModelSelectorProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [configuredProviders, setConfiguredProviders] = useState<Record<string, boolean>>({});

  React.useEffect(() => {
    fetch('/api/config/providers')
      .then(res => res.json())
      .then(data => setConfiguredProviders(data))
      .catch(() => { /* Backend chưa sẵn sàng — bỏ qua, dùng providers mặc định */ });
  }, []);

  const selectedModel = AI_MODELS.find(m => m.id === model) || AI_MODELS[0];
  const selectedProvider = AI_PROVIDERS.find(provider => provider.id === selectedModel.provider);

  // Dùng hook tái sử dụng thay vì duplicate useEffect
  useClickOutside(dropdownRef, useCallback(() => setIsOpen(false), []));

  return (
    <div className="relative flex items-center" ref={dropdownRef}>
      <button 
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center rounded-xl border border-gray-100 dark:border-slate-800 bg-gray-50 dark:bg-slate-800 px-3 py-1.5 transition-colors hover:bg-gray-100 dark:hover:bg-slate-700 active:bg-gray-200 dark:active:bg-slate-600"
      >
        <Cpu className="w-3.5 h-3.5 text-gray-700 dark:text-gray-300 mr-2" />
        <div className="flex items-center gap-1">
          <span className="text-[12px] font-bold text-gray-700 dark:text-gray-300">
            {selectedProvider?.name ?? selectedModel.provider}: {selectedModel.name}
          </span>
          <ChevronDown className={`w-3 h-3 text-gray-400 dark:text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
        </div>
      </button>

      {/* Menu thả xuống */}
      {isOpen && (
        <div className="absolute bottom-full mb-2 left-0 md:left-auto md:right-0 w-48 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 shadow-xl shadow-gray-200/50 dark:shadow-none rounded-xl py-1 z-50 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 border-b border-gray-50 dark:border-slate-800 mb-1">
            {t('settings.selectModel', 'Chọn mô hình AI')}
          </div>
          {AI_MODELS.map((m) => (
            <button
              key={m.id}
              onClick={() => {
                setModel(m.id);
                setIsOpen(false);
              }}
              className={`w-full text-left px-3 py-2.5 text-[12px] font-medium flex items-center justify-between transition-colors ${
                model === m.id 
                  ? 'text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800' 
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-slate-800'
              }`}
            >
              <span>
                <span className="block">{m.fullName}</span>
                <span className="block text-[10px] text-gray-400">
                  {AI_PROVIDERS.find(provider => provider.id === m.provider)?.name ?? m.provider}
                </span>
              </span>
              {model === m.id && <Check className="w-3.5 h-3.5 text-gray-900 dark:text-white" />}
            </button>
          ))}
        </div>
      )}
      
      {/* Warning if API key is missing */}
      {selectedProvider?.id && configuredProviders[selectedProvider.id] === false && (
        <div className="absolute top-full left-0 mt-2 p-2 w-64 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-center shadow-lg z-50 animate-in fade-in zoom-in-95 duration-200">
          <p className="text-[11px] text-red-600 dark:text-red-400 font-medium">
            Mô hình này chưa có API Key! Vui lòng chọn mô hình khác (ví dụ: GPT-4o Mini, Gemini 1.5).
          </p>
        </div>
      )}
    </div>
  );
}
