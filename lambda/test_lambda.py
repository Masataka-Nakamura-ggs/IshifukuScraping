#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lambda関数のローカルテスト用スクリプト
"""

import json
import os
import sys
from unittest.mock import Mock

# Lambda関数をインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lambda_scrape_ishifuku import lambda_handler


def test_lambda_locally():
    """Lambda関数をローカルでテスト"""

    print("🧪 Lambda関数のローカルテストを開始...")

    # 環境変数を設定（テスト用）
    os.environ["S3_BUCKET"] = "test-ishifuku-bucket"
    os.environ["LOG_LEVEL"] = "INFO"

    # モックイベントとコンテキスト
    event = {"source": "test", "test": True}

    context = Mock()
    context.function_name = "test-ishifuku-scraper"
    context.function_version = "1"
    context.invoked_function_arn = (
        "arn:aws:lambda:ap-northeast-1:123456789012:function:test-ishifuku-scraper"
    )
    context.memory_limit_in_mb = "1024"
    context.remaining_time_in_millis = lambda: 300000  # 5分

    try:
        # Lambda関数を実行
        result = lambda_handler(event, context)

        print("\n✅ テスト実行完了!")
        print("📋 実行結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 結果の検証
        if result["statusCode"] == 200:
            body = json.loads(result["body"])
            if "data" in body and "gold_price" in body["data"]:
                print(f"\n💰 取得した金価格: {body['data']['gold_price']}円/g")
                print(f"📅 取得日時: {body['data']['datetime']}")
                return True
            else:
                print("\n⚠️  価格データが見つかりませんでした")
                return False
        else:
            print(f"\n❌ エラーが発生しました: {result}")
            return False

    except Exception as e:
        print(f"\n💥 例外が発生しました: {e}")
        return False


def test_price_extraction():
    """価格抽出機能の単体テスト"""
    from lambda_scrape_ishifuku import extract_price_from_text

    print("\n🔍 価格抽出機能のテスト...")

    test_cases = [
        ("17,530(+117)", 17530),
        ("16,800(-200)", 16800),
        ("15,000(+0)", 15000),
        ("  18,250  ", 18250),
        ("19,999", 19999),
        ("invalid", None),
        ("", None),
    ]

    all_passed = True
    for input_text, expected in test_cases:
        result = extract_price_from_text(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_text}' -> {result} (期待値: {expected})")
        if result != expected:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("🧪 石福金属興業スクレイパー Lambda テストスイート")
    print("=" * 50)

    # 価格抽出のテスト
    extraction_ok = test_price_extraction()

    print("\n" + "=" * 50)

    # 実際のスクレイピングテスト（Seleniumが必要）
    try:
        scraping_ok = test_lambda_locally()
    except ImportError as e:
        print(f"⚠️  Seleniumが利用できないため、スクレイピングテストをスキップ: {e}")
        scraping_ok = None

    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー:")
    print(f"価格抽出テスト: {'✅ PASS' if extraction_ok else '❌ FAIL'}")

    if scraping_ok is not None:
        print(f"スクレイピングテスト: {'✅ PASS' if scraping_ok else '❌ FAIL'}")
    else:
        print("スクレイピングテスト: ⏭️ SKIP")

    print("\n🎯 Lambda環境でのテストを行うには:")
    print("1. Chrome Lambda Layerを設定")
    print("2. S3バケットを作成")
    print("3. 環境変数を設定")
    print("4. AWS Lambda コンソールでテスト実行")
