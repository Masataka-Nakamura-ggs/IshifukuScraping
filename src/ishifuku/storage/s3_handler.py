#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3ストレージモジュール

AWS S3でのデータ保存機能を提供します。
"""

import json
from typing import Dict, Optional

try:
    import boto3
    from botocore.exceptions import ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from ..config import StorageConfig
from ..utils import log_error, log_info
from .csv_handler import DataStorage


class S3Storage(DataStorage):
    """S3でのデータ保存クラス"""

    def __init__(self, config: Optional[StorageConfig] = None):
        """
        初期化

        Args:
            config: ストレージ設定。Noneの場合はデフォルト設定を使用

        Raises:
            ImportError: boto3がインストールされていない場合
            ValueError: S3バケット名が設定されていない場合
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3がインストールされていません。pip install boto3 でインストールしてください。"
            )

        self.config = config or StorageConfig()

        if not self.config.s3_bucket_name:
            raise ValueError("S3バケット名が設定されていません。")

        self.s3_client = boto3.client("s3")

    def save(self, data: Dict) -> str:
        """
        データをS3に保存

        Args:
            data: 保存するデータ
                - date_str: 日付文字列
                - gold_price: 金価格
                - datetime_str: 日時文字列

        Returns:
            str: S3のオブジェクトキー

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            # CSV形式のデータを作成
            csv_content = (
                f"{data['date_str']},{data['gold_price']},{data['datetime_str']}\n"
            )

            # S3オブジェクトキーを生成
            date_for_filename = data.get("date_for_filename", "unknown")
            filename = self.config.get_csv_filename(date_for_filename)
            s3_key = f"{self.config.s3_key_prefix}{filename}"

            # S3にアップロード
            if not self.config.s3_bucket_name:
                raise ValueError("S3バケット名が設定されていません")

            self.s3_client.put_object(
                Bucket=self.config.s3_bucket_name,
                Key=s3_key,
                Body=csv_content,
                ContentType="text/csv",
            )

            log_info(
                f"データをS3に保存しました: s3://{self.config.s3_bucket_name}/{s3_key}"
            )
            return s3_key

        except ClientError as e:
            error_msg = f"S3保存エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"S3保存エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e

    def save_json(self, data: Dict, date_for_filename: str) -> str:
        """
        データをJSON形式でS3に保存

        Args:
            data: 保存するデータ
            date_for_filename: ファイル名用の日付文字列

        Returns:
            str: S3のオブジェクトキー

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            # JSON形式のデータを作成
            json_content = json.dumps(data, ensure_ascii=False, indent=2)

            # S3オブジェクトキーを生成
            filename = f"ishihuku-gold-{date_for_filename}.json"
            s3_key = f"{self.config.s3_key_prefix}{filename}"

            # S3にアップロード
            if not self.config.s3_bucket_name:
                raise ValueError("S3バケット名が設定されていません")

            self.s3_client.put_object(
                Bucket=self.config.s3_bucket_name,
                Key=s3_key,
                Body=json_content,
                ContentType="application/json",
            )

            log_info(
                f"JSONデータをS3に保存しました: s3://{self.config.s3_bucket_name}/{s3_key}"
            )
            return s3_key

        except ClientError as e:
            error_msg = f"S3 JSON保存エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"S3 JSON保存エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e

    def read(self, s3_key: str) -> Dict:
        """
        S3からデータを読み込み

        Args:
            s3_key: S3オブジェクトキー

        Returns:
            Dict: 読み込まれたデータ

        Raises:
            Exception: 読み込みに失敗した場合
        """
        try:
            if not self.config.s3_bucket_name:
                raise ValueError("S3バケット名が設定されていません")

            response = self.s3_client.get_object(
                Bucket=self.config.s3_bucket_name, Key=s3_key
            )

            content = response["Body"].read().decode("utf-8")

            # CSV形式のデータを解析
            lines = content.strip().split("\n")
            data_list = []

            for line in lines:
                parts = line.split(",")
                if len(parts) >= 3:
                    data_list.append(
                        {
                            "date_str": parts[0],
                            "gold_price": int(parts[1]) if parts[1].isdigit() else 0,
                            "datetime_str": parts[2],
                        }
                    )

            return {"data": data_list}

        except ClientError as e:
            error_msg = f"S3読み込みエラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"S3読み込みエラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e

    def list_objects(self, prefix: Optional[str] = None) -> list:
        """
        S3バケット内のオブジェクト一覧を取得

        Args:
            prefix: オブジェクトキーのプレフィックス

        Returns:
            list: オブジェクト情報のリスト

        Raises:
            Exception: 取得に失敗した場合
        """
        try:
            if not self.config.s3_bucket_name:
                raise ValueError("S3バケット名が設定されていません")

            search_prefix = prefix or self.config.s3_key_prefix

            response = self.s3_client.list_objects_v2(
                Bucket=self.config.s3_bucket_name, Prefix=search_prefix
            )

            objects = response.get("Contents", [])
            return [
                {
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"],
                }
                for obj in objects
            ]

        except ClientError as e:
            error_msg = f"S3オブジェクト一覧取得エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"S3オブジェクト一覧取得エラー: {e}"
            log_error(error_msg, e)
            raise Exception(error_msg) from e


def create_s3_storage(config: Optional[StorageConfig] = None) -> S3Storage:
    """
    S3ストレージのファクトリ関数

    Args:
        config: ストレージ設定

    Returns:
        S3Storage: S3ストレージインスタンス
    """
    return S3Storage(config)


def is_s3_available() -> bool:
    """
    S3機能が利用可能かチェック

    Returns:
        bool: S3機能が利用可能な場合True
    """
    return BOTO3_AVAILABLE
