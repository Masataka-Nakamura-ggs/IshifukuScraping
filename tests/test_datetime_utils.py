#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日時ユーティリティのテスト
"""

import re

from src.ishifuku.utils.datetime_utils import (
    get_current_date_string,
    get_current_datetime,
)


class TestDateTimeUtils:
    """日時ユーティリティのテスト"""

    def test_get_current_datetime_returns_tuple(self):
        """get_current_datetime が適切なタプルを返すことを確認"""
        result = get_current_datetime()

        # タプルで3つの要素を返すことを確認
        assert isinstance(result, tuple)
        assert len(result) == 3

        date_str, datetime_str, filename_str = result

        # 各要素が文字列であることを確認
        assert isinstance(date_str, str)
        assert isinstance(datetime_str, str)
        assert isinstance(filename_str, str)

    def test_get_current_datetime_format_validation(self):
        """日時フォーマットの検証"""
        date_str, datetime_str, filename_str = get_current_datetime()

        # YYYY-MM-DD形式の確認
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", date_str)

        # YYYY-MM-DD HH:MM:SS形式の確認
        assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", datetime_str)

        # YYYYMMDD形式の確認
        assert re.match(r"^\d{8}$", filename_str)

    def test_get_current_date_string_format(self):
        """get_current_date_string のフォーマット確認"""
        result = get_current_date_string()

        # 文字列であることを確認
        assert isinstance(result, str)

        # YYYY-MM-DD形式であることを確認
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", result)

    def test_get_current_datetime_consistency(self):
        """get_current_datetime の一貫性確認"""
        date_str, datetime_str, filename_str = get_current_datetime()

        # date_str と datetime_str の日付部分が一致することを確認
        assert datetime_str.startswith(date_str)

        # filename_str が date_str から生成されていることを確認
        expected_filename = date_str.replace("-", "")
        assert filename_str == expected_filename
