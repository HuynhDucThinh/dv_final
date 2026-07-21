'use client';

import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  Check,
  RefreshCw,
  RotateCcw,
  Save,
} from 'lucide-react';
import { AI_MODELS, AI_PROVIDERS } from '@/lib/constants';
import { AISettings, DEFAULT_AI_SETTINGS, setRoleByModel } from '@/lib/ai-settings';
import { useAISettings } from '@/hooks/use-ai-settings';
import { useTranslation } from 'react-i18next';

export default function SystemSettingsTab() {
  const { t } = useTranslation();
  const { settings, setSettings, resetSettings, isLoaded } = useAISettings();
  const [draft, setDraft] = useState<AISettings>(DEFAULT_AI_SETTINGS);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (isLoaded) setDraft(settings);
  }, [isLoaded, settings]);

  const updateDraft = <K extends keyof AISettings,>(key: K, value: AISettings[K]) => {
    setDraft(current => ({ ...current, [key]: value }));
    setSaved(false);
  };

  const updateProviderKey = (provider: 'google' | 'huggingface', apiKey: string) => {
    setDraft(current => ({
      ...current,
      providerCredentials: {
        ...current.providerCredentials,
        [provider]: {
          apiKey,
          remember: current.providerCredentials[provider]?.remember ?? true,
        },
      },
    }));
    setSaved(false);
  };

  const updateProviderRemember = (provider: 'google' | 'huggingface', remember: boolean) => {
    setDraft(current => ({
      ...current,
      providerCredentials: {
        ...current.providerCredentials,
        [provider]: {
          apiKey: current.providerCredentials[provider]?.apiKey ?? '',
          remember,
        },
      },
    }));
    setSaved(false);
  };

  const updateRoleModel = (role: 'answer' | 'rewriter' | 'summarizer', modelId: string) => {
    setDraft(current => setRoleByModel(current, role, modelId));
    setSaved(false);
  };

  const handleSave = () => {
    setSettings(draft);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    const confirmed = window.confirm(
      t('admin.restoreConfigConfirm', 'Restore default AI configuration? This will clear provider API keys and reset model selections on this browser.')
    );
    if (!confirmed) return;

    resetSettings();
    setDraft(DEFAULT_AI_SETTINGS);
    setSaved(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-gray-800 dark:text-gray-200 mb-2">
            <BrainCircuit className="w-5 h-5" />
            <span className="text-xs font-bold uppercase tracking-widest">{t('admin.aiConfig', 'AI Configuration')}</span>
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">{t('admin.aiConfigTitle', 'Cấu hình AI & Tìm kiếm')}</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 max-w-2xl">
            {t('admin.aiConfigDesc', 'Điều chỉnh cấu hình mặc định dùng cho các câu hỏi mới trên trình duyệt này.')}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleReset}
            className="inline-flex items-center gap-2 px-3.5 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-slate-700 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            {t('admin.default', 'Mặc định')}
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-gray-800 hover:bg-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-xl transition-colors shadow-sm"
          >
            {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? t('admin.saved', 'Đã lưu') : t('admin.saveConfig', 'Lưu cấu hình')}
          </button>
        </div>
      </div>

      <section className="rounded-2xl border border-gray-200 dark:border-slate-800 p-5">
        <div className="mb-4">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white">{t('admin.providerCreds', 'Provider credentials')}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {t('admin.providerCredsDesc', 'API keys are stored in this browser and sent only with inference requests.')}
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {AI_PROVIDERS.filter(provider => provider.requiresApiKey).map(provider => (
                <div key={provider.id} className="rounded-xl border border-gray-200 dark:border-slate-700 p-4">
                  <label className="text-xs font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400">{provider.name}</label>
                  <input
                    type="password"
                    value={draft.providerCredentials[provider.id]?.apiKey ?? ''}
                    onChange={event => updateProviderKey(provider.id as 'google' | 'huggingface', event.target.value)}
                    className="mt-2 w-full rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-gray-900 dark:text-white outline-none focus:border-gray-500"
                    placeholder="API key"
                  />
                  <label className="mt-3 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                    <input
                      type="checkbox"
                      checked={draft.providerCredentials[provider.id]?.remember ?? true}
                      onChange={event => updateProviderRemember(provider.id as 'google' | 'huggingface', event.target.checked)}
                    />
                    {t('admin.rememberDevice', 'Remember on this device')}
                  </label>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-2xl border border-gray-200 dark:border-slate-800 p-5">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white">{t('admin.inferenceRoles', 'Inference roles')}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {t('admin.inferenceRolesDesc', 'Answer generation, query rewriting, and memory summarization can use separate provider models.')}
              </p>
            </div>
            <div className="space-y-3">
              {(['answer', 'rewriter', 'summarizer'] as const).map(role => (
                <div key={role} className="grid gap-2 md:grid-cols-[170px_1fr] md:items-center">
                  <span className="text-sm font-semibold capitalize text-gray-700 dark:text-gray-300">{role}</span>
                  <select
                    value={draft.roles[role].model}
                    onChange={event => updateRoleModel(role, event.target.value)}
                    disabled={draft.useSameModelForHelperRoles && role !== 'answer'}
                    className="rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-gray-900 dark:text-white outline-none focus:border-gray-500 disabled:opacity-60"
                  >
                    {AI_MODELS.filter(model => model.provider !== 'ollama').map(model => (
                      <option key={`${role}-${model.id}`} value={model.id}>
                        {model.fullName} - {AI_PROVIDERS.find(provider => provider.id === model.provider)?.name}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
              <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                <input
                  type="checkbox"
                  checked={draft.useSameModelForHelperRoles}
                  onChange={event => {
                    const enabled = event.target.checked;
                    setDraft(current => {
                      if (!enabled) return { ...current, useSameModelForHelperRoles: false };
                      const answer = current.roles.answer;
                      return {
                        ...current,
                        useSameModelForHelperRoles: true,
                        roles: {
                          ...current.roles,
                          rewriter: { ...answer },
                          summarizer: { ...answer },
                        },
                      };
                    });
                    setSaved(false);
                  }}
                />
                {t('admin.useSameModel', 'Use answer model for rewriter and memory summarizer')}
              </label>
            </div>
          </section>

          <section className="rounded-2xl border border-gray-200 dark:border-slate-800 p-5">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white">{t('admin.defaultModel', 'Mô hình trả lời mặc định')}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{t('admin.defaultModelDesc', 'Backend sẽ dùng chiến lược API/local fallback đã cấu hình trên server.')}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {AI_MODELS.map(model => (
                <button
                  key={model.id}
                  type="button"
                  onClick={() => updateRoleModel('answer', model.id)}
                  className={`flex items-center justify-between gap-3 p-4 rounded-xl border text-left transition-all ${draft.roles.answer.model === model.id ? 'border-gray-800 bg-gray-50 dark:bg-gray-800/50 ring-1 ring-gray-800 dark:ring-gray-600 dark:border-gray-600' : 'border-gray-200 dark:border-slate-700 hover:border-gray-400 dark:hover:border-gray-500'}`}
                >
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">{model.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{model.fullName}</p>
                  </div>
                  {draft.roles.answer.model === model.id && <Check className="w-4 h-4 text-gray-800 dark:text-gray-200" />}
                </button>
              ))}
            </div>
          </section>

          <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <RangeSetting
              label={t('admin.temperatureLabel', 'Temperature')}
              value={draft.temperature}
              displayValue={draft.temperature.toFixed(2)}
              min={0}
              max={1}
              step={0.05}
              description={t('admin.temperatureDesc', 'Độ sáng tạo của câu trả lời. Khuyên dùng 0.1–0.3.')}
              onChange={value => updateDraft('temperature', value)}
            />
            <RangeSetting
              label={t('admin.maxTokensLabel', 'Max Tokens')}
              value={draft.maxTokens}
              displayValue={String(draft.maxTokens)}
              min={100}
              max={4000}
              step={100}
              description={t('admin.maxTokensDesc', 'Giới hạn số token tối đa cho câu trả lời.')}
              onChange={value => updateDraft('maxTokens', value)}
            />
          </section>
    </div>
  );
}

interface RangeSettingProps {
  label: string;
  value: number;
  displayValue: string;
  min: number;
  max: number;
  step: number;
  description: string;
  onChange: (value: number) => void;
}

function RangeSetting({ label, value, displayValue, min, max, step, description, onChange }: RangeSettingProps) {
  return (
    <div className="rounded-2xl border border-gray-200 dark:border-slate-800 p-5 space-y-4">
      <div className="flex items-center justify-between gap-3">
        <label className="text-sm font-bold text-gray-900 dark:text-white">{label}</label>
        <span className="font-mono text-xs font-semibold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 px-2 py-1 rounded-lg">{displayValue}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={event => onChange(Number(event.target.value))}
        className="w-full h-2 bg-gray-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
      />
      <p className="text-xs leading-5 text-gray-500 dark:text-gray-400">{description}</p>
    </div>
  );
}
