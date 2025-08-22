#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日時処理ユーティリティモジュール

日時関連の処理を提供します。
"""

import datetime
from typing import Tuple


def get_current_datetime() -> Tuple[str, str, str]:
    """
    現在の日時を取得

    Returns:
        Tuple[str, str, str]: (日付文字列, 日時文字列, ファイル名用日付文字列)
            - 日付文字列: YYYY-MM-DD形式
            - 日時文字列: YYYY-MM-DD HH:MM:SS形式
            - ファイル名用日付文字列: YYYYMMDD形式
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_for_filename = now.strftime("%Y%m%d")
    return date_str, datetime_str, date_for_filename


def get_current_date_string() -> str:
    """
    現在の日付文字列を取得（YYYY-MM-DD形式）

    Returns:
        str: 現在の日付文字列
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_current_datetime_string() -> str:
    """
    現在の日時文字列を取得（YYYY-MM-DD HH:MM:SS形式）

    Returns:
        str: 現在の日時文字列
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_filename_date_string() -> str:
    """
    ファイル名用の日付文字列を取得（YYYYMMDD形式）

    Returns:
        str: ファイル名用日付文字列
    """
    return datetime.datetime.now().strftime("%Y%m%d")


def format_datetime_for_filename(dt: datetime.datetime) -> str:
    """
    指定された日時をファイル名用の文字列に変換

    Args:
        dt: 変換対象の日時

    Returns:
        str: ファイル名用日付文字列（YYYYMMDD形式）
    """
    return dt.strftime("%Y%m%d")


def format_datetime_for_display(dt: datetime.datetime) -> str:
    """
    指定された日時を表示用の文字列に変換

    Args:
        dt: 変換対象の日時

    Returns:
        str: 表示用日時文字列（YYYY-MM-DD HH:MM:SS形式）
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_date_string(date_str: str) -> datetime.datetime:
    """
    日付文字列をdatetimeオブジェクトに変換

    Args:
        date_str: 日付文字列（YYYY-MM-DD形式）

    Returns:
        datetime.datetime: 変換された日時オブジェクト

    Raises:
        ValueError: 日付文字列の形式が不正な場合
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD"
        ) from e


def is_valid_date_format(date_str: str) -> bool:
    """
    日付文字列の形式が正しいかチェック

    Args:
        date_str: チェック対象の日付文字列

    Returns:
        bool: 形式が正しい場合True、そうでなければFalse
    """
    try:
        parse_date_string(date_str)
        return True
    except ValueError:
        return False
