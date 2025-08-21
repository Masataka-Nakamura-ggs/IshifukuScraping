#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lambda関数のローカルテスト用スクリプト（改良版）
"""

import json
import os
import sys
from unittest.mock import Mock, patch

# Lambda関数をインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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


def test_lambda_with_mock():
    """モックを使用したLambda関数のテスト"""
    
    print("\n🧪 Lambda関数のモックテストを開始...")
    
    # 環境変数を設定（テスト用）
    os.environ['S3_BUCKET'] = 'test-ishifuku-bucket'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    # モックイベントとコンテキスト
    event = {
        "source": "test",
        "test": True
    }
    
    context = Mock()
    context.function_name = "test-ishifuku-scraper"
    context.function_version = "1"
    context.invoked_function_arn = "arn:aws:lambda:ap-northeast-1:123456789012:function:test-ishifuku-scraper"
    context.memory_limit_in_mb = "1024"
    context.remaining_time_in_millis = lambda: 300000  # 5分
    
    # モックデータ
    mock_price_data = {
        'gold_price': 17530,
        'datetime': '2025-08-21 15:30:00',
        'source_url': 'https://www.ishifuku.co.jp/market/gold.php'
    }
    
    try:
        # Lambda関数をインポート（遅延インポート）
        from lambda_scrape_ishifuku import (lambda_handler, save_to_s3,
                                            scrape_gold_price_selenium)

        # スクレイピング関数をモック
        with patch('lambda_scrape_ishifuku.scrape_gold_price_selenium') as mock_scrape, \
             patch('lambda_scrape_ishifuku.save_to_s3') as mock_s3:
            
            # モック設定
            mock_scrape.return_value = mock_price_data
            mock_s3.return_value = True
            
            # Lambda関数を実行
            result = lambda_handler(event, context)
            
            print("\n✅ モックテスト実行完了!")
            print("📋 実行結果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 結果の検証
            if result['statusCode'] == 200:
                body = json.loads(result['body'])
                if 'data' in body and 'gold_price' in body['data']:
                    print(f"\n💰 モック金価格: {body['data']['gold_price']}円/g")
                    print(f"📅 取得日時: {body['data']['datetime']}")
                    print("🔍 モック関数の呼び出し確認:")
                    print(f"  - scrape_gold_price_selenium: {mock_scrape.called}")
                    print(f"  - save_to_s3: {mock_s3.called}")
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


def test_lambda_locally_with_local_chrome():
    """ローカルChromeを使用した実際のスクレイピングテスト"""
    
    print("\n🌐 ローカルChromeでの実スクレイピングテスト...")
    
    # 環境変数を設定（テスト用）
    os.environ['S3_BUCKET'] = 'test-ishifuku-bucket'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    try:
        # ローカル環境用にパッチを当てる
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from scrape_ishifuku import scrape_gold_price as local_scrape

        # ローカルのスクレイピング関数を使用
        result = local_scrape()
        
        if result:
            print("✅ ローカルスクレイピング成功!")
            print(f"💰 取得した金価格: {result.get('gold_price', 'N/A')}円/g")
            print(f"📅 取得日時: {result.get('datetime', 'N/A')}")
            return True
        else:
            print("❌ ローカルスクレイピング失敗")
            return False
            
    except ImportError:
        print("⚠️  ローカルのscrape_ishifuku.pyが見つかりません")
        return None
    except Exception as e:
        print(f"💥 ローカルスクレイピングでエラー: {e}")
        return False


if __name__ == "__main__":
    print("🧪 石福金属興業スクレイパー Lambda テストスイート（改良版）")
    print("=" * 60)
    
    # 価格抽出のテスト
    extraction_ok = test_price_extraction()
    
    print("\n" + "=" * 60)
    
    # モックを使用したLambda関数テスト
    mock_test_ok = test_lambda_with_mock()
    
    print("\n" + "=" * 60)
    
    # ローカルChromeを使用した実際のスクレイピングテスト
    local_test_ok = test_lambda_locally_with_local_chrome()
    
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー:")
    print(f"価格抽出テスト: {'✅ PASS' if extraction_ok else '❌ FAIL'}")
    print(f"Lambda モックテスト: {'✅ PASS' if mock_test_ok else '❌ FAIL'}")
    
    if local_test_ok is not None:
        print(f"ローカル実スクレイピング: {'✅ PASS' if local_test_ok else '❌ FAIL'}")
    else:
        print("ローカル実スクレイピング: ⏭️ SKIP")
    
    print("\n🎯 各テストの説明:")
    print("✅ 価格抽出: 文字列から価格を抽出する機能（純粋な関数）")
    print("✅ Lambda モック: AWS環境をモックしたLambda関数全体のテスト")
    print("🌐 ローカル実行: 実際のWebサイトからデータを取得（ローカルChrome使用）")
    
    print("\n🚀 実際のLambda環境でのテストを行うには:")
    print("1. AWS Lambda コンソールでテスト実行")
    print("2. API Gateway経由でHTTPリクエスト")
    print("3. CloudWatch Logsでログ確認")
