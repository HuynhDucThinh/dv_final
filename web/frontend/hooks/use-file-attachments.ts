'use client';

import { useState, useCallback } from 'react';

export interface AttachedFile {
  id: string;           // local temp ID
  dbId?: string;        // ID từ DB sau khi upload
  file: File;
  previewUrl?: string;  // Object URL cho ảnh
  publicUrl?: string;   // Supabase public URL
  extractedText?: string;
  hasText: boolean;
  status: 'uploading' | 'done' | 'error';
  error?: string;
}

export function useFileAttachments() {
  const [attachments, setAttachments] = useState<AttachedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const addFiles = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);

    // Tạo entries tạm với status uploading
    const tempEntries: AttachedFile[] = fileArray.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      file,
      previewUrl: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
      hasText: false,
      status: 'uploading' as const,
    }));

    setAttachments(prev => [...prev, ...tempEntries]);
    setIsUploading(true);

    // Upload mỗi file
    await Promise.all(
      tempEntries.map(async (entry) => {
        try {
          const formData = new FormData();
          formData.append('file', entry.file);

          const res = await fetch('/api/files', {
            method: 'POST',
            body: formData,
          });

          if (!res.ok) {
            const err = await res.json().catch(() => ({ error: 'Upload failed' }));
            setAttachments(prev =>
              prev.map(a => a.id === entry.id ? { ...a, status: 'error', error: err.error } : a)
            );
            return;
          }

          const data = await res.json();
          setAttachments(prev =>
            prev.map(a => a.id === entry.id ? {
              ...a,
              dbId: data.id,
              publicUrl: data.publicUrl,
              hasText: data.hasText,
              extractedText: data.hasText ? undefined : undefined, // full text fetched on submit
              status: 'done',
            } : a)
          );
        } catch {
          setAttachments(prev =>
            prev.map(a => a.id === entry.id ? { ...a, status: 'error', error: 'Network error' } : a)
          );
        }
      })
    );

    setIsUploading(false);
  }, []);

  const removeAttachment = useCallback((id: string) => {
    setAttachments(prev => {
      const entry = prev.find(a => a.id === id);
      if (entry?.previewUrl) URL.revokeObjectURL(entry.previewUrl);
      return prev.filter(a => a.id !== id);
    });
  }, []);

  const clearAttachments = useCallback(() => {
    setAttachments(prev => {
      prev.forEach(a => { if (a.previewUrl) URL.revokeObjectURL(a.previewUrl); });
      return [];
    });
  }, []);

  // Lấy full extracted text cho các file có text (gọi trước khi submit)
  const getFullTexts = useCallback(async (): Promise<Map<string, string>> => {
    const result = new Map<string, string>();
    const textFiles = attachments.filter(a => a.hasText && a.dbId && a.status === 'done');

    await Promise.all(
      textFiles.map(async (a) => {
        try {
          const res = await fetch(`/api/files/${a.dbId}`);
          if (res.ok) {
            const data = await res.json();
            if (data.extractedText) result.set(a.id, data.extractedText);
          }
        } catch { /* ignore */ }
      })
    );

    return result;
  }, [attachments]);

  return {
    attachments,
    isUploading,
    addFiles,
    removeAttachment,
    clearAttachments,
    getFullTexts,
  };
}
