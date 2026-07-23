from __future__ import annotations

import pytest

from src.pages.shoofra_page import ShoofraPage


pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.cart]


def test_cart_smoke_adds_two_sized_products(shoofra: ShoofraPage):
    item_count = shoofra.build_cart_with_products_fast(minimum_count=2)
    assert item_count >= 2
