#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSVストレージモジュール

CSV形式でのデータ保存機能を提供します。
"""

import csv
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..config import StorageConfig
from ..utils import log_error, log_info


class DataStorage(ABC):
    """データ保存の抽象基底クラス"""

    @abstractmethod
    def save(self, data: Dict) -> str:
        """
        データを保存

        Args:
            data: 保存するデータ

        Returns:
            str: 保存先のパス/識別子
        """
        pass


class CSVStorage(DataStorage):
    """CSV形式でのデータ保存クラス"""

    def __init__(self, config: Optional[StorageConfig] = None):
        """
        初期化

        Args:
            config: ストレージ設定。Noneの場合はデフォルト設定を使用
        """
        self.config = config or StorageConfig()

    def save(self, data: Dict) -> str:
        """
        データをCSVファイルに保存

        Args:
            data: 保存するデータ
                - date_str: 日付文字列
                - gold_price: 金価格
                - datetime_str: 日時文字列

        Returns:
            str: 保存されたファイルのパス

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            # resultフォルダが存在しない場合は作成
            os.makedirs(self.config.result_dir, exist_ok=True)

            # ファイル名を生成
            date_for_filename = data.get("date_for_filename", "unknown")
            filename = self.config.get_csv_filename(date_for_filename)
            filepath = os.path.join(self.config.result_dir, filename)

            # CSVファイルに保存
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [data["date_str"], data["gold_price"], data["datetime_str"]]
                )

            log_info(f"データをCSVファイルに保存しました: {filepath}")
            return filepath

        except Exception as e:
            error_msg = f"CSV保存エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e

    def create_empty_file(self, date_for_filename: str) -> str:
        """
        空のCSVファイルを作成

        Args:
            date_for_filename: ファイル名用の日付文字列

        Returns:
            str: 作成されたファイルのパス

        Raises:
            Exception: ファイル作成に失敗した場合
        """
        try:
            # resultフォルダが存在しない場合は作成
            os.makedirs(self.config.result_dir, exist_ok=True)

            # ファイル名を生成
            filename = self.config.get_csv_filename(date_for_filename)
            filepath = os.path.join(self.config.result_dir, filename)

            # 空ファイルを作成
            with open(filepath, "w", encoding="utf-8"):
                pass  # 空ファイルを作成

            log_info(f"空のCSVファイルを作成しました: {filepath}")
            return filepath

        except Exception as e:
            error_msg = f"空ファイル作成エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e

    def save_batch(self, data_list: List[Dict]) -> List[str]:
        """
        複数のデータを一括保存

        Args:
            data_list: 保存するデータのリスト

        Returns:
            List[str]: 保存されたファイルのパスリスト
        """
        saved_files = []
        for data in data_list:
            filepath = self.save(data)
            saved_files.append(filepath)
        return saved_files

    def read(self, filepath: str) -> List[Dict]:
        """
        CSVファイルを読み込み

        Args:
            filepath: 読み込み対象のファイルパス

        Returns:
            List[Dict]: 読み込まれたデータのリスト

        Raises:
            Exception: 読み込みに失敗した場合
        """
        try:
            data_list = []
            with open(filepath, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 3:
                        data_list.append(
                            {
                                "date_str": row[0],
                                "gold_price": int(row[1]) if row[1].isdigit() else 0,
                                "datetime_str": row[2],
                            }
                        )
            return data_list

        except Exception as e:
            error_msg = f"CSV読み込みエラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e


class LegacyCSVHandler:
    """既存コードとの互換性のためのCSVハンドラ"""

    def __init__(self, config: Optional[StorageConfig] = None):
        """
        初期化

        Args:
            config: ストレージ設定
        """
        self.storage = CSVStorage(config)

    def save_to_csv(
        self, date_str: str, gold_price: int, datetime_str: str, filename: str
    ) -> None:
        """
        CSVファイルに価格データを保存（後方互換性）

        Args:
            date_str: 日付文字列
            gold_price: 金価格
            datetime_str: 日時文字列
            filename: ファイル名
        """
        # ファイル名から日付を抽出
        date_for_filename = filename.replace("ishihuku-gold-", "").replace(".csv", "")

        data = {
            "date_str": date_str,
            "gold_price": gold_price,
            "datetime_str": datetime_str,
            "date_for_filename": date_for_filename,
        }

        self.storage.save(data)

    def create_empty_csv(self, filename: str) -> None:
        """
        空のCSVファイルを作成（後方互換性）

        Args:
            filename: ファイル名
        """
        # ファイル名から日付を抽出
        date_for_filename = filename.replace("ishihuku-gold-", "").replace(".csv", "")
        self.storage.create_empty_file(date_for_filename)


def create_csv_storage(config: Optional[StorageConfig] = None) -> CSVStorage:
    """
    CSVストレージのファクトリ関数

    Args:
        config: ストレージ設定

    Returns:
        CSVStorage: CSVストレージインスタンス
    """
    return CSVStorage(config)


def create_legacy_csv_handler(
    config: Optional[StorageConfig] = None,
) -> LegacyCSVHandler:
    """
    レガシーCSVハンドラのファクトリ関数

    Args:
        config: ストレージ設定

    Returns:
        LegacyCSVHandler: レガシーCSVハンドラインスタンス
    """
    return LegacyCSVHandler(config)


# 後方互換性のための関数
def save_to_csv(
    date_str: str, gold_price: int, datetime_str: str, filename: str
) -> None:
    """
    CSVファイルに価格データを保存（後方互換性のための関数）

    Args:
        date_str: 日付文字列
        gold_price: 金価格
        datetime_str: 日時文字列
        filename: ファイル名
    """
    handler = create_legacy_csv_handler()
    handler.save_to_csv(date_str, gold_price, datetime_str, filename)


def create_empty_csv(filename: str) -> None:
    """
    空のCSVファイルを作成（後方互換性のための関数）

    Args:
        filename: ファイル名
    """
    handler = create_legacy_csv_handler()
    handler.create_empty_csv(filename)
