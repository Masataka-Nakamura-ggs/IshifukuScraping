#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ストレージモジュール

データ保存関連機能の公開インターフェース
"""

from .csv_handler import (
    CSVStorage,
    DataStorage,
    LegacyCSVHandler,
    create_csv_storage,
    create_empty_csv,
    create_legacy_csv_handler,
    save_to_csv,
)

# S3関連の機能は条件付きでインポート
try:
    from .s3_handler import S3Storage, create_s3_storage, is_s3_available

    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    S3Storage = None  # type: ignore
    create_s3_storage = None  # type: ignore

    def is_s3_available() -> bool:
        return False


__all__ = [
    # 抽象基底クラス
    "DataStorage",
    # CSV関連
    "CSVStorage",
    "LegacyCSVHandler",
    "create_csv_storage",
    "create_legacy_csv_handler",
    "save_to_csv",
    "create_empty_csv",
    # S3関連（利用可能な場合のみ）
]

# S3が利用可能な場合のみエクスポートリストに追加
if S3_AVAILABLE:
    __all__.extend(
        [
            "S3Storage",
            "create_s3_storage",
            "is_s3_available",
        ]
    )
