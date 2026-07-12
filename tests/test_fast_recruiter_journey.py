from __future__ import annotations

import pytest

from src.pages.shoofra_page import ShoofraPage


"""Fast end-to-end demo kept in one file because it is one recruiter-facing journey."""

pytestmark = pytest.mark.e2e


@pytest.mark.smoke
@pytest.mark.demo
def test_fast_recruiter_shoofra_journey(shoofra: ShoofraPage):
    total_steps = 4

    shoofra.show_demo_step(1, total_steps, "Home, registration, and login forms")
    shoofra.open()
    shoofra.show_demo_notice(
        "Fast live-site demo",
        [
            "Registration and login forms are filled but not submitted.",
            "Header navigation is checked through the visible top menu.",
            "Six products are added with size selection before checkout.",
        ],
    )
    shoofra.open_account_modal()
    shoofra.assert_registration_fields()
    shoofra.fill_registration_form_without_submit()
    shoofra.fill_login_form_without_submit()
    shoofra.show_demo_pass("Registration and login forms filled safely")

    shoofra.show_demo_step(2, total_steps, "Header navigation from the screenshot")
    shoofra.navigate_fast_recruiter_headers()
    shoofra.show_demo_pass("All visible header links opened")

    shoofra.show_demo_step(3, total_steps, "Select sizes and add six products")
    final_count = shoofra.build_cart_with_products_fast(minimum_count=6)
    shoofra.show_demo_pass(f"Six-product cart verified: {final_count} items")

    shoofra.show_demo_step(4, total_steps, "Finish on verified cart")
    shoofra.show_demo_summary(
        [
            "Registration form filled safely",
            "Login form filled safely",
            "Screenshot header links covered",
            "Sizes selected for six products",
            f"Cart verified with {final_count} items",
            "No real registration, payment, or order submitted",
        ]
    )
