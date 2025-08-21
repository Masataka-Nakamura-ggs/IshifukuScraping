#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パフォーマンス最適化されたGoldPriceScraperクラス

パフォーマンス監視とキャッシュ機能を追加したバージョン
"""

import json
import os
import time
from typing import Any, Dict, Optional

from .config import get_config
from .core import GoldPriceScraper as BaseGoldPriceScraper
from .utils import log_info, log_warning


class OptimizedGoldPriceScraper(BaseGoldPriceScraper):
    """最適化されたGoldPriceScraperクラス"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        初期化
        """
        # キャッシュ関連の引数を取り除く
        self.cache_enabled = kwargs.pop("enable_cache", True)
        self.cache_ttl = kwargs.pop("cache_ttl", 300)  # 5分
        self.cache_file = kwargs.pop("cache_file", "cache/gold_price_cache.json")

        # 親クラスに残りの引数を渡す
        super().__init__(*args, **kwargs)

    def __enter__(self) -> "OptimizedGoldPriceScraper":
        """
        コンテキストマネージャーの開始
        """
        super().__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        コンテキストマネージャーの終了
        """
        super().__exit__(exc_type, exc_val, exc_tb)

    def scrape_and_save(self, use_cache: Optional[bool] = None) -> dict:
        """
        キャッシュ機能付きのスクレイピングと保存

        Args:
            use_cache: キャッシュを使用するか（デフォルト: self.cache_enabled）

        Returns:
            dict: 実行結果（基底クラスと同じ形式）
                - success: 成功フラグ
                - gold_price: 金価格（成功時）
                - filepath: 保存先パス（成功時）
                - error: エラーメッセージ（失敗時）
        """
        if use_cache is None:
            use_cache = self.cache_enabled

        # キャッシュチェック
        if use_cache:
            cached_result = self._get_cached_price()
            if cached_result:
                log_info("キャッシュされた価格データを使用します")
                return self._save_cached_result(cached_result)

        # 通常のスクレイピング実行
        try:
            result = super().scrape_and_save()
            success = result.get("success", False)

            # 成功した場合、結果をキャッシュ
            if success and use_cache:
                # 取得した金価格をキャッシュのために保存
                gold_price = result.get("gold_price")
                if gold_price:
                    self._last_gold_price = gold_price
                self._cache_last_result()

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_cached_price(self) -> Optional[Dict]:
        """
        キャッシュから価格データを取得

        Returns:
            Optional[Dict]: キャッシュされたデータ（有効期限内の場合）
        """
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # 有効期限チェック
            cache_time = cache_data.get("timestamp", 0)
            if time.time() - cache_time > self.cache_ttl:
                log_info("キャッシュの有効期限が切れています")
                return None

            data = cache_data.get("data")
            return data if isinstance(data, dict) else None

        except (json.JSONDecodeError, IOError) as e:
            log_warning(f"キャッシュファイルの読み込みに失敗: {e}")
            return None

    def _cache_last_result(self) -> None:
        """
        最後の結果をキャッシュに保存
        """
        try:
            # キャッシュディレクトリ作成
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

            # 最後のスクレイピング結果を取得（実装依存）
            # この例では簡略化
            cache_data = {
                "timestamp": time.time(),
                "data": {
                    "gold_price": getattr(self, "_last_gold_price", None),
                    "scrape_time": time.time(),
                },
            }

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            log_info("スクレイピング結果をキャッシュに保存しました")

        except Exception as e:
            log_warning(f"キャッシュ保存に失敗: {e}")

    def _save_cached_result(self, cached_data: Dict) -> dict:
        """
        キャッシュされた結果を保存

        Args:
            cached_data: キャッシュされたデータ

        Returns:
            dict: 実行結果（基底クラスと同じ形式）
        """
        try:
            # キャッシュデータを使用してCSVに保存
            gold_price = cached_data.get("gold_price")
            if gold_price:
                from .utils import (
                    get_current_datetime,
                )

                date_str, datetime_str, date_for_filename = get_current_datetime()

                data = {
                    "date_str": date_str,
                    "gold_price": gold_price,
                    "datetime_str": datetime_str,
                    "date_for_filename": date_for_filename,
                }

                filepath = self.storage.save(data)
                return {
                    "success": True,
                    "gold_price": gold_price,
                    "filepath": filepath,
                    "date_str": date_str,
                    "datetime_str": datetime_str,
                }

            return {
                "success": False,
                "error": "キャッシュデータに金価格が含まれていません",
            }

        except Exception as e:
            return {"success": False, "error": f"キャッシュデータの保存に失敗: {e}"}

    def find_price_page_url(self, driver: Any = None) -> str:
        """
        価格ページURLを検索
        """
        return super().find_price_page_url(driver)

    def scrape_gold_price(self) -> int:
        """
        金価格を取得
        """
        return super().scrape_gold_price()

    def clear_cache(self) -> None:
        """
        キャッシュをクリア
        """
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                log_info("キャッシュをクリアしました")
        except Exception as e:
            log_warning(f"キャッシュクリアに失敗: {e}")

    def get_cache_info(self) -> Dict:
        """
        キャッシュ情報を取得

        Returns:
            Dict: キャッシュ情報
        """
        if not os.path.exists(self.cache_file):
            return {"exists": False}

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            cache_time = cache_data.get("timestamp", 0)
            age_seconds = time.time() - cache_time
            is_valid = age_seconds <= self.cache_ttl

            return {
                "exists": True,
                "timestamp": cache_time,
                "age_seconds": age_seconds,
                "is_valid": is_valid,
                "ttl": self.cache_ttl,
            }

        except Exception as e:
            return {"exists": True, "error": str(e)}


def create_optimized_scraper(
    environment: str = "local", **kwargs: Any
) -> OptimizedGoldPriceScraper:
    """
    最適化されたスクレイパーを作成

    Args:
        environment: 実行環境（"local" または "lambda"）
        **kwargs: 追加オプション

    Returns:
        OptimizedGoldPriceScraper: 最適化されたスクレイパーインスタンス
    """
    config = get_config(environment)

    # 最適化オプションを設定
    optimization_options = {
        "enable_cache": kwargs.get("enable_cache", True),
        "cache_ttl": kwargs.get("cache_ttl", 300),
        "cache_file": kwargs.get("cache_file", "cache/gold_price_cache.json"),
    }

    return OptimizedGoldPriceScraper(config=config, **optimization_options)
