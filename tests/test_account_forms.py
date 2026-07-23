from __future__ import annotations

import pytest

from src.pages.shoofra_page import ShoofraPage


pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.account]


def test_account_forms_can_be_filled_without_submit(shoofra: ShoofraPage):
    shoofra.open()
    shoofra.open_account_modal()
    shoofra.assert_registration_fields()
    shoofra.fill_registration_form_without_submit()
    shoofra.fill_login_form_without_submit()
    shoofra.fill_password_reset_without_submit()
