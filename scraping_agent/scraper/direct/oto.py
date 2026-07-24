import re
import json
import httpx
from bs4 import BeautifulSoup
from datetime import datetime


class OtoScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
        }

    async def run(self, url: str, output_path: str, fmt: str = "json", max_reviews: int = 1, progress_callback=None) -> int:
        print(f"  [Oto] Fetching {url}...")

        async with httpx.AsyncClient(headers=self.headers, verify=False, timeout=30.0) as client:
            response = await client.get(url)

        if response.status_code != 200:
            print(f"  [Oto] HTTP Error {response.status_code}")
            return 0

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Khu vực chính của trang detail ---
        box = soup.find('div', id='box-detail') or soup

        # Tên xe
        h1 = box.find('h1')
        title_text = re.sub(r'\s+', ' ', h1.text.strip()) if h1 else "N/A"

        # Giá — span.price bên trong div#box-detail
        price_span = box.find('span', class_='price')
        price = re.sub(r'\s+', ' ', price_span.text.strip()) if price_span else "N/A"

        # Thông số kỹ thuật — ul.list-info (có 2 ul: cột trái .pr và cột phải .pl)
        specs = {}
        for ul in box.find_all('ul', class_='list-info'):
            for li in ul.find_all('li'):
                # Text dạng "Năm SX: |  2020" hoặc "Km đã đi: |  72.000 km"
                parts = [p.strip() for p in li.get_text(separator='|').split('|') if p.strip()]
                if len(parts) >= 2:
                    key = parts[0].rstrip(':').strip()
                    val = parts[1].strip()
                    if key and val:
                        specs[key] = val
                elif len(parts) == 1 and ':' in parts[0]:
                    k, _, v = parts[0].partition(':')
                    if k.strip() and v.strip():
                        specs[k.strip()] = v.strip()

        # Mô tả — div.description
        desc_div = box.find('div', class_='description') or box.find('div', class_='box-content-c')
        desc = re.sub(r'\s+', ' ', desc_div.text.strip()) if (desc_div and desc_div.text.strip()) else ""

        # Liên hệ
        contact = {}
        seller_el = box.find('span', class_='seller-name')
        if seller_el:
            contact['Ten'] = re.sub(r'\s+', ' ', seller_el.text.strip())
        phone_el = box.find('a', class_='btn-call') or box.find('span', class_='phone')
        if phone_el:
            contact['Dien thoai'] = phone_el.text.strip()

        car_info = {
            "ten_xe": title_text,
            "gia":    price,
            "thong_so_ky_thuat": specs,
            "lien_he": contact,
            "mo_ta":  desc,
            "nguon":  url,
            "thoi_gian": datetime.now().isoformat(),
        }

        print(f"  [Oto] OK: {title_text} | {price} | specs={len(specs)}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([car_info], f, ensure_ascii=False, indent=2)

        return 1
