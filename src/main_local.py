#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石福金属興業スクレイピングツール - ローカル実行用メインスクリプト

リファクタリング後の新しいアーキテクチャを使用したローカル実行用スクリプト
"""

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
    # 設定を取得
    config = get_config("local")

    # ログ設定を初期化
    setup_logging(config.storage)

    try:
        print("石福金属興業から金の価格を取得します...")

        # スクレイパーを作成して実行
        with create_gold_price_scraper("local", config) as scraper:
            result = scraper.scrape_and_save()

        if result["success"]:
            print("処理が正常に完了しました。")
            print(f"取得日時: {result['datetime_str']}")
            print(f"金の小売価格: {result['gold_price']}円/g")
            print(f"保存ファイル: {result['filepath']}")
        else:
            print(f"エラーが発生しました: {result['error']}")
            print("エラー処理が完了しました。")

    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
