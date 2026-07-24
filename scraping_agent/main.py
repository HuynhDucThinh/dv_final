"""
Car Info Collector — CLI entry point.

Thu thập thông tin chi tiết về xe ô tô từ bất kỳ URL nào.

Usage:
    python main.py "https://bonbanh.com/xe-porsche-..."
    python main.py "https://oto.com.vn/..." --output xe_info.json
    python main.py "https://www.caranddriver.com/..." --llm openai
    python main.py --help
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix Windows cp1252 encoding — allow Unicode symbols in print statements
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='python main.py',
        description='Car Info Collector — Thu thập thông tin xe ô tô từ bất kỳ URL nào',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "https://bonbanh.com/xe-porsche-macan-2022"
  python main.py "https://oto.com.vn/..." --output xe_info.json
  python main.py "https://www.caranddriver.com/porsche/911" --llm openai

Supported LLM providers (for unknown sites, set matching key in .env):
  openai   ->  OPENAI_API_KEY   (best quality)
  google   ->  GOOGLE_API_KEY   (good quality)
  groq     ->  GROQ_API_KEY     (free tier, rate-limited)
        """,
    )

    parser.add_argument(
        'url',
        help='URL trang xe cần thu thập thông tin (bonbanh.com, oto.com.vn, caranddriver.com, ...)',
    )
    parser.add_argument(
        '--output',
        '-o',
        default=None,
        metavar='FILE',
        help='Đường dẫn file output. Mặc định: car_info_YYYYMMDD_HHMMSS.json',
    )
    parser.add_argument(
        '--format',
        '-f',
        choices=['csv', 'json'],
        default='json',
        help='Định dạng output (mặc định: json)',
    )
    parser.add_argument(
        '--llm',
        choices=['auto', 'openai', 'google', 'groq'],
        default='auto',
        metavar='PROVIDER',
        help='LLM provider dùng cho site không rõ: auto | openai | google | groq (mặc định: auto)',
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Chạy browser ẩn (không hiện cửa sổ)',
    )

    return parser.parse_args()


def print_banner(url: str, output: str, fmt: str, llm: str, headless: bool) -> None:
    bar = '=' * 60
    print(f'\n{bar}')
    print('  Car Info Collector')
    print(bar)
    print(f'  URL      : {url}')
    print(f'  Output   : {output}')
    print(f'  Format   : {fmt.upper()}')
    print(f'  LLM      : {llm}')
    print(f'  Headless : {headless}')
    print(bar)
    print('  Đang thu thập thông tin xe...\n')


async def run(args: argparse.Namespace) -> int:
    from scraper.dispatcher import scrape

    return await scrape(
        url=args.url,
        output_path=args.output,
        fmt=args.format,
        max_reviews=1,          # không cần max cho xe, chỉ cần 1 record
        llm_provider=args.llm,
        headless=args.headless,
        filter_mode='all',
    )


def main() -> None:
    args = parse_args()

    # Build default output filename
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'car_info_{timestamp}.{args.format}'

    print_banner(
        url=args.url,
        output=args.output,
        fmt=args.format,
        llm=args.llm,
        headless=args.headless,
    )

    try:
        total = asyncio.run(run(args))
    except ValueError as e:
        print(f'\nConfiguration error: {e}')
        sys.exit(1)
    except KeyboardInterrupt:
        print('\n\nStopped by user.')
        output_abs = os.path.abspath(args.output)
        if Path(args.output).exists():
            print(f'Partial data saved to: {output_abs}')
        sys.exit(0)
    except Exception as e:
        print(f'\nUnexpected error: {e}')
        raise

    # Final summary
    bar = '=' * 60
    print(f'\n{bar}')
    print('  Thu thập hoàn tất!')
    print(bar)
    if total > 0:
        print(f'  Kết quả  : Đã lưu thông tin xe')
    else:
        print(f'  Kết quả  : Không lấy được dữ liệu')
    print(f'  File     : {os.path.abspath(args.output)}')
    print(f'{bar}\n')


if __name__ == '__main__':
    main()
