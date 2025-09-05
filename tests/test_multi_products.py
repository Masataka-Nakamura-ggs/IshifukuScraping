#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""複数商品価格抽出テスト"""

import csv
import tempfile
from pathlib import Path

from src.ishifuku.config import ScrapingConfig, StorageConfig
from src.ishifuku.models import ProductPrice
from src.ishifuku.scraping.extractor import MultiProductPriceExtractor
from src.ishifuku.storage.csv_handler import CSVStorage

HTML_BASE = """
<html><body>
<table>
  <tr><td>金(g)</td><td>17,530</td></tr>
  <tr><td>メイプルリーフ金貨 1オンス</td><td>350,000</td></tr>
  <tr><td>メイプルリーフ金貨 1/2オンス</td><td>180,000</td></tr>
  <tr><td>ウィーン金貨ハーモニー 1/4オンス</td><td>95,000</td></tr>
  <tr><td>ウィーン金貨ハーモニー 1/10オンス</td><td>40,000</td></tr>
</table>
</body></html>
"""


def test_extract_all_products_complete():
    extractor = MultiProductPriceExtractor(ScrapingConfig())
    products = extractor.extract(HTML_BASE)
    # 金 + 4サイズ = 5
    assert len(products) == 5
    names = [p.product_name for p in products]
    assert names[0] == "金"
    # 価格は None でないものを最低3件以上想定
    assert sum(1 for p in products if p.price is not None) >= 3


def test_extract_partial_missing():
    html = """
    <html><body><table>
      <tr><td>金(g)</td><td>17,530</td></tr>
      <tr><td>メイプルリーフ金貨 1オンス</td><td>350,000</td></tr>
      <!-- 1/2オンス欠損 -->
      <tr><td>メイプルリーフ金貨 1/4オンス</td><td>95,000</td></tr>
      <!-- 1/10オンス欠損 -->
    </table></body></html>
    """
    extractor = MultiProductPriceExtractor(ScrapingConfig())
    products = extractor.extract(html)
    # 欠損は None で埋められる想定（合計5）
    assert len(products) == 5
    missing = [p for p in products if p.price is None]
    assert len(missing) >= 1


def test_csv_multi_product_write():
    # 成功商品のみ保存される想定
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = CSVStorage(StorageConfig(result_dir=tmpdir))
        data_rows = [
            {
                "date_str": "2025-09-04",
                "product_name": "金",
                "price": 17530,
                "datetime_str": "2025-09-04 10:00:00",
                "date_for_filename": "20250904",
                "multi_product": True,
            },
            {
                "date_str": "2025-09-04",
                "product_name": "メイプルリーフ金貨・ウィーン金貨ハーモニー(1oz)",
                "price": 350000,
                "datetime_str": "2025-09-04 10:00:00",
                "date_for_filename": "20250904",
                "multi_product": True,
            },
        ]
        for d in data_rows:
            storage.save(d)

        filename = storage.config.get_price_csv_filename("20250904")
        path = Path(tmpdir) / filename
        assert path.exists()
        with path.open("r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 2
        assert rows[0][0] == "2025-09-04"