from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pytest

from src.core.settings import PROJECT_ROOT, Settings


ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"

try:
    import allure
except ImportError:  # pragma: no cover - fallback keeps pytest usable before install.
    allure = None


@contextmanager
def report_step(title: str) -> Iterator[None]:
    if allure is None:
        yield
        return

    with allure.step(title):
        yield


def attach_png(path: Path, name: str) -> None:
    if allure is None or not path.exists():
        return

    allure.attach.file(
        str(path),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def attach_file(path: Path, name: str) -> None:
    if allure is None or not path.exists():
        return

    allure.attach.file(str(path), name=name)


def attach_text(name: str, body: str) -> None:
    if allure is None:
        return

    allure.attach(
        body,
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


def apply_test_metadata(item: pytest.Item) -> None:
    if allure is None:
        return

    test_name = item.name.replace("_", " ").title()
    allure.dynamic.epic("Shoofra Store Automation")
    allure.dynamic.suite("Recruiter Ready E2E Suite")
    allure.dynamic.feature(_feature_for_test(item.name))
    allure.dynamic.story(_story_for_test(item))
    allure.dynamic.title(test_name)
    allure.dynamic.description(_description_for_test(item.name))
    allure.dynamic.severity(_severity_for_test(item))
    for marker in ("smoke", "demo", "account", "navigation", "catalog", "cart", "storefront"):
        if item.get_closest_marker(marker):
            allure.dynamic.tag(marker)


def write_allure_environment(settings: Settings) -> None:
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    environment = {
        "Project": "Shoofra E2E Automation Framework",
        "Base URL": settings.base_url,
        "Browser": settings.browser_name,
        "Headless": str(settings.headless),
        "Start Maximized": str(settings.start_maximized),
        "Slow Motion MS": str(settings.slow_mo_ms),
        "Test Pause MS": str(settings.test_pause_ms),
        "Trace On Failure": str(settings.trace_on_failure),
        "Video On Failure": str(settings.video_on_failure),
        "Demo Final Screenshot": str(settings.demo_final_screenshot),
    }

    (ALLURE_RESULTS_DIR / "environment.properties").write_text(
        "\n".join(f"{key}={value}" for key, value in environment.items()),
        encoding="utf-8",
    )


def write_allure_executor() -> None:
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    server_url = os.getenv("GITHUB_SERVER_URL", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    executor = {
        "name": "GitHub Actions" if os.getenv("GITHUB_ACTIONS") else "Local machine",
        "type": "github" if os.getenv("GITHUB_ACTIONS") else "local",
        "buildName": os.getenv("GITHUB_RUN_NUMBER", "local"),
        "buildUrl": f"{server_url}/{repository}/actions/runs/{run_id}" if server_url and repository and run_id else "",
        "reportName": "Shoofra E2E Automation Report",
    }

    (ALLURE_RESULTS_DIR / "executor.json").write_text(
        json.dumps(executor, indent=2),
        encoding="utf-8",
    )


def write_allure_categories() -> None:
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    categories = [
        {
            "name": "Site Availability",
            "matchedStatuses": ["failed", "broken"],
            "messageRegex": ".*blocked.*|.*security verification.*|.*Timeout.*",
        },
        {
            "name": "UI Assertion Failure",
            "matchedStatuses": ["failed"],
            "traceRegex": ".*AssertionError.*",
        },
    ]

    (ALLURE_RESULTS_DIR / "categories.json").write_text(
        json.dumps(categories, indent=2),
        encoding="utf-8",
    )


def _feature_for_test(test_name: str) -> str:
    if "homepage" in test_name or "home_page" in test_name:
        return "Homepage"
    if "navigation" in test_name or "footer" in test_name:
        return "Navigation"
    if "category" in test_name or "filter" in test_name:
        return "Catalog"
    if "search" in test_name:
        return "Search"
    if "product" in test_name or "cart" in test_name:
        return "Product and Cart"
    if "account" in test_name or "login" in test_name or "register" in test_name:
        return "Account"
    if "service" in test_name or "policy" in test_name or "stores" in test_name:
        return "Service Pages"
    return "Storefront"


def _story_for_test(item: pytest.Item) -> str:
    if item.get_closest_marker("negative"):
        return "Negative validation"
    if item.get_closest_marker("demo"):
        return "Visible recruiter demo"
    if item.get_closest_marker("smoke"):
        return "Fast confidence check"
    return "Customer journey"


def _severity_for_test(item: pytest.Item) -> str:
    if item.get_closest_marker("demo") or item.get_closest_marker("cart"):
        return "critical"
    if item.get_closest_marker("smoke"):
        return "normal"
    return "minor"


def _description_for_test(test_name: str) -> str:
    descriptions = {
        "test_fast_recruiter_shoofra_journey": (
            "Visible end-to-end recruiter demo: safe account form filling, header navigation, "
            "size selection, six-product cart build, and final cart verification."
        ),
        "test_homepage_core_links_are_available": (
            "Checks the live home page loads, exposes the expected header links, and keeps social links available."
        ),
        "test_account_forms_can_be_filled_without_submit": (
            "Validates login, registration, and password reset fields with safe demo data and no submission."
        ),
        "test_header_navigation_pages_load_directly": (
            "Opens the main header destinations directly to verify every recruiter-visible section is reachable."
        ),
        "test_catalog_product_detail_supports_size_selection": (
            "Verifies a product listing can open a product detail page with available size controls."
        ),
        "test_cart_smoke_adds_two_sized_products": (
            "Builds a short cart with two sized products as a fast add-to-cart confidence check."
        ),
    }
    return descriptions.get(test_name, "Shoofra live-site automation coverage.")
