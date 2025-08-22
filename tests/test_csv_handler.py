#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSVハンドラーのテスト
"""

import tempfile

from src.ishifuku.config import StorageConfig
from src.ishifuku.storage.csv_handler import CSVStorage


class TestCSVStorage:
    """CSVStorageクラスのテスト"""

    def test_csv_storage_initialization(self):
        """CSVStorageの初期化テスト"""
        config = StorageConfig()
        csv_storage = CSVStorage(config)
        assert csv_storage is not None
        assert csv_storage.config == config

    def test_csv_storage_with_temp_directory(self):
        """一時ディレクトリでのCSVStorage動作テスト"""
        with tempfile.TemporaryDirectory():
            config = StorageConfig()
            # configのoutput_dirを一時ディレクトリに設定（可能な場合）
            csv_storage = CSVStorage(config)

            # 基本的な存在確認
            assert hasattr(csv_storage, "save")
            assert callable(csv_storage.save)

    def test_csv_storage_save_method_exists(self):
        """CSVStorageのsaveメソッド存在確認"""
        config = StorageConfig()
        csv_storage = CSVStorage(config)

        # saveメソッドが存在することを確認
        assert hasattr(csv_storage, "save")

        # メソッドが呼び出し可能であることを確認
        assert callable(getattr(csv_storage, "save"))


class TestDataStorageInterface:
    """DataStorageインターフェースのテスト"""

    def test_data_storage_abstract_class_import(self):
        """DataStorageクラスのインポートテスト"""
        from src.ishifuku.storage.csv_handler import DataStorage

        # 抽象基底クラスであることを確認
        assert hasattr(DataStorage, "save")
        assert DataStorage.__abstractmethods__
