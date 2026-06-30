from __future__ import annotations

import pytest

from src.core.settings import Settings
from src.pages.shoofra_page import ShoofraPage


@pytest.fixture()
def shoofra(page, settings: Settings) -> ShoofraPage:
    return ShoofraPage(page, settings.base_url)
