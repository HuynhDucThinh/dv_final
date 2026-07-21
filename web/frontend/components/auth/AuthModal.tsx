'use client';

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Mail, Lock, User, Car, Eye, EyeOff, Chrome, Loader2, AlertCircle } from 'lucide-react';
import { signIn, signUp } from '@/lib/auth-client';
import { useTranslation } from 'react-i18next';

type AuthMode = 'login' | 'register';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultMode?: AuthMode;
}

export function AuthModal({ isOpen, onClose, defaultMode = 'login' }: AuthModalProps) {
  const { t } = useTranslation();
  const [mode, setMode] = useState<AuthMode>(defaultMode);
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Form fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (isOpen) {
      setError('');
      setEmail('');
      setPassword('');
      setName('');
      setShowPassword(false);
      setMode(defaultMode);
    }
  }, [isOpen, defaultMode]);

  // Đóng modal khi nhấn Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (mode === 'login') {
        const result = await signIn.email({ email, password });
        if (result.error) {
          setError(result.error.message || t('auth.errorInvalidCredentials'));
        } else {
          onClose();
        }
      } else {
        if (!name.trim()) {
          setError(t('auth.errorNameRequired'));
          setIsLoading(false);
          return;
        }
        if (password.length < 8) {
          setError(t('auth.errorPasswordLength'));
          setIsLoading(false);
          return;
        }
        const result = await signUp.email({ email, password, name });
        if (result.error) {
          setError(result.error.message || t('auth.errorRegisterFailed'));
        } else {
          onClose();
        }
      }
    } catch {
      setError(t('auth.errorGeneral'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    setIsLoading(true);
    try {
      await signIn.social({ provider: 'google' });
      // Google OAuth sẽ redirect về, không cần onClose()
    } catch {
      setError(t('auth.errorGoogleFailed'));
      setIsLoading(false);
    }
  };

  if (!mounted || !isOpen) return null;

  const modal = (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-black/50 dark:bg-black/70 backdrop-blur-sm px-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md bg-white dark:bg-[#1c1c1c] border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative px-6 pt-6 pb-4">
          <button
            onClick={onClose}
            className="absolute right-4 top-4 p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>

          {/* Logo */}
          <div className="flex items-center gap-3 mb-5">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/20 flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #f97316, #ea580c)' }}
            >
              <Car className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-base font-bold text-gray-900 dark:text-white">VietCar AI</span>
              <span className="block text-[10px] font-semibold text-orange-500 uppercase tracking-widest leading-none mt-0.5">
                Car Data Assistant
              </span>
            </div>
          </div>

          {/* Tab switcher */}
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1 mb-5">
            <button
              type="button"
              onClick={() => { setMode('login'); setError(''); }}
              className={`flex-1 py-1.5 text-sm font-semibold rounded-lg transition-all ${
                mode === 'login'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
              }`}
            >
              {t('auth.loginTitle')}
            </button>
            <button
              type="button"
              onClick={() => { setMode('register'); setError(''); }}
              className={`flex-1 py-1.5 text-sm font-semibold rounded-lg transition-all ${
                mode === 'register'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
              }`}
            >
              {t('auth.registerTitle')}
            </button>
          </div>

          {/* Subtitle */}
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {mode === 'login' ? t('auth.loginSubtitle') : t('auth.registerSubtitle')}
          </p>
        </div>

        <div className="px-6 pb-6 space-y-4">
          {/* Google Sign In — chỉ hiện ở tab Đăng nhập */}
          {mode === 'login' && (
            <>
              <button
                type="button"
                onClick={handleGoogleSignIn}
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-3 py-2.5 px-4 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Chrome className="w-4 h-4 text-[#4285F4]" />
                {t('auth.continueWithGoogle')}
              </button>

              {/* Divider */}
              <div className="relative flex items-center gap-3">
                <div className="flex-1 border-t border-gray-200 dark:border-gray-700" />
                <span className="text-xs text-gray-400 dark:text-gray-500 font-medium">{t('auth.or')}</span>
                <div className="flex-1 border-t border-gray-200 dark:border-gray-700" />
              </div>
            </>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2.5 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-xl px-3.5 py-2.5">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleEmailAuth} className="space-y-3">
            {/* Name — chỉ hiện khi register */}
            {mode === 'register' && (
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={t('auth.namePlaceholder')}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500/30 focus:border-orange-400 transition-colors"
                />
              </div>
            )}

            {/* Email */}
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="email"
                placeholder={t('auth.emailPlaceholder')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500/30 focus:border-orange-400 transition-colors"
              />
            </div>

            {/* Password */}
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder={mode === 'register' ? t('auth.passwordRegisterPlaceholder') : t('auth.passwordPlaceholder')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                className="w-full pl-10 pr-10 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500/30 focus:border-orange-400 transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-60 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg, #f97316, #ea580c)' }}
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                mode === 'login' ? t('auth.loginButton') : t('auth.registerButton')
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}
