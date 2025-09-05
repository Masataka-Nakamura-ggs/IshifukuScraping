#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データモデルモジュール

スクレイピング結果を保持するための共通データモデルを定義します。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductPrice:
    """単一商品の価格情報

    Attributes:
        product_name: 商品名（仕様で定義されたラベル）
        price: 取得した小売価格。取得失敗時は None
    """

    product_name: str
    price: Optional[int]


__all__ = ["ProductPrice"]
