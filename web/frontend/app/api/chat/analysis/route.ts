import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

// Tăng thời gian tối đa lên 5 phút cho streaming
export const maxDuration = 300;

function getBackendUrl(reqUrl: string): string {
  let base = process.env.BACKEND_URL || 'http://localhost:8000';
  if (base.startsWith('/')) {
    const { origin } = new URL(reqUrl);
    base = `${origin}${base}`;
  }
  return base.replace(/\/+$/, '');
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const backendBase = getBackendUrl(req.url);
    const targetUrl = `${backendBase}/api/analysis/chat/stream`;

    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    try {
      const session = await auth.api.getSession({ headers: req.headers });
      if (session?.user?.id) {
        headers['X-User-Id'] = session.user.id;
      }
    } catch {
      // Guest mode — không có session
    }

    // Dùng AbortController độc lập (KHÔNG dùng req.signal trực tiếp)
    // để tránh Next.js tự abort kết nối khi streaming chưa xong
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 280_000); // 4.5 phút

    let backendRes: Response;
    try {
      backendRes = await fetch(targetUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
    } catch (fetchErr: any) {
      clearTimeout(timeoutId);
      const details = fetchErr instanceof Error ? fetchErr.message : String(fetchErr);
      return NextResponse.json({ error: 'Backend connection error', details }, { status: 502 });
    }

    if (!backendRes.ok) {
      const err = await backendRes.json().catch(() => ({}));
      return NextResponse.json(
        { error: 'Backend error', details: err.detail || `Status: ${backendRes.status}` },
        { status: backendRes.status },
      );
    }

    return new NextResponse(backendRes.body, {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive',
        'Transfer-Encoding': 'chunked',
      },
    });
  } catch (error: unknown) {
    const details = error instanceof Error ? error.message : 'Unknown proxy error';
    return NextResponse.json({ error: 'Backend connection error', details }, { status: 502 });
  }
}
