/**
 * Supabase Client — dùng cho Storage (upload file/ảnh)
 * Không dùng cho auth (Better Auth đảm nhiệm)
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
// Hỗ trợ cả format mới (sb_publishable_...) lẫn format cũ (eyJ...)
const supabaseKey =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Client-side: dùng publishable/anon key (bị giới hạn bởi RLS)
export const supabase = createClient(supabaseUrl, supabaseKey);

// Upload file lên Supabase Storage
export async function uploadUserFile(
  userId: string,
  file: File,
  bucket: string = 'user-uploads'
): Promise<{ path: string; url: string } | null> {
  const ext = file.name.split('.').pop();
  const filename = `${userId}/${Date.now()}-${Math.random().toString(36).slice(2)}.${ext}`;

  const { data, error } = await supabase.storage
    .from(bucket)
    .upload(filename, file, {
      cacheControl: '3600',
      upsert: false,
    });

  if (error) {
    console.error('[Supabase Storage] Upload error:', error.message);
    return null;
  }

  const { data: urlData } = supabase.storage.from(bucket).getPublicUrl(data.path);

  return {
    path: data.path,
    url: urlData.publicUrl,
  };
}

// Xóa file khỏi Supabase Storage
export async function deleteUserFile(
  path: string,
  bucket: string = 'user-uploads'
): Promise<boolean> {
  const { error } = await supabase.storage.from(bucket).remove([path]);
  if (error) {
    console.error('[Supabase Storage] Delete error:', error.message);
    return false;
  }
  return true;
}
