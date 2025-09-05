#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
価格抽出モジュール

HTML内から金価格を抽出する処理を提供します。
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from ..config import ScrapingConfig
from ..models import ProductPrice


class PriceExtractor(ABC):
    """価格抽出の抽象基底クラス"""

    @abstractmethod
    def extract_price(self, html: str) -> Optional[int]:
        """
        HTMLから価格を抽出

        Args:
            html: 解析対象のHTML文字列

        Returns:
            Optional[int]: 抽出された価格（円/g）。見つからない場合はNone
        """
        pass


class GoldPriceExtractor(PriceExtractor):
    """金価格抽出クラス"""

    def __init__(self, config: Optional[ScrapingConfig] = None):
        """
        初期化

        Args:
            config: スクレイピング設定。Noneの場合はデフォルト設定を使用
        """
        self.config = config or ScrapingConfig()

    def extract_price(self, html: str) -> Optional[int]:
        """
        HTMLから金価格を抽出

        Args:
            html: 解析対象のHTML文字列

        Returns:
            Optional[int]: 抽出された金価格（円/g）。見つからない場合はNone
        """
        soup = BeautifulSoup(html, "html.parser")

        # テーブルから金価格を検索
        gold_price = self._extract_from_table(soup)

        # テーブルで見つからない場合は別の方法で検索
        if not gold_price:
            gold_price = self._extract_from_text_patterns(soup)

        return gold_price

    def _extract_from_table(self, soup: BeautifulSoup) -> Optional[int]:
        """
        テーブルから金価格を抽出

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[int]: 抽出された金価格。見つからない場合はNone
        """
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:  # 最低3列必要
                    first_cell_text = cells[0].get_text(strip=True)

                    # 「金」を含む行を検索（「金(g)」など）
                    if self._is_gold_row(first_cell_text):
                        # 2番目のセル（小売価格）を取得
                        price_text = cells[1].get_text(strip=True)
                        gold_price = self._extract_price_from_text(price_text)

                        # 2番目がダメなら3番目を試す
                        if not gold_price and len(cells) >= 3:
                            price_text = cells[2].get_text(strip=True)
                            gold_price = self._extract_price_from_text(price_text)

                        if gold_price:
                            return gold_price

        return None

    def _extract_from_text_patterns(self, soup: BeautifulSoup) -> Optional[int]:
        """
        テキストパターンから金価格を抽出

        Args:
            soup: BeautifulSoupオブジェクト

        Returns:
            Optional[int]: 抽出された金価格。見つからない場合はNone
        """
        # 数値パターンを含む要素を検索（カンマ区切りの数値）
        price_patterns = [
            r"\d{1,2},\d{3}",  # 例: 17,550
            r"\d{2,3},\d{3}",  # 例: 175,500
            r"\d{1,3},\d{3}",  # 例: 1,750 または 17,550
        ]

        all_text = soup.get_text()

        for pattern in price_patterns:
            matches = re.findall(pattern, all_text)
            for match in matches:
                potential_price = self._extract_price_from_text(match)
                # 妥当な金価格の範囲をチェック
                if self._is_valid_price(potential_price):
                    return potential_price

        return None

    def _is_gold_row(self, text: str) -> bool:
        """
        テキストが金に関する行かどうかを判定

        Args:
            text: 判定対象のテキスト

        Returns:
            bool: 金に関する行の場合True
        """
        return "金" in text and ("g" in text or len(text) <= 5)

    def _extract_price_from_text(self, price_text: Optional[str]) -> Optional[int]:
        """
        価格テキストから数値を抽出

        Args:
            price_text: 価格テキスト

        Returns:
            Optional[int]: 抽出された価格。抽出できない場合はNone
        """
        if not price_text:
            return None

        # まず括弧内の部分を除去 (例: "+117" や "-50" など)
        cleaned_text = re.sub(r"\([^)]*\)", "", price_text.strip())

        # 数値パターンを検索（カンマ区切りまたは連続数字）
        # カンマ区切りの数値を優先
        match = re.search(r"(\d{1,3}(?:,\d{3})+)", cleaned_text)
        if match:
            price_str = match.group(1)
            # カンマを除去
            clean_price = price_str.replace(",", "")
            try:
                return int(clean_price)
            except ValueError:
                return None

        # カンマ区切りが見つからない場合は連続する数字を検索
        match = re.search(r"(\d+)", cleaned_text)
        if match:
            price_str = match.group(1)
            try:
                return int(price_str)
            except ValueError:
                return None

        return None

    def _is_valid_price(self, price: Optional[int]) -> bool:
        """
        価格が妥当な範囲内かチェック

        Args:
            price: チェック対象の価格

        Returns:
            bool: 妥当な価格の場合True
        """
        if price is None:
            return False

        return self.config.min_valid_price <= price <= self.config.max_valid_price


class MultiProductPriceExtractor:
    """複数商品の価格を抽出する拡張クラス

    金価格 + 地金型コイン（メイプルリーフ金貨・ウィーン金貨ハーモニー）各サイズ。
    既存 GoldPriceExtractor のヘルパーを再利用するため内部にインスタンスを保持。
    """

    # 仕様で定義された表示ラベル生成用設定
    BASE_COIN_LABEL = "メイプルリーフ金貨・ウィーン金貨ハーモニー"
    SIZE_LABEL_MAP = {
        "1オンス": "(1oz)",
        "1/2オンス": "(1/2oz)",
        "1/4オンス": "(1/4oz)",
        "1/10オンス": "(1/10oz)",
    }

    # 行テキスト判定に利用するサイズキー順序
    SIZE_KEYS = list(SIZE_LABEL_MAP.keys())

    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.config = config or ScrapingConfig()
        self.gold_extractor = GoldPriceExtractor(self.config)

    def _is_valid_coin_price(self, price: Optional[int]) -> bool:
        """コイン価格の妥当性判定
        """
        if price is None:
            return False
        return 20000 <= price <= 2000000

    def extract(self, html: str) -> List[ProductPrice]:
        """HTMLから対象全商品の価格を抽出

        Returns:
            List[ProductPrice]: 取得結果（price が None の場合は抽出失敗）
        """
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")

        results: List[ProductPrice] = []

        # 1. 金価格
        gold_price = self.gold_extractor.extract_price(html)
        results.append(ProductPrice(product_name="金", price=gold_price))

        # 2. コイン各サイズ
        # テーブル全行を走査し、ヘッダ/データセルの最初のテキストにパターンが含まれるか判定
        from ishifuku.utils import log_debug  # 遅延インポート（循環回避）

        # コインセクション継続フラグ（見出し行→サイズ行分割パターンに対応）
        coin_section_active = False
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if not cells:
                    continue

                # --- 集約行(1行内に複数サイズdiv)パターン検出と処理 ---
                if (
                    len(cells) >= 2
                    and (
                        "メイプル" in cells[0].get_text()
                        or "ウィーン" in cells[0].get_text()
                    )
                    and cells[1].find(class_="price-table-v2__price__ounce")
                ):
                    coin_section_active = True
                    price_blocks = cells[1].find_all(class_="price-table-v2__price")

                    for pb in price_blocks:
                        ounce_el = pb.find(class_="price-table-v2__price__ounce")
                        yen1_el = pb.find(class_="price-table-v2__price__yen1")
                        if not ounce_el or not yen1_el:
                            continue
                        size_raw = self._normalize(ounce_el.get_text(strip=True))
                        size_key = self._match_size_key_size_only(size_raw)
                        if not size_key:
                            # 行内にコイン名がないので size-only 判定を直接
                            for candidate in self.SIZE_KEYS:
                                if candidate in size_raw:
                                    size_key = candidate
                                    break
                        price_val = self.gold_extractor._extract_price_from_text(
                            yen1_el.get_text(strip=True)
                        )
                        if price_val is not None and not self._is_valid_coin_price(
                            price_val
                        ):
                            log_debug(
                                f"[COIN_PRICE_REJECT_AGG] size={size_raw}"
                                f"extracted={price_val} (invalid range)"
                            )
                            price_val = None
                        if size_key:
                            label = (
                                f"{self.BASE_COIN_LABEL}{self.SIZE_LABEL_MAP[size_key]}"
                            )
                            if not any(r.product_name == label for r in results):
                                log_debug(
                                    f"[COIN_AGG_ROW] size={size_key}"
                                    f"label={label} price={price_val}"
                                )
                                results.append(
                                    ProductPrice(product_name=label, price=price_val)
                                )
                    # 集約行は通常処理スキップ
                    continue

                # 行全体のテキスト連結（サイズ語が分割されているケース対応）
                all_text_parts = [c.get_text(strip=True) for c in cells]
                first_text = all_text_parts[0]
                row_joined_text = " / ".join(all_text_parts)
                normalized_first = self._normalize(first_text)
                normalized_row = self._normalize(row_joined_text)

                # 見出し行判定（コインキーワードのみでサイズを含まないケース）
                if ("メイプル" in normalized_first) or ("ウィーン" in normalized_first):
                    # サイズ語を含まなければセクション開始扱い
                    if not any(sk in normalized_first for sk in self.SIZE_KEYS):
                        coin_section_active = True

                size_key = self._match_size_key(normalized_first)
                if size_key is None:
                    # 1セル目でマッチしない場合、行全体で再判定
                    size_key = self._match_size_key(normalized_row)

                # コインセクション内ではサイズ語のみ行も許容
                if size_key is None and coin_section_active:
                    size_key = self._match_size_key_size_only(normalized_first)
                    if size_key is None:
                        size_key = self._match_size_key_size_only(normalized_row)

                if size_key is None:
                    continue

                price_val = None
                # 2列目以降を左から順に探索（最大5列程度想定）
                for idx in range(1, min(len(cells), 6)):
                    candidate_text = cells[idx].get_text(strip=True)
                    extracted = self.gold_extractor._extract_price_from_text(
                        candidate_text
                    )
                    if extracted is None:
                        continue
                    if not self._is_valid_coin_price(extracted):
                        log_debug(
                            f"[COIN_PRICE_REJECT] size={size_key}"
                            f"text='{candidate_text}'"
                            f"extracted={extracted} (invalid range)"
                        )
                        continue
                    price_val = extracted
                    break

                label = f"{self.BASE_COIN_LABEL}{self.SIZE_LABEL_MAP[size_key]}"
                if any(r.product_name == label for r in results):
                    continue
                log_debug(
                    f"[COIN_ROW] size={size_key} label={label}"
                    f"first='{normalized_first}'"
                    f"row='{normalized_row}' price={price_val}"
                )
                results.append(ProductPrice(product_name=label, price=price_val))

        # 抽出されたサイズが不足している場合も結果としては返す（欠損扱いは上位で判定）
        # 足りないサイズを None で埋める（安定した出力順保証）
        existing_labels = {r.product_name for r in results}
        for size_key in self.SIZE_KEYS:
            expected_label = f"{self.BASE_COIN_LABEL}{self.SIZE_LABEL_MAP[size_key]}"
            if expected_label not in existing_labels:
                results.append(ProductPrice(product_name=expected_label, price=None))

        # 表示順を仕様どおり: 金 → 各サイズ順
        order_map: Dict[str, int] = {"金": 0}
        for idx, size_key in enumerate(self.SIZE_KEYS, start=1):
            order_map[f"{self.BASE_COIN_LABEL}{self.SIZE_LABEL_MAP[size_key]}"] = idx
        results.sort(key=lambda x: order_map.get(x.product_name, 999))
        return results

    def _normalize(self, text: str) -> str:
        """表記揺れ吸収のための正規化

        - 全角スペース -> 半角
        - 全角数字 -> 半角
        - 大文字小文字統一（今回は数字+日本語中心のためそのまま）
        - 'oz' と 'オンス' の同一視のため前処理しやすい形へ（ここでは置換せず _match_size_key 内で対応）
        """
        import unicodedata

        if not text:
            return ""
        # 全角 -> 半角（幅変換）。記号も変換されるが影響軽微。
        normalized = unicodedata.normalize("NFKC", text)
        # 余分な空白統一
        normalized = re.sub(r"[\u3000\s]+", " ", normalized)
        return normalized.strip()

    def _match_size_key(self, text: str) -> Optional[str]:
        """コインサイズ行かを判定してサイズキーを返す

        許容パターン拡張:
          - 1オンス / 1 オンス / 1oz / 1 oz
          - 1/2オンス / 1/2 oz / 1/2oz 等
        """
        if not text:
            return None

        # コイン名キーワード存在チェック（改行・区切り差異吸収のため）
        if not ("メイプル" in text or "ウィーン" in text):
            return None

        # サイズ毎に複数パターンを構築
        pattern_map = {
            "1オンス": [r"1\s*オンス", r"1\s*oz"],
            "1/2オンス": [r"1/2\s*オンス", r"1/2\s*oz"],
            "1/4オンス": [r"1/4\s*オンス", r"1/4\s*oz"],
            "1/10オンス": [r"1/10\s*オンス", r"1/10\s*oz"],
        }
        for size_key, patterns in pattern_map.items():
            for pat in patterns:
                if re.search(pat, text, flags=re.IGNORECASE):
                    return size_key
        return None

    def _match_size_key_size_only(self, text: str) -> Optional[str]:
        """サイズ語のみで判定（直前にコイン見出しが出現したコンテキスト用）"""
        if not text:
            return None
        pattern_map = {
            "1オンス": [r"1\s*オンス", r"1\s*oz"],
            "1/2オンス": [r"1/2\s*オンス", r"1/2\s*oz"],
            "1/4オンス": [r"1/4\s*オンス", r"1/4\s*oz"],
            "1/10オンス": [r"1/10\s*オンス", r"1/10\s*oz"],
        }
        for size_key, patterns in pattern_map.items():
            for pat in patterns:
                if re.search(pat, text, flags=re.IGNORECASE):
                    return size_key
        return None


def extract_price_from_text(price_text: Optional[str]) -> Optional[int]:
    """
    価格テキストから数値を抽出（後方互換性のための関数）

    Args:
        price_text: 価格テキスト

    Returns:
        Optional[int]: 抽出された価格。抽出できない場合はNone
    """
    extractor = GoldPriceExtractor()
    return extractor._extract_price_from_text(price_text)


def create_price_extractor(config: Optional[ScrapingConfig] = None) -> PriceExtractor:
    """
    価格抽出器のファクトリ関数

    Args:
        config: スクレイピング設定

    Returns:
        PriceExtractor: 価格抽出器インスタンス
    """
    return GoldPriceExtractor(config)
