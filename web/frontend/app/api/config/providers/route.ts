import { NextRequest, NextResponse } from 'next/server';

function getBackendUrl(reqUrl: string): string {
  let base = process.env.BACKEND_URL || 'http://localhost:8000';
  if (base.startsWith('/')) {
    const { origin } = new URL(reqUrl);
    base = `${origin}${base}`;
  }
  return base.replace(/\/+$/, '');
}

// GET /api/config/providers → proxy → backend /api/config/providers
export async function GET(req: NextRequest) {
  try {
    const backendBase = getBackendUrl(req.url);
    const targetUrl = `${backendBase}/api/config/providers`;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000); // 5s timeout

    const backendRes = await fetch(targetUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
    });
    clearTimeout(timeout);

    const data = await backendRes.json();
    return NextResponse.json(data, { status: backendRes.status });
  } catch {
    // Trả về object rỗng khi backend chưa sẵn sàng hoặc timeout — không crash UI
    return NextResponse.json({}, { status: 200 });
  }
}

