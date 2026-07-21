-- =====================================================
-- Migration: Thêm bảng Chat Sessions & Messages
-- Chạy file này trong Supabase SQL Editor
-- (Đã chạy auth-schema.sql phiên bản trước rồi)
-- =====================================================

-- Bảng phiên chat của từng user
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES "user"(id) ON DELETE SET NULL,
    title TEXT NOT NULL DEFAULT 'Cuộc trò chuyện mới',
    summary TEXT NOT NULL DEFAULT '',
    turn_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at DESC);

-- Bảng tin nhắn trong mỗi phiên chat
CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    context_used JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at);

-- Bảng user_files (nếu chưa có)
CREATE TABLE IF NOT EXISTS user_files (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    public_url TEXT,
    size_bytes BIGINT,
    mime_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_files_user_id ON user_files(user_id);

-- Bảng chat_feedbacks (nếu chưa có)
CREATE TABLE IF NOT EXISTS chat_feedbacks (
    id SERIAL PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,
    session_id TEXT NOT NULL,
    user_query TEXT,
    ai_response TEXT,
    context_used JSONB,
    feedback_type SMALLINT NOT NULL,
    reason TEXT,
    comment TEXT,
    model_used TEXT,
    user_id TEXT REFERENCES "user"(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
