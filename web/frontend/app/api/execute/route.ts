import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

// Tăng thời gian tối đa cho route này lên 5 phút
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
    const targetUrl = `${backendBase}/api/analysis/execute`;

    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    try {
      const session = await auth.api.getSession({ headers: req.headers });
      if (session?.user?.id) {
        headers['X-User-Id'] = session.user.id;
      }
    } catch {
      // Bỏ qua lỗi auth (guest mode)
    }

    // Tăng timeout lên 4 phút (240 giây) để chờ code Python chạy xong
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 240_000);

    try {
      const backendRes = await fetch(targetUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!backendRes.ok) {
        const errorText = await backendRes.text();
        return NextResponse.json(
          { error: `Backend error: ${backendRes.status}`, details: errorText },
          { status: backendRes.status }
        );
      }

      const data = await backendRes.json();
      return NextResponse.json(data);
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError?.name === 'AbortError') {
        return NextResponse.json(
          { success: false, error: 'Thời gian chờ thực thi code đã vượt quá 4 phút. Vui lòng rút gọn hoặc tối ưu đoạn code.', stdout: '', stderr: '', images: [] },
          { status: 504 }
        );
      }
      throw fetchError;
    }
  } catch (error) {
    console.error('Execute API Error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal Server Error', details: error instanceof Error ? error.message : String(error), stdout: '', stderr: '', images: [] },
      { status: 500 }
    );
  }
}
