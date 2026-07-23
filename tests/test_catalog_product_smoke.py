from __future__ import annotations

import pytest

from src.pages.shoofra_page import ShoofraPage


pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.catalog]


def test_catalog_product_detail_supports_size_selection(shoofra: ShoofraPage):
    shoofra.open_category_and_first_product("shop/new-collection/")
    shoofra.assert_product_detail_page()
