#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ストレージモジュールのテスト
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from src.ishifuku.config import StorageConfig
from src.ishifuku.storage.csv_handler import (
    CSVStorage,
    LegacyCSVHandler,
    create_csv_storage,
    create_empty_csv,
    create_legacy_csv_handler,
    save_to_csv,
)


class TestCSVStorage:
    """CSVStorageのテスト"""

    def test_initialization_default(self):
        """デフォルト設定での初期化を確認"""
        storage = CSVStorage()

        assert storage.config is not None
        assert isinstance(storage.config, StorageConfig)

    def test_initialization_with_config(self):
        """カスタム設定での初期化を確認"""
        config = StorageConfig(result_dir="custom_result")
        storage = CSVStorage(config)

        assert storage.config == config
        assert storage.config.result_dir == "custom_result"

    def test_save_success(self):
        """データ保存成功ケースを確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(result_dir=temp_dir)
            storage = CSVStorage(config)

            data = {
                "date_str": "2025-08-21",
                "gold_price": 17530,
                "datetime_str": "2025-08-21 15:30:00",
                "date_for_filename": "20250821",
            }

            filepath = storage.save(data)

            # ファイルが作成されることを確認
            assert os.path.exists(filepath)
            assert "ishihuku-gold-20250821.csv" in filepath

            # ファイル内容を確認
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                assert "2025-08-21,17530,2025-08-21 15:30:00" in content

    def test_save_creates_directory(self):
        """保存時にディレクトリが作成されることを確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result_dir = os.path.join(temp_dir, "new_result")
            config = StorageConfig(result_dir=result_dir)
            storage = CSVStorage(config)

            data = {
                "date_str": "2025-08-21",
                "gold_price": 17530,
                "datetime_str": "2025-08-21 15:30:00",
                "date_for_filename": "20250821",
            }

            filepath = storage.save(data)

            # ディレクトリとファイルが作成されることを確認
            assert os.path.exists(result_dir)
            assert os.path.exists(filepath)

    def test_save_failure(self):
        """データ保存失敗ケースを確認"""
        # 書き込み不可能なディレクトリを指定
        config = StorageConfig(result_dir="/invalid/path")
        storage = CSVStorage(config)

        data = {
            "date_str": "2025-08-21",
            "gold_price": 17530,
            "datetime_str": "2025-08-21 15:30:00",
            "date_for_filename": "20250821",
        }

        with pytest.raises(Exception, match="CSV保存エラー"):
            storage.save(data)

    def test_create_empty_file_success(self):
        """空ファイル作成成功ケースを確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(result_dir=temp_dir)
            storage = CSVStorage(config)

            filepath = storage.create_empty_file("20250821")

            # ファイルが作成されることを確認
            assert os.path.exists(filepath)
            assert "ishihuku-gold-20250821.csv" in filepath

            # ファイルが空であることを確認
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                assert content == ""

    def test_create_empty_file_failure(self):
        """空ファイル作成失敗ケースを確認"""
        config = StorageConfig(result_dir="/invalid/path")
        storage = CSVStorage(config)

        with pytest.raises(Exception, match="空ファイル作成エラー"):
            storage.create_empty_file("20250821")

    def test_save_batch(self):
        """複数データの一括保存を確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(result_dir=temp_dir)
            storage = CSVStorage(config)

            data_list = [
                {
                    "date_str": "2025-08-21",
                    "gold_price": 17530,
                    "datetime_str": "2025-08-21 15:30:00",
                    "date_for_filename": "20250821",
                },
                {
                    "date_str": "2025-08-22",
                    "gold_price": 17600,
                    "datetime_str": "2025-08-22 15:30:00",
                    "date_for_filename": "20250822",
                },
            ]

            filepaths = storage.save_batch(data_list)

            # 2つのファイルが作成されることを確認
            assert len(filepaths) == 2
            for filepath in filepaths:
                assert os.path.exists(filepath)

    def test_read_success(self):
        """ファイル読み込み成功ケースを確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(result_dir=temp_dir)
            storage = CSVStorage(config)

            # まずファイルを作成
            data = {
                "date_str": "2025-08-21",
                "gold_price": 17530,
                "datetime_str": "2025-08-21 15:30:00",
                "date_for_filename": "20250821",
            }
            filepath = storage.save(data)

            # ファイルを読み込み
            read_data = storage.read(filepath)

            # データが正しく読み込まれることを確認
            assert len(read_data) == 1
            assert read_data[0]["date_str"] == "2025-08-21"
            assert read_data[0]["gold_price"] == 17530
            assert read_data[0]["datetime_str"] == "2025-08-21 15:30:00"

    def test_read_failure(self):
        """ファイル読み込み失敗ケースを確認"""
        storage = CSVStorage()

        with pytest.raises(Exception, match="CSV読み込みエラー"):
            storage.read("/nonexistent/file.csv")


class TestLegacyCSVHandler:
    """LegacyCSVHandlerのテスト"""

    def test_initialization(self):
        """初期化が正しく動作することを確認"""
        handler = LegacyCSVHandler()

        assert handler.storage is not None
        assert isinstance(handler.storage, CSVStorage)

    def test_save_to_csv(self):
        """レガシー形式での保存を確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(result_dir=temp_dir)
            handler = LegacyCSVHandler(config)

            handler.save_to_csv(
                "2025-08-21", 17530, "2025-08-21 15:30:00", "ishihuku-gold-20250821.csv"
            )

            # ファイルが作成されることを確認
            expected_path = os.path.join(temp_dir, "ishihuku-gold-20250821.csv")
            assert os.path.exists(expected_path)

    def test_create_empty_csv(self):
        """レガシー形式での空ファイル作成を確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = StorageConfig(result_dir=temp_dir)
            handler = LegacyCSVHandler(config)

            handler.create_empty_csv("ishihuku-gold-20250821.csv")

            # ファイルが作成されることを確認
            expected_path = os.path.join(temp_dir, "ishihuku-gold-20250821.csv")
            assert os.path.exists(expected_path)


class TestCSVStorageFactory:
    """CSVストレージファクトリのテスト"""

    def test_create_csv_storage_default(self):
        """デフォルト設定でのストレージ作成を確認"""
        storage = create_csv_storage()

        assert isinstance(storage, CSVStorage)
        assert storage.config is not None

    def test_create_csv_storage_with_config(self):
        """カスタム設定でのストレージ作成を確認"""
        config = StorageConfig(result_dir="custom")
        storage = create_csv_storage(config)

        assert isinstance(storage, CSVStorage)
        assert storage.config == config

    def test_create_legacy_csv_handler_default(self):
        """デフォルト設定でのレガシーハンドラ作成を確認"""
        handler = create_legacy_csv_handler()

        assert isinstance(handler, LegacyCSVHandler)
        assert handler.storage is not None

    def test_create_legacy_csv_handler_with_config(self):
        """カスタム設定でのレガシーハンドラ作成を確認"""
        config = StorageConfig(result_dir="custom")
        handler = create_legacy_csv_handler(config)

        assert isinstance(handler, LegacyCSVHandler)
        assert handler.storage.config == config


class TestBackwardCompatibilityFunctions:
    """後方互換性関数のテスト"""

    def test_save_to_csv_function(self):
        """save_to_csv関数の後方互換性を確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 一時的にresult_dirを変更
            with patch("src.ishifuku.storage.csv_handler.StorageConfig") as mock_config:
                mock_config.return_value.result_dir = temp_dir
                mock_config.return_value.get_csv_filename.return_value = (
                    "ishihuku-gold-20250821.csv"
                )

                # 関数を実行
                save_to_csv(
                    "2025-08-21",
                    17530,
                    "2025-08-21 15:30:00",
                    "ishihuku-gold-20250821.csv",
                )

                # 関数が例外なく実行されることを確認
                mock_config.assert_called()

    def test_create_empty_csv_function(self):
        """create_empty_csv関数の後方互換性を確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 一時的にresult_dirを変更
            with patch("src.ishifuku.storage.csv_handler.StorageConfig") as mock_config:
                mock_config.return_value.result_dir = temp_dir
                mock_config.return_value.get_csv_filename.return_value = (
                    "ishihuku-gold-20250821.csv"
                )

                # 関数を実行
                create_empty_csv("ishihuku-gold-20250821.csv")

                # 関数が例外なく実行されることを確認
                mock_config.assert_called()


class TestS3StorageImports:
    """S3ストレージのインポートテスト"""

    def test_s3_storage_imports(self):
        """S3関連機能のインポートテスト"""
        # boto3が利用不可能な環境でも正常にインポートできることを確認
        from src.ishifuku.storage import S3_AVAILABLE, is_s3_available

        # インポートが成功することを確認
        assert is_s3_available is not None
        assert isinstance(S3_AVAILABLE, bool)

        # 現在の環境でS3が利用可能かチェック
        available = is_s3_available()
        assert isinstance(available, bool)


class TestStorageInit:
    """storage __init__.py のテスト"""

    def test_import_all_storage_functions(self):
        """全てのストレージ関数がインポートできることを確認"""
        from src.ishifuku.storage import (
            CSVStorage,
            DataStorage,
            LegacyCSVHandler,
            create_csv_storage,
            create_empty_csv,
            create_legacy_csv_handler,
            is_s3_available,
            save_to_csv,
        )

        # 全ての関数がインポートされることを確認
        assert DataStorage is not None
        assert CSVStorage is not None
        assert LegacyCSVHandler is not None
        assert create_csv_storage is not None
        assert create_legacy_csv_handler is not None
        assert save_to_csv is not None
        assert create_empty_csv is not None
        assert is_s3_available is not None
