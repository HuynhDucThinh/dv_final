"""
dispatcher.py — Điều phối URL xe đến đúng scraper.

Level 1 — Direct Scraper (BeautifulSoup, không cần LLM):
  bonbanh.com, oto.com.vn → parse HTML trực tiếp, siêu nhanh

Level 2 — LLM Browser Agent (browser-use):
  Bất kỳ URL nào khác → AI điều khiển trình duyệt, đọc và trích xuất thông tin
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Level 1: Direct scrapers — không cần LLM, parse HTML trực tiếp
# ---------------------------------------------------------------------------

_DIRECT_SITES = {
    "bonbanh.com": "scraper.direct.bonbanh.BonbanhScraper",
    "oto.com.vn":  "scraper.direct.oto.OtoScraper",
}


def _get_direct_scraper(url: str):
    """Trả về class scraper nếu URL khớp site đã biết, ngược lại trả None."""
    import importlib
    for domain, cls_path in _DIRECT_SITES.items():
        if domain in url:
            mod_name, cls_name = cls_path.rsplit(".", 1)
            mod = importlib.import_module(mod_name)
            return getattr(mod, cls_name)
    return None


# ---------------------------------------------------------------------------
# Main dispatch function
# ---------------------------------------------------------------------------

async def scrape(
    url: str,
    output_path: str,
    fmt: str          = "json",
    max_reviews: int  = 1,
    llm_provider: str = "auto",
    headless: bool    = False,
    filter_mode: str  = "all",
    progress_callback = None
) -> int:
    """Điều phối URL đến đúng scraper. Trả về 1 nếu thành công, 0 nếu thất bại."""

    # -- Level 1: Direct scraper (nhanh nhất, không tốn API key)
    ScraperClass = _get_direct_scraper(url)
    if ScraperClass is not None:
        print(f"  [Dispatcher] Direct scraper: {ScraperClass.__name__}")
        scraper = ScraperClass()
        return await scraper.run(url, output_path, fmt, max_reviews, progress_callback=progress_callback)

    # -- Level 2: LLM Browser Agent (cho các site chưa có direct scraper)
    print(f"  [Dispatcher] Không có direct scraper → dùng LLM browser agent")
    try:
        from scraper.agent import scrape_reviews
        return await scrape_reviews(
            url=url,
            output_path=output_path,
            fmt=fmt,
            max_reviews=max_reviews,
            llm_provider=llm_provider,
            headless=headless,
        )
    except ModuleNotFoundError as e:
        print(f"\n  [Dispatcher] LLM Agent không khả dụng: {e}")
        return 0
