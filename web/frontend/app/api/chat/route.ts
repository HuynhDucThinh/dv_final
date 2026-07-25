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
    const streaming = body.streaming !== false;
    const targetUrl = `${backendBase}${streaming ? '/chat/stream' : '/chat'}`;

    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
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
      if (session?.user?.id) {
        headers['X-User-Id'] = session.user.id;
      }
    } catch {
      // Bỏ qua lỗi auth (guest mode)
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

    if (!streaming) {
      return new NextResponse(await backendRes.arrayBuffer(), {
        status: backendRes.status,
        headers: { 'Content-Type': backendRes.headers.get('content-type') || 'application/json' },
      });
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
    console.error('[Proxy Chat Error]', error);
    return NextResponse.json(
      { error: 'Backend connection error', details },
      { status: 502 },
    );
  }
}
