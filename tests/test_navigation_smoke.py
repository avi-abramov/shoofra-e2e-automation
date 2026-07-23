from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from src.pages.shoofra_page import FAST_RECRUITER_HEADER_LINKS, ShoofraPage


pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.navigation]


def test_header_navigation_pages_load_directly(shoofra: ShoofraPage):
    for _label, href_fragment in FAST_RECRUITER_HEADER_LINKS:
        shoofra.open(href_fragment)
        expect(shoofra.page).to_have_url(re.compile(re.escape(href_fragment), re.IGNORECASE))
        shoofra.assert_page_is_usable(minimum_text_length=40)
