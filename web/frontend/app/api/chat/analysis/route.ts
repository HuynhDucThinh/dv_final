import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

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

    // Thêm X-User-Id để backend biết user nào đang gửi
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    try {
      const session = await auth.api.getSession({ headers: req.headers });
      if (session?.user?.id) {
        headers['X-User-Id'] = session.user.id;
      }
    } catch {
      // Guest mode — không có session
    }

    const backendRes = await fetch(targetUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: req.signal,
    });

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
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        Connection: 'keep-alive',
      },
    });
  } catch (error: unknown) {
    const details = error instanceof Error ? error.message : 'Unknown proxy error';
    return NextResponse.json({ error: 'Backend connection error', details }, { status: 502 });
  }
}
