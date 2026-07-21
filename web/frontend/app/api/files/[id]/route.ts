import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { createClient } from '@supabase/supabase-js';

const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { persistSession: false } }
);

const BUCKET = 'user-uploads';

// GET /api/files/[id] — get extracted text for a file
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await auth.api.getSession({ headers: req.headers });
    if (!session?.user?.id) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const { id } = await params;
    const { data, error } = await supabaseAdmin
      .from('user_files')
      .select('extracted_text, original_name, mime_type')
      .eq('id', id)
      .eq('user_id', session.user.id)
      .single();

    if (error || !data) return NextResponse.json({ error: 'File not found' }, { status: 404 });

    return NextResponse.json({
      extractedText: data.extracted_text,
      originalName: data.original_name,
      mimeType: data.mime_type,
    });
  } catch {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// DELETE /api/files/[id] — delete file from Storage + DB
export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await auth.api.getSession({ headers: req.headers });
    if (!session?.user?.id) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const { id } = await params;

    // Get file record first to get storage path
    const { data: file, error: fetchErr } = await supabaseAdmin
      .from('user_files')
      .select('storage_path')
      .eq('id', id)
      .eq('user_id', session.user.id)
      .single();

    if (fetchErr || !file) return NextResponse.json({ error: 'File not found' }, { status: 404 });

    // Delete from storage
    await supabaseAdmin.storage.from(BUCKET).remove([file.storage_path]);

    // Delete from DB
    await supabaseAdmin.from('user_files').delete().eq('id', id);

    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
