import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { createClient } from '@supabase/supabase-js';

// Supabase admin client (service role — bypass RLS)
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { persistSession: false } }
);

const BUCKET = 'user-uploads';
const MAX_SIZE_BYTES = 50 * 1024 * 1024; // 50MB
const ALLOWED_MIME = [
  'image/jpeg', 'image/png', 'image/webp', 'image/gif',
  'application/pdf',
  'text/plain',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
];

async function extractText(buffer: Buffer, mimeType: string, filename: string): Promise<string | null> {
  try {
    if (mimeType === 'text/plain') {
      return buffer.toString('utf-8').slice(0, 50000); // max 50k chars
    }

    if (
      mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
      mimeType === 'application/msword'
    ) {
      const mammoth = (await import('mammoth')).default;
      const result = await mammoth.extractRawText({ buffer });
      return result.value.slice(0, 50000);
    }

    if (mimeType === 'application/pdf') {
      const pdfParse = (await import('pdf-parse')).default;
      const data = await pdfParse(buffer);
      return data.text.slice(0, 50000);
    }
  } catch (err) {
    console.error(`[File Extract] Failed to extract text from ${filename}:`, err);
  }
  return null;
}

// POST /api/files — upload file
export async function POST(req: NextRequest) {
  try {
    const sessionResult = await Promise.race([
      auth.api.getSession({ headers: req.headers }),
      new Promise<null>((_, reject) =>
        setTimeout(() => reject(new Error('auth timeout')), 5000)
      ),
    ]);
    const session = (
      sessionResult &&
      typeof sessionResult === 'object' &&
      'user' in sessionResult
    ) ? sessionResult : null;
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    const userId = session.user.id;

    const formData = await req.formData();
    const file = formData.get('file') as File | null;

    if (!file) return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    if (file.size > MAX_SIZE_BYTES) return NextResponse.json({ error: 'File too large (max 50MB)' }, { status: 413 });
    if (!ALLOWED_MIME.includes(file.type)) {
      return NextResponse.json({ error: `File type not allowed: ${file.type}` }, { status: 415 });
    }

    const ext = file.name.split('.').pop()?.toLowerCase() || 'bin';
    const storagePath = `${userId}/${Date.now()}-${Math.random().toString(36).slice(2)}.${ext}`;

    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // Upload to Supabase Storage
    const { data: uploadData, error: uploadError } = await supabaseAdmin.storage
      .from(BUCKET)
      .upload(storagePath, buffer, {
        contentType: file.type,
        cacheControl: '3600',
        upsert: false,
      });

    if (uploadError) {
      console.error('[Files API] Upload error:', uploadError.message);
      return NextResponse.json({ error: 'Storage upload failed', details: uploadError.message }, { status: 500 });
    }

    const { data: urlData } = supabaseAdmin.storage.from(BUCKET).getPublicUrl(uploadData.path);
    const publicUrl = urlData.publicUrl;

    // Extract text for non-image files
    const extractedText = file.type.startsWith('image/') ? null : await extractText(buffer, file.type, file.name);

    // Save metadata to DB
    const { data: dbRecord, error: dbError } = await supabaseAdmin
      .from('user_files')
      .insert({
        user_id: userId,
        filename: storagePath.split('/').pop()!,
        original_name: file.name,
        storage_path: storagePath,
        public_url: publicUrl,
        size_bytes: file.size,
        mime_type: file.type,
        extracted_text: extractedText,
      })
      .select()
      .single();

    if (dbError) {
      console.error('[Files API] DB error:', dbError.message);
      // File is uploaded but not recorded — try to delete orphan
      await supabaseAdmin.storage.from(BUCKET).remove([storagePath]);
      return NextResponse.json({ error: 'Failed to save file record', details: dbError.message }, { status: 500 });
    }

    return NextResponse.json({
      id: dbRecord.id,
      originalName: file.name,
      publicUrl,
      mimeType: file.type,
      sizeBytes: file.size,
      extractedText: extractedText?.slice(0, 200), // preview only
      hasText: !!extractedText,
      createdAt: dbRecord.created_at,
    });
  } catch (error) {
    console.error('[Files API] Unexpected error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// GET /api/files — list user's files
export async function GET(req: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: req.headers });
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(req.url);
    const filter = searchParams.get('filter') || 'all'; // all | images | files

    let query = supabaseAdmin
      .from('user_files')
      .select('id, original_name, public_url, size_bytes, mime_type, created_at, has_text:extracted_text')
      .eq('user_id', session.user.id)
      .order('created_at', { ascending: false });

    if (filter === 'images') {
      query = query.like('mime_type', 'image/%');
    } else if (filter === 'files') {
      query = query.not('mime_type', 'like', 'image/%');
    }

    const { data, error } = await query;

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    const files = (data || []).map(f => ({
      ...f,
      hasText: !!f.has_text,
      has_text: undefined,
    }));

    return NextResponse.json(files);
  } catch (error) {
    console.error('[Files API] List error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
