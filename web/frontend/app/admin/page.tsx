'use client';

import React from 'react';
import { Settings, BarChart2, BrainCircuit } from 'lucide-react';
import AnalyticsTab from '@/components/admin/AnalyticsTab';
import Link from 'next/link';
import SystemSettingsTab from '@/components/admin/SystemSettingsTab';
import { useTranslation } from 'react-i18next';

export default function AdminPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = React.useState<'analytics' | 'settings'>('analytics');

  React.useEffect(() => {
    if (window.location.hash === '#settings') setActiveTab('settings');
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col font-sans">
      <header className="h-16 flex items-center justify-between px-6 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 shrink-0">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 -ml-2 rounded-xl text-gray-500 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-arrow-left"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
              <Settings className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white leading-tight">{t('admin.systemAdmin', 'Quản trị hệ thống')}</h1>
              <p className="text-xs text-gray-500 font-medium">{t('admin.systemAdminDesc', 'Analytics & System Settings')}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-6 lg:p-8 space-y-8">
          
          <div className="flex mx-auto p-1 bg-gray-100/80 dark:bg-slate-800/80 rounded-xl w-max border border-gray-200/50 dark:border-slate-700/50">
            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'analytics'
                  ? 'bg-white dark:bg-slate-900 text-gray-800 dark:text-gray-200 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-slate-700/50'
              }`}
            >
              <BarChart2 className="w-4 h-4" />
              {t('admin.analyticsTab', 'Thống kê & Lịch sử')}
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'settings'
                  ? 'bg-white dark:bg-slate-900 text-gray-800 dark:text-gray-200 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-slate-700/50'
              }`}
            >
              <BrainCircuit className="w-4 h-4" />
              {t('admin.aiConfigTab', 'Cấu hình AI')}
            </button>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-6">
            {activeTab === 'analytics' ? (
              <AnalyticsTab />
            ) : (
              <SystemSettingsTab />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
