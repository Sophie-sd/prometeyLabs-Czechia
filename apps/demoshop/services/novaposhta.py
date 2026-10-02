"""Stub dopravce pro demo-shop (CZ): fixture měst/výdejních míst, bez API klíče a bez zásilek.

Historicky pojmenováno novaposhta; checkout stále používá np_* pole. Data = CZ demo (Zásilkovna-style).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parent.parent / 'fixtures' / 'np_test_data.json'


@lru_cache(maxsize=1)
def _load_fixture() -> dict:
    with FIXTURE_PATH.open(encoding='utf-8') as fh:
        return json.load(fh)


def search_cities(query: str = '', limit: int = 12) -> list[dict]:
    q = (query or '').strip().casefold()
    cities = _load_fixture().get('cities', [])
    if q:
        cities = [c for c in cities if q in c['name'].casefold() or q in c.get('area', '').casefold()]
    return cities[: max(1, min(limit, 50))]


def warehouses_for_city(city_ref: str) -> list[dict]:
    ref = (city_ref or '').strip()
    if not ref:
        return []
    return [
        w for w in _load_fixture().get('warehouses', [])
        if w.get('city_ref') == ref
    ]


def city_by_ref(city_ref: str) -> dict | None:
    ref = (city_ref or '').strip()
    for city in _load_fixture().get('cities', []):
        if city['ref'] == ref:
            return city
    return None


def warehouse_by_ref(warehouse_ref: str) -> dict | None:
    ref = (warehouse_ref or '').strip()
    for wh in _load_fixture().get('warehouses', []):
        if wh['ref'] == ref:
            return wh
    return None
