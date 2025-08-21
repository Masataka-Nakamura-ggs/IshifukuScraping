#!/usr/bin/env python3

from src.ishifuku.scraping.extractor import GoldPriceExtractor

extractor = GoldPriceExtractor()
test_cases = ['12,34a', '1,2,3,', 'invalid,number']

for case in test_cases:
    result = extractor._extract_price_from_text(case)
    print(f'Input: {case!r} -> Result: {result}')
