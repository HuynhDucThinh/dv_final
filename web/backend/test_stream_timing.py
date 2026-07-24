"""
Test streaming THẬT: dùng aiohttp (non-blocking) để đo chính xác thời điểm
mỗi SSE chunk đến. Mục đích: xác nhận backend flush từng chunk riêng biệt.
"""
import asyncio
import time
import json
import aiohttp

async def test_stream():
    url = "http://localhost:8000/api/analysis/chat/stream"
    payload = {
        "messages": [{"role": "user", "content": "cho tôi xem tổng quan dashboard"}],
        "model": "qwen2.5:7b-instruct",
        "session_id": f"test-stream-{int(time.time())}",
        "streaming": True,
    }
    
    t0 = time.time()
    print(f"[{0:.0f}ms] Sending...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            print(f"[{(time.time()-t0)*1000:.0f}ms] Status: {resp.status}")
            
            chunk_count = 0
            buf = ""
            # Read byte by byte effectively via content.iter_any()
            async for raw_bytes in resp.content.iter_any():
                buf += raw_bytes.decode('utf-8', errors='replace')
                while '\n' in buf:
                    line, buf = buf.split('\n', 1)
                    line = line.strip()
                    if not line or not line.startswith('data: '):
                        continue
                    
                    chunk_count += 1
                    elapsed = (time.time() - t0) * 1000
                    
                    try:
                        data = json.loads(line[6:])
                        typ = data.get('type', '?')
                        content = data.get('content', '')
                        preview = content[:60].replace('\n', '\\n')
                        # Print first 10 chunks, then every 50th
                        if chunk_count <= 10 or chunk_count % 50 == 0 or typ == 'done':
                            print(f"[{elapsed:7.0f}ms] #{chunk_count:03d} type={typ:5s} len={len(content):4d} | {preview}")
                    except:
                        if chunk_count <= 10:
                            print(f"[{elapsed:7.0f}ms] #{chunk_count:03d} RAW: {line[:80]}")
    
    total_ms = (time.time() - t0) * 1000
    print(f"\n[{total_ms:.0f}ms] DONE - {chunk_count} total chunks")

asyncio.run(test_stream())
