from __future__ import annotations

import json
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
    allure.dynamic.feature(_feature_for_test(item.name))
    allure.dynamic.story("Negative validation" if item.get_closest_marker("negative") else "Customer journey")
    allure.dynamic.title(test_name)


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
