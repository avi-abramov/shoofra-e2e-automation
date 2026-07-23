from __future__ import annotations

import pytest

from src.pages.shoofra_page import ShoofraPage


pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.storefront]


def test_homepage_core_links_are_available(shoofra: ShoofraPage):
    shoofra.open()
    shoofra.assert_page_is_usable()
    shoofra.assert_recruiter_header_links_present()
    shoofra.assert_external_social_links()
