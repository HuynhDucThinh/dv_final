import { NextRequest, NextResponse } from 'next/server';

function getBackendUrl(reqUrl: string): string {
  let base = process.env.BACKEND_URL || 'http://localhost:8000';
  if (base.startsWith('/')) {
    const { origin } = new URL(reqUrl);
    base = `${origin}${base}`;
  }
  return base.replace(/\/+$/, '');
}

// DELETE /api/execute/session/[id]
// → proxy DELETE /api/analysis/session/[id] trên backend
// Dùng để xóa Python namespace khi bắt đầu chat mới
export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: sessionId } = await params;
    const backendBase = getBackendUrl(req.url);
    const targetUrl = `${backendBase}/api/analysis/session/${encodeURIComponent(sessionId)}`;

    const backendRes = await fetch(targetUrl, { method: 'DELETE' });
    const data = await backendRes.json().catch(() => ({}));
    return NextResponse.json(data, { status: backendRes.status });
  } catch (error) {
    // Lỗi không block UI — trả về 200 để client không bị stuck
    return NextResponse.json({ cleared: false }, { status: 200 });
  }
}
