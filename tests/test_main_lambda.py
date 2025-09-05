#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main_lambda.py のテスト

AWS Lambda関数のテストケースを提供します。
"""

import json
from types import SimpleNamespace
from typing import Any, Dict
from unittest.mock import Mock, patch


class TestMainLambda:
    """main_lambda.py のテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行される設定"""
        self.mock_context = Mock()
        self.mock_context.function_name = "test-ishifuku-scraper"
        self.mock_context.function_version = "1"
        self.mock_context.invoked_function_arn = (
            "arn:aws:lambda:region:account:function:test-function"
        )
        self.mock_context.memory_limit_in_mb = "128"
        self.mock_context.remaining_time_in_millis = lambda: 30000
        self.mock_context.log_group_name = "/aws/lambda/test-function"
        self.mock_context.log_stream_name = "2024/08/21/[$LATEST]test"
        self.mock_context.aws_request_id = "test-request-id"

    @patch("src.main_lambda.GoldPriceScraper")
    @patch("src.main_lambda.create_s3_storage")
    @patch("src.main_lambda.get_config")
    @patch("src.main_lambda.setup_lambda_logging")
    @patch("src.main_lambda.is_s3_available")
    def test_lambda_handler_success(
        self,
        mock_is_s3_available,
        mock_setup_logging,
        mock_get_config,
        mock_create_s3_storage,
        mock_GoldPriceScraper,
    ):
        """正常なLambda実行をテスト"""
        from src.main_lambda import lambda_handler

        # モックの設定
        mock_config = Mock()
        mock_config.storage = Mock()
        mock_config.storage.s3_bucket_name = "test-bucket"
        mock_config.storage.s3_key_prefix = "test-prefix"
        mock_get_config.return_value = mock_config

        mock_is_s3_available.return_value = True

        mock_storage = Mock()
        mock_create_s3_storage.return_value = mock_storage

        mock_scraper_instance = mock_GoldPriceScraper.return_value
        mock_scraper_instance.scrape_all_and_save.return_value = {
            "success": True,
            "filepath": "result/test.csv",
            "datetime_str": "2025-08-21 10:00:00",
            "products": [
                SimpleNamespace(product_name="金", price=17530),
                SimpleNamespace(
                    product_name="メイプルリーフ金貨・ウィーン金貨ハーモニー(1oz)",
                    price=400000,
                ),
            ],
        }

        # テスト実行
        event: Dict[str, Any] = {"test": True}
        result = lambda_handler(event, self.mock_context)

        # 検証
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["success"] is True
        assert "timestamp" in body
        assert "products" in body
        assert isinstance(body["products"], list)
        assert len(body["products"]) >= 2
        assert body["products"][0]["product_name"] == "金"

        logger_mock = mock_setup_logging.return_value
        info_messages = [str(c.args[0]) for c in logger_mock.info.call_args_list]
        assert any("取得商品数:" in msg for msg in info_messages)

        # モックが適切に呼ばれたことを確認
        mock_setup_logging.assert_called_once()
        mock_get_config.assert_called_once_with("lambda")
        mock_create_s3_storage.assert_called_once_with(config=mock_config.storage)
        mock_GoldPriceScraper.assert_called_once_with(
            config=mock_config, storage=mock_storage
        )
        mock_scraper_instance.scrape_all_and_save.assert_called_once()

    @patch("src.main_lambda.GoldPriceScraper")
    @patch("src.main_lambda.create_s3_storage")
    @patch("src.main_lambda.get_config")
    @patch("src.main_lambda.setup_lambda_logging")
    @patch("src.main_lambda.is_s3_available")
    def test_lambda_handler_scraping_failure(
        self,
        mock_is_s3_available,
        mock_setup_logging,
        mock_get_config,
        mock_create_s3_storage,
        mock_GoldPriceScraper,
    ):
        """スクレイピング失敗時のテスト"""
        from src.main_lambda import lambda_handler

        # モックの設定
        mock_config = Mock()
        mock_config.storage = Mock()
        mock_config.storage.s3_bucket_name = "test-bucket"
        mock_config.storage.s3_key_prefix = "test-prefix"
        mock_get_config.return_value = mock_config

        mock_is_s3_available.return_value = True

        mock_storage = Mock()
        mock_create_s3_storage.return_value = mock_storage

        mock_scraper_instance = mock_GoldPriceScraper.return_value
        mock_scraper_instance.scrape_all_and_save.return_value = {
            "success": False,
            "error": "スクレイピングに失敗しました",
        }

        # テスト実行
        event: Dict[str, Any] = {}
        result = lambda_handler(event, self.mock_context)

        # 検証
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body
        assert "スクレイピング" in body["error"]

    @patch("src.main_lambda.GoldPriceScraper")
    @patch("src.main_lambda.get_config")
    @patch("src.main_lambda.setup_lambda_logging")
    @patch("src.main_lambda.is_s3_available")
    def test_lambda_handler_s3_unavailable(
        self,
        mock_is_s3_available,
        mock_setup_logging,
        mock_get_config,
        mock_GoldPriceScraper,
    ):
        """S3が利用できない場合のテスト"""
        from src.main_lambda import lambda_handler

        # モックの設定
        mock_config = Mock()
        mock_config.storage = Mock()
        mock_get_config.return_value = mock_config

        mock_is_s3_available.return_value = False

        # テスト実行
        event: Dict[str, Any] = {}
        result = lambda_handler(event, self.mock_context)

        # 検証
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body
        assert "S3" in body["error"]

    def test_main_function_execution(self):
        """メイン関数の実行テスト"""
        from src.main_lambda import main

        # ローカルテスト実行（例外が発生しないことを確認）
        with patch("src.main_lambda.lambda_handler") as mock_lambda_handler:
            mock_lambda_handler.return_value = {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "success": True,
                        "timestamp": "2025-08-21 10:00:00",
                        "products": [{"product_name": "金", "price": 17530}],
                    }
                ),
            }

            # テスト実行（例外なく完了することを確認）
            try:
                main()
            except SystemExit:
                # main関数内でprint文の後にexit処理がある場合があるため
                pass
