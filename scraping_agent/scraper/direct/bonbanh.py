import re
import json
import httpx
from bs4 import BeautifulSoup
from datetime import datetime


class BonbanhScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def run(self, url: str, output_path: str, fmt: str = "json", max_reviews: int = 1, progress_callback=None) -> int:
        print(f"  [Bonbanh] Fetching {url}...")

        async with httpx.AsyncClient(headers=self.headers, verify=False, timeout=30.0) as client:
            response = await client.get(url)

        if response.status_code != 200:
            print(f"  [Bonbanh] HTTP Error {response.status_code}")
            return 0

        soup = BeautifulSoup(response.text, 'html.parser')

        # Tên xe
        title_h1 = soup.find('h1')
        title_text = re.sub(r'\s+', ' ', title_h1.text.strip()).strip() if title_h1 else "N/A"

        # Giá
        price_tag = soup.find('span', class_='price-value') or soup.find('div', class_='price')
        price = price_tag.text.strip() if price_tag else "N/A"

        # Thông số kỹ thuật
        specs = {}
        for row in soup.find_all('div', class_='row'):
            label_tag = row.find('label')
            value_tag = row.find('span', class_='inp')
            if label_tag and value_tag:
                key = label_tag.text.strip().replace(':', '')
                val = value_tag.text.strip()
                if key and val:
                    specs[key] = val

        # Mô tả
        desc_div = soup.find('div', class_='des_txt')
        desc = re.sub(r'\s+', ' ', desc_div.text.strip()).strip() if desc_div else ""

        # Liên hệ
        contact = {}
        contact_box = soup.find('div', class_='contact-txt')
        if contact_box:
            name = contact_box.find('span', class_='cname')
            phone = contact_box.find('span', class_='cphone')
            address = contact_box.find('div', class_='caddress')
            if name:    contact['Tên'] = name.text.strip()
            if phone:   contact['Điện thoại'] = phone.text.strip()
            if address: contact['Địa chỉ'] = address.text.strip()

        car_info = {
            "ten_xe": title_text,
            "gia":    price,
            "thong_so_ky_thuat": specs,
            "lien_he": contact,
            "mo_ta":  desc,
            "nguon":  url,
            "thoi_gian": datetime.now().isoformat(),
        }

        print(f"  [Bonbanh] OK: {title_text}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([car_info], f, ensure_ascii=False, indent=2)

        return 1
