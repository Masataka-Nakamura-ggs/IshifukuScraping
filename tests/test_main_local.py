#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main_local.py のテスト

ローカル実行用メイン関数のテストケースを提供します。
"""

from io import StringIO
from unittest.mock import Mock, patch

import pytest


class TestMainLocal:
    """main_local.py のテスト"""

    @patch("src.main_local.create_gold_price_scraper")
    @patch("src.main_local.get_config")
    @patch("src.main_local.setup_logging")
    def test_main_execution_success(
        self, mock_setup_logging, mock_get_config, mock_create_scraper
    ):
        """メイン実行の正常ケース"""
        from src.main_local import main

        # モックの設定
        mock_config = Mock()
        mock_config.storage = Mock()
        mock_get_config.return_value = mock_config

        # コンテキストマネージャーを持つモックスクレイパー
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = {
            "success": True,
            "gold_price": 17530,
            "datetime_str": "2025-08-21 12:00:00",
            "filepath": "/test/path.csv",
        }

        # コンテキストマネージャーのサポート
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_scraper)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_create_scraper.return_value = mock_context_manager

        # 標準出力をキャプチャ
        captured_output = StringIO()

        with patch("sys.stdout", captured_output):
            main()

        # 検証
        mock_setup_logging.assert_called_once()
        mock_get_config.assert_called_once_with("local")
        mock_create_scraper.assert_called_once_with("local", mock_config)
        mock_scraper.scrape_and_save.assert_called_once()

        output = captured_output.getvalue()
        assert "石福金属興業" in output or "処理が正常に完了" in output

    @patch("src.main_local.create_gold_price_scraper")
    @patch("src.main_local.get_config")
    @patch("src.main_local.setup_logging")
    def test_main_execution_failure(
        self, mock_setup_logging, mock_get_config, mock_create_scraper
    ):
        """スクレイピング失敗時のテスト"""
        from src.main_local import main

        # モックの設定
        mock_config = Mock()
        mock_config.storage = Mock()
        mock_get_config.return_value = mock_config

        # コンテキストマネージャーを持つモックスクレイパー
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = {
            "success": False,
            "error": "テストエラー",
        }

        # コンテキストマネージャーのサポート
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_scraper)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_create_scraper.return_value = mock_context_manager

        # 標準出力をキャプチャ
        captured_output = StringIO()

        with patch("sys.stdout", captured_output):
            main()

        # 検証
        mock_scraper.scrape_and_save.assert_called_once()

        output = captured_output.getvalue()
        assert "エラーが発生しました" in output or "エラー処理が完了" in output

    def test_module_imports(self):
        """必要なモジュールのインポートテスト"""
        try:
            from src.main_local import main

            # インポートが成功することを確認
            assert callable(main)
        except ImportError as e:
            pytest.fail(f"Required modules could not be imported: {e}")
