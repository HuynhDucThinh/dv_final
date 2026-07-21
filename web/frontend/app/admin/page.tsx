'use client';

import React from 'react';
import { Settings, BarChart2, BrainCircuit, ChevronLeft } from 'lucide-react';
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
    <div className="min-h-screen bg-white dark:bg-[#171717] font-sans">
      <div className="max-w-5xl mx-auto px-6 py-10">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="p-2 -ml-2 rounded-xl text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-white">
              {t('admin.systemAdmin', 'Quản trị hệ thống')}
            </h1>
          </div>
        </div>

        {/* Toolbar (Tabs) */}
        <div className="flex items-center pb-3 mb-4 border-b border-gray-100 dark:border-white/10">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'analytics'
                  ? 'bg-gray-100 dark:bg-white/10 text-gray-900 dark:text-white'
                  : 'text-gray-500 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-white/5'
              }`}
            >
              <BarChart2 className="w-4 h-4" />
              {t('admin.analyticsTab', 'Thống kê & Lịch sử')}
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'settings'
                  ? 'bg-gray-100 dark:bg-white/10 text-gray-900 dark:text-white'
                  : 'text-gray-500 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-white/5'
              }`}
            >
              <BrainCircuit className="w-4 h-4" />
              {t('admin.aiConfigTab', 'Cấu hình AI')}
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="mt-6 bg-white dark:bg-[#212121] rounded-2xl border border-gray-100 dark:border-white/10 shadow-sm p-6">
          {activeTab === 'analytics' ? (
            <AnalyticsTab />
          ) : (
            <SystemSettingsTab />
          )}
        </div>
      </div>
    </div>
  );
}
