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

export const dynamic = 'force-dynamic';

async function readSafeErrorBody(response: Response): Promise<string> {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    const payload = await response.json().catch(() => ({}));
    if (payload && typeof payload === 'object' && 'detail' in payload) {
      return String(payload.detail).slice(0, 240);
    }
    if (payload && typeof payload === 'object' && 'error' in payload) {
      return String(payload.error).slice(0, 240);
    }
    return `Status: ${response.status}`;
  }
  const text = await response.text().catch(() => '');
  return text ? text.slice(0, 240) : `Status: ${response.status}`;
}

export async function GET(req: NextRequest) {
  try {
    const backendBase = getBackendUrl(req.url);
    const targetUrl = `${backendBase}/chat/sessions`;

    // Lấy session từ Better Auth với timeout 5s — tránh treo khi Supabase chậm
    const headers: Record<string, string> = { 'Cache-Control': 'no-store' };
    try {
      const sessionResult = await Promise.race([
        auth.api.getSession({ headers: req.headers }),
        new Promise<null>((_, reject) =>
          setTimeout(() => reject(new Error('auth timeout')), 3000)
        ),
      ]);
      if (
        sessionResult &&
        typeof sessionResult === 'object' &&
        'user' in sessionResult &&
        sessionResult.user?.id
      ) {
        // Header nội bộ — chỉ Next.js server mới gửi được (backend không expose public)
        headers['X-User-Id'] = sessionResult.user.id;
      }
    } catch {
      // Timeout hoặc không có session — tiếp tục như guest
    }

    // Fetch backend với timeout 4s
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);

    const backendRes = await fetch(targetUrl, {
      method: 'GET',
      cache: 'no-store',
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!backendRes.ok) {
      const details = await readSafeErrorBody(backendRes);
      return NextResponse.json(
        { error: 'Backend error', details },
        { status: backendRes.status },
      );
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (error: unknown) {
    // Timeout hoặc lỗi kết nối → trả về mảng rỗng để UI tạo session mới ngay
    const details = error instanceof Error ? error.message : 'Unknown proxy error';
    console.warn('[sessions/route] Fallback to empty sessions:', details);
    return NextResponse.json([], { status: 200 });
  }
}
