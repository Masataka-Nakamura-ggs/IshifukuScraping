#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Lambda向けメインスクリプト

"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from ishifuku import get_config, setup_lambda_logging
from ishifuku.core import GoldPriceScraper
from ishifuku.storage import create_s3_storage, is_s3_available

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda関数のエントリーポイント

    Args:
        event: Lambda イベント
        context: Lambda コンテキスト

    Returns:
        dict: 実行結果
    """
    # Lambda環境用のロガー設定
    logger = setup_lambda_logging()

    try:
        logger.info("Lambda Selenium スクレイピング処理を開始")

        # 設定を取得
        config = get_config("lambda")

        # ストレージを S3 に設定
        if not is_s3_available():
            raise RuntimeError(
                "S3 が利用できません。boto3 をインストールしてください。"
            )

        storage = create_s3_storage(config=config.storage)

        # スクレイパーを作成
        scraper = GoldPriceScraper(config=config, storage=storage)

        # スクレイピングを実行 (複数商品取得)
        result = scraper.scrape_all_and_save()

        if result.get("success"):
            products = result.get("products", [])
            # ProductPrice オブジェクト -> dict に変換（__dict__ で十分 / dataclassでない前提）
            product_list: List[Dict[str, Any]] = [p.__dict__ for p in products]
            success_count = sum(1 for p in product_list if p.get("price") is not None)

            logger.info(
                f"✅ Lambda スクレイピング処理が正常に完了しました"
                f"(取得商品数: {success_count}/{len(product_list)})"
            )

            # 結果を返す（products を返却）
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "success": True,
                        "message": "スクレイピングが正常に完了しました",
                        "filepath": result.get("filepath"),
                        "timestamp": result.get("datetime_str"),
                        "products": product_list,
                    },
                    ensure_ascii=False,
                ),
            }
        else:
            error_msg = result.get("error")
            logger.error(f"❌ スクレイピング処理が失敗しました: {error_msg}")

            return {
                "statusCode": 500,
                "body": json.dumps(
                    {
                        "success": False,
                        "message": f"スクレイピング処理が失敗しました: {error_msg}",
                        "error": error_msg,
                    },
                    ensure_ascii=False,
                ),
            }

    except Exception as e:
        logger.error(f"❌ 予期しないエラーが発生しました: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "message": "予期しないエラーが発生しました",
                    "error": str(e),
                },
                ensure_ascii=False,
            ),
        }


def main() -> None:
    """ローカルテスト用のメイン関数"""
    # テスト用のイベントとコンテキスト
    test_event: Dict[str, Any] = {}
    function_arn = "arn:aws:lambda:region:account:function:test-function"
    test_context = type(
        "Context",
        (),
        {
            "function_name": "test-function",
            "function_version": "1",
            "invoked_function_arn": function_arn,
            "memory_limit_in_mb": "128",
            "remaining_time_in_millis": lambda: 30000,
            "log_group_name": "/aws/lambda/test-function",
            "log_stream_name": "test-stream",
            "aws_request_id": "test-request-id",
        },
    )()

    # Lambda ハンドラーを実行
    result = lambda_handler(test_event, test_context)

    # 結果を表示
    print("Lambda実行結果:")
    print(f"ステータスコード: {result.get('statusCode')}")
    body = json.loads(result.get("body", "{}"))
    print(f"成功: {body.get('success')}")
    print(f"メッセージ: {body.get('message')}")

    if body.get("success"):
        print(f"タイムスタンプ: {body.get('timestamp')}")
        products = body.get("products", [])
        print("取得商品一覧:")
        for p in products:
            print(f" - {p.get('product_name')}: {p.get('price')}")


if __name__ == "__main__":
    main()
