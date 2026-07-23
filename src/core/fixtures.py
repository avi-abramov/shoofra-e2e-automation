from __future__ import annotations

import re
from pathlib import Path
from time import sleep

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from src.core.reporting import (
    attach_file,
    apply_test_metadata,
    attach_png,
    attach_text,
    write_allure_categories,
    write_allure_environment,
    write_allure_executor,
)
from src.core.settings import PROJECT_ROOT, Settings, get_settings


ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
DEMO_SCREENSHOTS_DIR = ARTIFACTS_DIR / "demo"
TRACES_DIR = ARTIFACTS_DIR / "traces"
VIDEOS_DIR = ARTIFACTS_DIR / "videos"


def _safe_artifact_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "artifact"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(autouse=True)
def allure_metadata(request: pytest.FixtureRequest) -> None:
    apply_test_metadata(request.node)


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, settings: Settings) -> Browser:
    browser_type = getattr(playwright_instance, settings.browser_name, None)
    if browser_type is None:
        raise ValueError(f"Unsupported browser '{settings.browser_name}'. Use chromium, firefox, or webkit.")

    launch_options = {
        "headless": settings.headless,
        "slow_mo": settings.slow_mo_ms,
    }
    if settings.browser_name == "chromium":
        launch_args = [f"--window-size={settings.browser_window_width},{settings.browser_window_height}"]
        if settings.start_maximized:
            launch_args.append("--start-maximized")
        launch_options["args"] = launch_args

    browser = browser_type.launch(**launch_options)
    yield browser
    browser.close()


@pytest.fixture()
def context(browser: Browser, settings: Settings, request: pytest.FixtureRequest) -> BrowserContext:
    context_options = {
        "base_url": settings.base_url,
    }
    if settings.start_maximized and settings.browser_name == "chromium":
        context_options["no_viewport"] = True
    else:
        context_options["viewport"] = {
            "width": settings.viewport_width,
            "height": settings.viewport_height,
        }

    if settings.video_on_failure:
        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        context_options["record_video_dir"] = VIDEOS_DIR
        context_options["record_video_size"] = {
            "width": settings.viewport_width,
            "height": settings.viewport_height,
        }

    context = browser.new_context(**context_options)
    context.set_default_timeout(settings.default_timeout_ms)

    if settings.trace_on_failure:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if settings.trace_on_failure:
        try:
            if failed:
                TRACES_DIR.mkdir(parents=True, exist_ok=True)
                trace_path = TRACES_DIR / f"{_safe_artifact_name(request.node.name)}.zip"
                context.tracing.stop(path=trace_path)
                attach_file(trace_path, "Playwright trace")
            else:
                context.tracing.stop()
        except Exception as error:
            attach_text("Trace capture error", str(error))

    context.close()


@pytest.fixture()
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Page:
    settings = request.getfixturevalue("settings")
    page = context.new_page()
    browser_events: list[str] = []
    page.on("console", lambda message: browser_events.append(f"{message.type}: {message.text}"))
    page.on("pageerror", lambda error: browser_events.append(f"pageerror: {error}"))

    if settings.demo_zoom_percent != 100:
        page.add_init_script(
            f"""
            (() => {{
              const zoomPercent = {settings.demo_zoom_percent};
              const applyZoom = () => {{
                if (document.documentElement) {{
                  document.documentElement.style.zoom = `${{zoomPercent}}%`;
                }}
              }};
              applyZoom();
              window.addEventListener('DOMContentLoaded', applyZoom);
              window.addEventListener('load', applyZoom);
            }})();
            """
        )
    yield page

    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    passed = hasattr(request.node, "rep_call") and request.node.rep_call.passed
    artifact_name = _safe_artifact_name(request.node.name)

    if failed:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        screenshot_path = SCREENSHOTS_DIR / f"{artifact_name}.png"
        try:
            page.screenshot(path=screenshot_path, full_page=True)
            attach_png(screenshot_path, "Failure screenshot")
        except Exception as error:
            attach_text("Failure screenshot error", str(error))
        try:
            attach_text("Current URL", page.url)
            attach_text("Page title", page.title())
            attach_text("Page HTML", page.locator("body").inner_html(timeout=3000)[:20000])
        except Exception as error:
            attach_text("Failure page snapshot error", str(error))
        if browser_events:
            attach_text("Browser console and page errors", "\n".join(browser_events[-80:]))

    if passed and request.node.get_closest_marker("demo") and settings.demo_final_screenshot:
        DEMO_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        screenshot_path = DEMO_SCREENSHOTS_DIR / f"{artifact_name}.png"
        try:
            page.screenshot(path=screenshot_path, full_page=True)
            attach_png(screenshot_path, "Demo final screenshot")
        except Exception as error:
            attach_text("Demo final screenshot error", str(error))

    if settings.test_pause_ms > 0:
        sleep(settings.test_pause_ms / 1000)

    video = page.video
    page.close()
    if settings.video_on_failure and video is not None:
        try:
            video_path = Path(video.path())
            if failed:
                attach_file(video_path, "Failure video")
            elif video_path.exists():
                video_path.unlink()
        except Exception as error:
            attach_text("Video capture error", str(error))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    settings = get_settings()
    write_allure_environment(settings)
    write_allure_executor()
    write_allure_categories()
