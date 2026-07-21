import React, { useState, useRef, useCallback } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { useClickOutside } from '@/hooks/use-click-outside';
import { useTranslation } from 'react-i18next';

export function LanguageSelector() {
  const { i18n, t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useClickOutside(dropdownRef, useCallback(() => setIsOpen(false), []));

  const currentLang = i18n.language === 'en' ? 'English' : 'Tiếng Việt';

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    setIsOpen(false);
  };

  return (
    <div className="relative flex items-center" ref={dropdownRef}>
      <button 
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`p-1.5 rounded-lg transition-all ${
          isOpen
            ? 'bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200'
            : 'text-gray-500 dark:text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800'
        }`}
        title={t('settings.language', 'Ngôn ngữ')}
      >
        <Globe className="w-4 h-4" />
      </button>

      {/* Menu thả xuống */}
      {isOpen && (
        <div className="absolute bottom-full mb-2 right-0 w-40 bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 shadow-xl shadow-gray-200/50 dark:shadow-none rounded-xl py-1 z-50 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500 border-b border-gray-50 dark:border-slate-800 mb-1">
            {t('settings.language', 'NGÔN NGỮ')}
          </div>
          
          <button
            onClick={() => changeLanguage('vi')}
            className={`w-full text-left px-3 py-2.5 text-[12px] font-medium flex items-center justify-between transition-colors ${
              i18n.language === 'vi' 
                ? 'text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800' 
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-slate-800 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Tiếng Việt
            {i18n.language === 'vi' && <Check className="w-3.5 h-3.5" />}
          </button>
          
          <button
            onClick={() => changeLanguage('en')}
            className={`w-full text-left px-3 py-2.5 text-[12px] font-medium flex items-center justify-between transition-colors ${
              i18n.language === 'en' 
                ? 'text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800' 
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-slate-800 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            English
            {i18n.language === 'en' && <Check className="w-3.5 h-3.5" />}
          </button>
        </div>
      )}
    </div>
  );
}
