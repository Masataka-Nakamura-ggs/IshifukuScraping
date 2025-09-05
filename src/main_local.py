#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石福金属興業スクレイピングツール - ローカル実行用メインスクリプト

"""

import argparse
import sys
from pathlib import Path

from ishifuku import get_config, setup_logging
from ishifuku.core import create_gold_price_scraper

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(description="Ishifuku Scraper")
    parser.add_argument(
        "--multi",
        action="store_true",
        help="金 + コイン各サイズを取得し新フォーマットCSVへ保存",
    )
    args = parser.parse_args()

    config = get_config("local")
    setup_logging(config.storage)

    try:
        mode_msg = "複数商品（金+コイン）" if args.multi else "金"
        print(f"石福金属興業から{mode_msg}の価格を取得します...")
        with create_gold_price_scraper("local", config) as scraper:
            if args.multi:
                result = scraper.scrape_all_and_save()
            else:
                result = scraper.scrape_and_save()

        if result.get("success"):
            print("処理が正常に完了しました。")
            print(f"取得日時: {result['datetime_str']}")
            if args.multi:
                for p in result["products"]:
                    print(f" - {p.product_name}: {p.price}")
            else:
                print(f"金の小売価格: {result['gold_price']}円/g")
            print(f"保存ファイル: {result['filepath']}")
        else:
            print(f"エラーが発生しました: {result.get('error')}")
            print("エラー処理が完了しました。")
    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
