#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログ設定ユーティリティモジュール

ログ関連の設定と処理を提供します。
"""

import logging
import os
from typing import Optional

from ..config import StorageConfig
from .datetime_utils import get_filename_date_string


def setup_logging(
    storage_config: Optional[StorageConfig] = None, log_level: int = logging.INFO
) -> logging.Logger:
    """
    ログ設定を初期化（日時ローテーション）

    Args:
        storage_config: ストレージ設定。Noneの場合はデフォルト設定を使用
        log_level: ログレベル

    Returns:
        logging.Logger: 設定されたロガー
    """
    if storage_config is None:
        storage_config = StorageConfig()

    # logsフォルダが存在しない場合は作成
    os.makedirs(storage_config.logs_dir, exist_ok=True)

    # 現在の日付を取得してログファイル名に使用
    current_date = get_filename_date_string()

    # ログファイル名を生成
    error_log_filename = os.path.join(
        storage_config.logs_dir, storage_config.get_log_filename("error", current_date)
    )
    info_log_filename = os.path.join(
        storage_config.logs_dir, storage_config.get_log_filename("info", current_date)
    )

    # ログ設定をクリア
    logging.getLogger().handlers.clear()

    # フォーマッター
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # エラーログハンドラ
    error_handler = logging.FileHandler(error_log_filename, mode="a", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # 実行ログハンドラ
    info_handler = logging.FileHandler(info_log_filename, mode="a", encoding="utf-8")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # ルートロガーに設定
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)

    return logger


def setup_lambda_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Lambda環境用のログ設定を初期化

    Args:
        log_level: ログレベル

    Returns:
        logging.Logger: 設定されたロガー
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Lambda環境では既存のハンドラをそのまま使用
    if not logger.handlers:
        # ハンドラが存在しない場合のみ追加
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    指定された名前のロガーを取得

    Args:
        name: ロガー名

    Returns:
        logging.Logger: ロガー
    """
    return logging.getLogger(name)


def log_error(message: str, exception: Optional[Exception] = None) -> None:
    """
    エラーメッセージをログに記録

    Args:
        message: エラーメッセージ
        exception: 例外オブジェクト（オプション）
    """
    logger = logging.getLogger()
    if exception:
        logger.error(f"{message}: {exception}", exc_info=True)
    else:
        logger.error(message)


def log_info(message: str) -> None:
    """
    情報メッセージをログに記録

    Args:
        message: 情報メッセージ
    """
    logger = logging.getLogger()
    logger.info(message)


def log_warning(message: str) -> None:
    """
    警告メッセージをログに記録

    Args:
        message: 警告メッセージ
    """
    logger = logging.getLogger()
    logger.warning(message)


def log_debug(message: str) -> None:
    """
    デバッグメッセージをログに記録

    Args:
        message: デバッグメッセージ
    """
    logger = logging.getLogger()
    logger.debug(message)
