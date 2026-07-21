-- =====================================================
-- Supabase Storage: Tạo bucket user-uploads
-- Chạy trong Supabase Dashboard > SQL Editor
-- =====================================================

-- Tạo bucket (nếu chưa có)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'user-uploads',
  'user-uploads',
  true,
  52428800,  -- 50MB limit
  ARRAY[
    'image/jpeg', 'image/png', 'image/webp', 'image/gif',
    'application/pdf',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
  ]
)
ON CONFLICT (id) DO NOTHING;

-- Policy: Cho phép authenticated users upload
CREATE POLICY "Authenticated users can upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'user-uploads');

-- Policy: Public read
CREATE POLICY "Public read access"
ON storage.objects FOR SELECT
USING (bucket_id = 'user-uploads');

-- Policy: Users can delete their folder
CREATE POLICY "Authenticated users can delete"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'user-uploads');

-- Đảm bảo bảng user_files đã có (nếu chưa chạy add-chat-tables.sql)
CREATE TABLE IF NOT EXISTS user_files (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL DEFAULT '',
    storage_path TEXT NOT NULL,
    public_url TEXT,
    size_bytes BIGINT,
    mime_type TEXT,
    extracted_text TEXT,  -- Nội dung text đã extract (cho PDF/DOCX/TXT)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_files_user_id ON user_files(user_id);
CREATE INDEX IF NOT EXISTS idx_user_files_created ON user_files(created_at DESC);
