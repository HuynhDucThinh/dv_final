'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Search, Grid3X3, List, Upload, Trash2, X, Eye,
  FileText, File, Image as ImageIcon, Calendar, HardDrive,
  Loader2, ImageOff, RefreshCw, ChevronLeft, Filter
} from 'lucide-react';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';

type FilterType = 'all' | 'images' | 'files';
type ViewType = 'list' | 'grid';

interface UserFile {
  id: string;
  original_name: string;
  public_url: string;
  size_bytes: number;
  mime_type: string;
  created_at: string;
  hasText: boolean;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatDate(dateStr: string, locale: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffDays === 0) return locale === 'vi' ? 'Hôm nay' : 'Today';
  if (diffDays === 1) return locale === 'vi' ? 'Hôm qua' : 'Yesterday';
  if (diffDays < 7) return locale === 'vi' ? `${diffDays} ngày trước` : `${diffDays} days ago`;

  return date.toLocaleDateString(locale === 'vi' ? 'vi-VN' : 'en-US', {
    day: 'numeric', month: 'short', year: diffDays > 365 ? 'numeric' : undefined
  });
}

function FileIcon({ mimeType, className }: { mimeType: string; className?: string }) {
  if (mimeType.startsWith('image/')) return <ImageIcon className={className} />;
  if (mimeType === 'application/pdf') return <FileText className={className} />;
  return <File className={className} />;
}

export default function LibraryPage() {
  const { t, i18n } = useTranslation();
  const locale = i18n.language;

  const [files, setFiles] = useState<UserFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<FilterType>('all');
  const [view, setView] = useState<ViewType>('list');
  const [search, setSearch] = useState('');
  const [lightbox, setLightbox] = useState<UserFile | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await fetch(`/api/files?filter=${filter}`);
      if (res.status === 401) {
        setError(locale === 'vi' ? 'Vui lòng đăng nhập để xem thư viện.' : 'Please sign in to view your library.');
        return;
      }
      if (!res.ok) throw new Error('Failed to fetch files');
      const data = await res.json();
      setFiles(Array.isArray(data) ? data : []);
    } catch {
      setError(locale === 'vi' ? 'Không thể tải danh sách file.' : 'Unable to load files.');
    } finally {
      setIsLoading(false);
    }
  }, [filter, locale]);

  useEffect(() => { fetchFiles(); }, [fetchFiles]);

  // Lightbox: close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') setLightbox(null); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);
    const uploads = Array.from(files).map(async (file) => {
      const fd = new FormData();
      fd.append('file', file);
      await fetch('/api/files', { method: 'POST', body: fd });
    });
    await Promise.all(uploads);
    setIsUploading(false);
    fetchFiles();
  };

  const handleDelete = async (id: string) => {
    if (deletingId) return;
    setDeletingId(id);
    try {
      await fetch(`/api/files/${id}`, { method: 'DELETE' });
      setFiles(prev => prev.filter(f => f.id !== id));
      if (lightbox?.id === id) setLightbox(null);
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = files.filter(f =>
    f.original_name.toLowerCase().includes(search.toLowerCase())
  );

  const TABS: { key: FilterType; label: string }[] = [
    { key: 'all', label: locale === 'vi' ? 'Tất cả' : 'All' },
    { key: 'images', label: locale === 'vi' ? 'Ảnh' : 'Images' },
    { key: 'files', label: locale === 'vi' ? 'Tệp' : 'Files' },
  ];

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
              {locale === 'vi' ? 'Thư viện' : 'Library'}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder={locale === 'vi' ? 'Tìm kiếm' : 'Search'}
                className="pl-9 pr-4 py-2 bg-gray-100 dark:bg-[#212121] border border-transparent focus:border-gray-300 dark:focus:border-white/10 rounded-full text-sm text-gray-800 dark:text-gray-200 focus:outline-none w-[200px] sm:w-[260px] transition-all"
              />
            </div>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*,.pdf,.txt,.doc,.docx"
              className="hidden"
              onChange={e => handleUpload(e.target.files)}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="flex items-center gap-2 bg-black text-white dark:bg-white dark:text-black px-4 py-2 rounded-full text-sm font-medium hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors disabled:opacity-60 shadow-sm"
            >
              {isUploading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /></>
              ) : (
                <><span>{locale === 'vi' ? 'Mới' : 'New'}</span> <span className="text-[10px] ml-1">▼</span></>
              )}
            </button>
          </div>
        </div>

        {/* Toolbar (Tabs & Views) */}
        <div className="flex items-center justify-between pb-3 mb-2">
          <div className="flex items-center gap-1">
            {TABS.map(tab => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  filter === tab.key
                    ? 'bg-gray-100 dark:bg-white/10 text-gray-900 dark:text-white'
                    : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1 text-gray-400">
            <button className="p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-white/10 transition-colors">
              <Filter className="w-4 h-4" />
            </button>
            <button
              onClick={() => setView('grid')}
              className={`p-1.5 rounded-md transition-colors ${view === 'grid' ? 'text-gray-900 dark:text-white bg-gray-100 dark:bg-white/10' : 'hover:bg-gray-100 dark:hover:bg-white/10'}`}
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setView('list')}
              className={`p-1.5 rounded-md transition-colors ${view === 'list' ? 'text-gray-900 dark:text-white bg-gray-100 dark:bg-white/10' : 'hover:bg-gray-100 dark:hover:bg-white/10'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* List Header */}
        {!isLoading && !error && filtered.length > 0 && view === 'list' && (
          <div className="grid grid-cols-[1fr_150px_100px_60px] items-center px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-white/10">
            <span>{locale === 'vi' ? 'Tên' : 'Name'}</span>
            <span>{locale === 'vi' ? 'Đã sửa đổi' : 'Modified'} ↓</span>
            <span>{locale === 'vi' ? 'Kích thước' : 'Size'}</span>
            <span></span>
          </div>
        )}

        {/* Content */}
        <div className="mt-1">
          {error && (
            <div className="text-center py-16 text-gray-400">
              <ImageOff className="w-12 h-12 mx-auto mb-3 opacity-40" />
              <p>{error}</p>
            </div>
          )}

          {isLoading && !error && (
            <div className="space-y-1">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-4 rounded-xl animate-pulse">
                  <div className="w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-700 flex-shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {!isLoading && !error && filtered.length === 0 && (
            <div className="text-center py-20">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gray-50 dark:bg-white/5 flex items-center justify-center">
                <File className="w-8 h-8 text-gray-300 dark:text-gray-600" />
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-200 mb-1">
                {locale === 'vi' ? 'Thư viện trống' : 'Library is empty'}
              </p>
            </div>
          )}

          {!isLoading && !error && filtered.length > 0 && view === 'list' && (
            <div className="flex flex-col">
              {filtered.map((file, i) => (
                <div
                  key={file.id}
                  className="grid grid-cols-[1fr_150px_100px_60px] items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors group border-b border-gray-50 dark:border-white/5 last:border-0 rounded-lg"
                >
                  {/* Name + icon */}
                  <div className="flex items-center gap-3 min-w-0 pr-4">
                    {file.mime_type.startsWith('image/') ? (
                      <div
                        className="w-7 h-7 rounded overflow-hidden flex-shrink-0 cursor-pointer bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                        onClick={() => setLightbox(file)}
                      >
                        <img src={file.public_url} alt={file.original_name} className="w-full h-full object-cover" />
                      </div>
                    ) : (
                      <div className={`w-7 h-7 rounded flex items-center justify-center flex-shrink-0 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-gray-700`}>
                        <FileIcon mimeType={file.mime_type} className="w-3.5 h-3.5 text-gray-500 dark:text-gray-400" />
                      </div>
                    )}
                    <button
                      onClick={() => file.mime_type.startsWith('image/') ? setLightbox(file) : window.open(file.public_url, '_blank')}
                      className="text-sm text-gray-700 dark:text-gray-200 hover:underline truncate"
                      title={file.original_name}
                    >
                      {file.original_name}
                    </button>
                  </div>

                  {/* Date */}
                  <div className="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">
                    {formatDate(file.created_at, locale)}
                  </div>

                  {/* Size */}
                  <div className="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">
                    {formatSize(file.size_bytes)}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleDelete(file.id)}
                      disabled={deletingId === file.id}
                      className="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                    >
                      {deletingId === file.id
                        ? <Loader2 className="w-4 h-4 animate-spin" />
                        : <Trash2 className="w-4 h-4" />
                      }
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Grid view */}
          {!isLoading && !error && filtered.length > 0 && view === 'grid' && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {filtered.map(file => (
                <div
                  key={file.id}
                  className="group relative bg-white dark:bg-[#212121] rounded-xl border border-gray-200/60 dark:border-white/10 overflow-hidden hover:border-gray-300 dark:hover:border-white/20 transition-all"
                >
                  {/* Preview */}
                  <div
                    className="aspect-square flex items-center justify-center cursor-pointer bg-gray-50 dark:bg-gray-800/50"
                    onClick={() => file.mime_type.startsWith('image/') ? setLightbox(file) : window.open(file.public_url, '_blank')}
                  >
                    {file.mime_type.startsWith('image/') ? (
                      <img src={file.public_url} alt={file.original_name} className="w-full h-full object-cover" />
                    ) : (
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-white dark:bg-gray-700 shadow-sm`}>
                        <FileIcon mimeType={file.mime_type} className="w-6 h-6 text-gray-400" />
                      </div>
                    )}
                  </div>

                  {/* Actions overlay */}
                  <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleDelete(file.id)}
                      disabled={deletingId === file.id}
                      className="p-1.5 bg-white/90 dark:bg-gray-900/90 rounded-md text-gray-500 hover:text-red-500 shadow-sm transition-colors"
                    >
                      {deletingId === file.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
                    </button>
                  </div>

                  {/* Name */}
                  <div className="px-3 py-2 border-t border-gray-100 dark:border-white/5">
                    <p className="text-xs font-medium text-gray-900 dark:text-gray-200 truncate" title={file.original_name}>
                      {file.original_name}
                    </p>
                    <p className="text-[10px] text-gray-500 mt-0.5">{formatDate(file.created_at, locale)} • {formatSize(file.size_bytes)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-[300] bg-black/90 flex items-center justify-center p-4 animate-in fade-in duration-200"
          onClick={() => setLightbox(null)}
        >
          <button
            className="absolute top-4 right-4 p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-full transition-colors"
            onClick={() => setLightbox(null)}
          >
            <X className="w-6 h-6" />
          </button>
          <div className="flex flex-col items-center gap-4 max-w-4xl max-h-[90vh]" onClick={e => e.stopPropagation()}>
            <img
              src={lightbox.public_url}
              alt={lightbox.original_name}
              className="max-w-full max-h-[85vh] object-contain"
            />
            <div className="flex items-center gap-4 text-sm text-white/70">
              <span className="font-medium text-white">{lightbox.original_name}</span>
              <span>{formatSize(lightbox.size_bytes)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
