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

async function getAuthHeaders(req: NextRequest): Promise<Record<string, string>> {
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
    if (session?.user?.id) headers['X-User-Id'] = session.user.id;
  } catch { /* guest */ }
  return headers;
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const backendBase = getBackendUrl(req.url);
    const id = (await params).id;
    const targetUrl = `${backendBase}/chat/session/${id}`;
    const backendRes = await fetch(targetUrl, {
      method: 'DELETE',
      headers: await getAuthHeaders(req),
    });
    if (!backendRes.ok) {
      const err = await backendRes.json().catch(() => ({}));
      return NextResponse.json(
        { error: 'Backend error', details: err.detail || `Status: ${backendRes.status}` },
        { status: backendRes.status },
      );
    }
    return NextResponse.json({ success: true });
  } catch (error: unknown) {
    const details = error instanceof Error ? error.message : 'Unknown proxy error';
    return NextResponse.json({ error: 'Backend connection error', details }, { status: 502 });
  }
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const backendBase = getBackendUrl(req.url);
    const id = (await params).id;
    const body = await req.json();
    const targetUrl = `${backendBase}/chat/session/${id}`;
    const backendRes = await fetch(targetUrl, {
      method: 'PATCH',
      headers: await getAuthHeaders(req),
      body: JSON.stringify(body),
    });
    if (!backendRes.ok) {
      const err = await backendRes.json().catch(() => ({}));
      return NextResponse.json(
        { error: 'Backend error', details: err.detail || `Status: ${backendRes.status}` },
        { status: backendRes.status },
      );
    }
    return NextResponse.json({ success: true });
  } catch (error: unknown) {
    const details = error instanceof Error ? error.message : 'Unknown proxy error';
    return NextResponse.json({ error: 'Backend connection error', details }, { status: 502 });
  }
}
