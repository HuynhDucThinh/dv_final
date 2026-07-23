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

    const backendRes = await fetch(targetUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    const data = await backendRes.json();
    return NextResponse.json(data, { status: backendRes.status });
  } catch {
    // Trả về object rỗng khi backend chưa sẵn sàng — không crash UI
    return NextResponse.json({}, { status: 200 });
  }
}
