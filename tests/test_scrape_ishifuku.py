#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrape_ishifuku.py のテストファイル
"""

import csv
import datetime
import os
import shutil
import sys
import tempfile
from unittest.mock import patch

import pytest

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrape_ishifuku import (
    create_empty_csv,
    extract_price_from_text,
    get_current_datetime,
    save_to_csv,
    setup_logging,
)


class TestGetCurrentDatetime:
    """get_current_datetime関数のテスト"""

    def test_get_current_datetime_format(self):
        """日時フォーマットが正しいことを確認"""
        date_str, datetime_str, date_for_filename = get_current_datetime()

        # 日付フォーマットの確認 (YYYY-MM-DD)
        assert len(date_str) == 10
        assert date_str[4] == "-"
        assert date_str[7] == "-"

        # 日時フォーマットの確認 (YYYY-MM-DD HH:MM:SS)
        assert len(datetime_str) == 19
        assert datetime_str[10] == " "
        assert datetime_str[13] == ":"
        assert datetime_str[16] == ":"

        # ファイル名用日付フォーマットの確認 (YYYYMMDD)
        assert len(date_for_filename) == 8
        assert date_for_filename.isdigit()

    @patch("scrape_ishifuku.datetime")
    def test_get_current_datetime_mock(self, mock_datetime):
        """モックを使用した日時テスト"""
        # 固定の日時を設定
        fixed_datetime = datetime.datetime(2025, 8, 21, 15, 30, 45)
        mock_datetime.datetime.now.return_value = fixed_datetime
        mock_datetime.datetime.side_effect = lambda *args, **kw: datetime.datetime(
            *args, **kw
        )

        date_str, datetime_str, date_for_filename = get_current_datetime()

        assert date_str == "2025-08-21"
        assert datetime_str == "2025-08-21 15:30:45"
        assert date_for_filename == "20250821"


class TestExtractPriceFromText:
    """extract_price_from_text関数のテスト"""

    def test_extract_price_basic(self):
        """基本的な価格抽出テスト"""
        assert extract_price_from_text("17,530") == 17530
        assert extract_price_from_text("1,000") == 1000
        assert extract_price_from_text("123,456") == 123456

    def test_extract_price_with_parentheses(self):
        """括弧付き価格の抽出テスト"""
        assert extract_price_from_text("17,530(+117)") == 17530
        assert extract_price_from_text("16,800(-200)") == 16800
        assert extract_price_from_text("15,000(+0)") == 15000

    def test_extract_price_with_spaces(self):
        """スペース付き価格の抽出テスト"""
        assert extract_price_from_text(" 17,530 ") == 17530
        assert extract_price_from_text("  1,000  ") == 1000

    def test_extract_price_invalid_input(self):
        """無効な入力のテスト"""
        assert extract_price_from_text("") is None
        assert extract_price_from_text(None) is None
        assert extract_price_from_text("abc") is None
        assert extract_price_from_text("no numbers here") is None

    def test_extract_price_edge_cases(self):
        """エッジケースのテスト"""
        assert extract_price_from_text("0") == 0
        assert extract_price_from_text("1") == 1
        assert extract_price_from_text("999,999") == 999999


class TestCreateEmptyCSV:
    """create_empty_csv関数のテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch("scrape_ishifuku.logging")
    def test_create_empty_csv_success(self, mock_logging):
        """空CSVファイル作成の成功テスト"""
        filename = "test_empty.csv"

        with patch("builtins.print") as mock_print:
            create_empty_csv(filename)

        # resultフォルダとファイルが作成されているか確認
        assert os.path.exists("result")
        assert os.path.exists(f"result/{filename}")

        # ファイルが空であることを確認
        with open(f"result/{filename}", "r") as f:
            content = f.read()
            assert content == ""

        # 成功メッセージが出力されているか確認
        mock_print.assert_called_once()
        assert "空のCSVファイルを作成しました" in str(mock_print.call_args)

    @patch("scrape_ishifuku.logging")
    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_create_empty_csv_error(self, mock_open, mock_logging):
        """空CSVファイル作成のエラーテスト"""
        filename = "test_error.csv"

        create_empty_csv(filename)

        # エラーログが呼ばれているか確認
        mock_logging.error.assert_called_once()
        assert "空ファイル作成エラー" in str(mock_logging.error.call_args)


class TestSaveToCSV:
    """save_to_csv関数のテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_save_to_csv_success(self):
        """CSV保存の成功テスト"""
        date_str = "2025-08-21"
        gold_price = 17530
        datetime_str = "2025-08-21 15:30:45"
        filename = "test_gold.csv"

        with patch("builtins.print") as mock_print:
            save_to_csv(date_str, gold_price, datetime_str, filename)

        # resultフォルダとファイルが作成されているか確認
        assert os.path.exists("result")
        assert os.path.exists(f"result/{filename}")

        # ファイル内容の確認
        with open(f"result/{filename}", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            row = next(reader)
            assert row == [date_str, str(gold_price), datetime_str]

        # 成功メッセージが出力されているか確認
        mock_print.assert_called_once()
        assert "データをCSVファイルに保存しました" in str(mock_print.call_args)

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_save_to_csv_error(self, mock_open):
        """CSV保存のエラーテスト"""
        with pytest.raises(Exception) as exc_info:
            save_to_csv("2025-08-21", 17530, "2025-08-21 15:30:45", "test_error.csv")

        assert "CSV保存エラー" in str(exc_info.value)


class TestSetupLogging:
    """setup_logging関数のテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch("scrape_ishifuku.datetime")
    def test_setup_logging(self, mock_datetime):
        """ログ設定のテスト"""
        # 固定の日付を設定
        fixed_datetime = datetime.datetime(2025, 8, 21, 15, 30, 45)
        mock_datetime.datetime.now.return_value = fixed_datetime
        mock_datetime.datetime.side_effect = lambda *args, **kw: datetime.datetime(
            *args, **kw
        )

        setup_logging()

        # logsフォルダが作成されているか確認
        assert os.path.exists("logs")

        # ログファイルが作成されているか確認
        expected_error_log = "logs/scraping_error_20250821.log"
        expected_info_log = "logs/scraping_info_20250821.log"

        # ログファイルが存在するかは、実際にログを出力してから確認
        import logging

        logging.error("Test error message")
        logging.info("Test info message")

        assert os.path.exists(expected_error_log)
        assert os.path.exists(expected_info_log)


# 統合テスト用のフィクスチャ
@pytest.fixture
def temp_workspace():
    """一時的なワークスペースを作成"""
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(test_dir)

    yield test_dir

    os.chdir(original_cwd)
    shutil.rmtree(test_dir)


class TestIntegration:
    """統合テスト"""

    def test_workflow_success(self, temp_workspace):
        """正常なワークフローのテスト"""
        # ログ設定
        with patch("scrape_ishifuku.datetime") as mock_datetime:
            fixed_datetime = datetime.datetime(2025, 8, 21, 15, 30, 45)
            mock_datetime.datetime.now.return_value = fixed_datetime
            mock_datetime.datetime.side_effect = lambda *args, **kw: datetime.datetime(
                *args, **kw
            )

            setup_logging()

            # 日時取得
            date_str, datetime_str, date_for_filename = get_current_datetime()

            # 価格データの準備
            price_text = "17,530(+117)"
            gold_price = extract_price_from_text(price_text)

            # CSV保存
            filename = f"ishihuku-gold-{date_for_filename}.csv"
            save_to_csv(date_str, gold_price, datetime_str, filename)

            # 結果の確認
            assert gold_price == 17530
            assert os.path.exists(f"result/{filename}")

            # ファイル内容の確認
            with open(f"result/{filename}", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                row = next(reader)
                assert row == ["2025-08-21", "17530", "2025-08-21 15:30:45"]


if __name__ == "__main__":
    pytest.main([__file__])
