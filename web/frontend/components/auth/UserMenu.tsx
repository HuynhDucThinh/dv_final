'use client';

import React, { useState, useRef } from 'react';
import { LogIn, LogOut, User, ChevronUp } from 'lucide-react';
import { signOut } from '@/lib/auth-client';
import { useAuth } from '@/hooks/use-auth';
import { useClickOutside } from '@/hooks/use-click-outside';
import { AuthModal } from './AuthModal';
import { useTranslation } from 'react-i18next';

export function UserMenu() {
  const { t } = useTranslation();
  const { user, isLoading, isAuthenticated } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<'login' | 'register'>('login');
  const dropdownRef = useRef<HTMLDivElement>(null);

  useClickOutside(dropdownRef, () => setIsDropdownOpen(false));

  const handleSignOut = async () => {
    setIsDropdownOpen(false);
    await signOut();
  };

  const openLogin = () => {
    setAuthModalMode('login');
    setIsAuthModalOpen(true);
  };

  const openRegister = () => {
    setAuthModalMode('register');
    setIsAuthModalOpen(true);
  };

  // Skeleton loading
  if (isLoading) {
    return (
      <div className="flex items-center gap-2.5 px-3 py-2 animate-pulse">
        <div className="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-700 flex-shrink-0" />
        <div className="flex-1">
          <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-1" />
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-28" />
        </div>
      </div>
    );
  }

  // Chưa đăng nhập — hiện 2 nút
  if (!isAuthenticated) {
    return (
      <>
        <div className="flex flex-col gap-1.5 px-1">
          <button
            onClick={openLogin}
            id="btn-auth-login"
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-sm font-medium text-white transition-all"
            style={{ background: 'linear-gradient(135deg, #f97316, #ea580c)' }}
          >
            <LogIn className="w-3.5 h-3.5" />
            {t('sidebar.loginBtn')}
          </button>
          <button
            onClick={openRegister}
            id="btn-auth-register"
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {t('sidebar.registerBtn')}
          </button>
        </div>

        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
          defaultMode={authModalMode}
        />
      </>
    );
  }

  // Đã đăng nhập — hiện avatar + dropdown
  const avatarUrl = (user as { avatarUrl?: string; image?: string })?.avatarUrl || (user as { avatarUrl?: string; image?: string })?.image;
  const displayName = user?.name || user?.email?.split('@')[0] || t('sidebar.userLabel');

  return (
    <div ref={dropdownRef} className="relative px-1">
      {/* Dropdown */}
      {isDropdownOpen && (
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-150">
          <div className="px-3 py-2.5 border-b border-gray-100 dark:border-gray-800">
            <p className="text-xs font-semibold text-gray-900 dark:text-white truncate">{user?.name || 'Người dùng'}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{user?.email}</p>
          </div>
          <button
            onClick={handleSignOut}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            {t('sidebar.signOut')}
          </button>
        </div>
      )}

      {/* User button */}
      <button
        id="btn-user-menu"
        onClick={() => setIsDropdownOpen((v) => !v)}
        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
      >
        {/* Avatar */}
        <div className="w-7 h-7 rounded-full flex-shrink-0 overflow-hidden bg-orange-100 dark:bg-orange-500/20 flex items-center justify-center">
          {avatarUrl ? (
            <img src={avatarUrl} alt={displayName} className="w-full h-full object-cover" />
          ) : (
            <User className="w-3.5 h-3.5 text-orange-500" />
          )}
        </div>

        {/* Name + email */}
        <div className="flex-1 text-left overflow-hidden">
          <p className="text-xs font-semibold text-gray-800 dark:text-gray-200 truncate">{displayName}</p>
          <p className="text-[10px] text-gray-400 dark:text-gray-500 truncate">{user?.email}</p>
        </div>

        <ChevronUp
          className={`w-3.5 h-3.5 text-gray-400 flex-shrink-0 transition-transform duration-200 ${isDropdownOpen ? 'rotate-0' : 'rotate-180'}`}
        />
      </button>
    </div>
  );
}
