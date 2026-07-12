from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    base_url: str = field(default_factory=lambda: os.getenv("BASE_URL", "https://www.shoofra.co.il/"))
    browser_name: str = field(default_factory=lambda: os.getenv("BROWSER", "chromium"))
    headless: bool = field(default_factory=lambda: _get_bool("HEADLESS", False))
    start_maximized: bool = field(default_factory=lambda: _get_bool("START_MAXIMIZED", True))
    slow_mo_ms: int = field(default_factory=lambda: _get_int("SLOW_MO_MS", 100))
    viewport_width: int = field(default_factory=lambda: _get_int("VIEWPORT_WIDTH", 2560))
    viewport_height: int = field(default_factory=lambda: _get_int("VIEWPORT_HEIGHT", 1440))
    browser_window_width: int = field(default_factory=lambda: _get_int("BROWSER_WINDOW_WIDTH", 2560))
    browser_window_height: int = field(default_factory=lambda: _get_int("BROWSER_WINDOW_HEIGHT", 1440))
    default_timeout_ms: int = field(default_factory=lambda: _get_int("DEFAULT_TIMEOUT_MS", 15000))
    test_pause_ms: int = field(default_factory=lambda: _get_int("TEST_PAUSE_MS", 120))
    demo_highlight: bool = field(default_factory=lambda: _get_bool("DEMO_HIGHLIGHT", True))
    demo_zoom_percent: int = field(default_factory=lambda: _get_int("DEMO_ZOOM_PERCENT", 100))
    demo_action_pause_ms: int = field(default_factory=lambda: _get_int("DEMO_ACTION_PAUSE_MS", 120))
    trace_on_failure: bool = field(default_factory=lambda: _get_bool("TRACE_ON_FAILURE", True))
    video_on_failure: bool = field(default_factory=lambda: _get_bool("VIDEO_ON_FAILURE", False))
    demo_final_screenshot: bool = field(default_factory=lambda: _get_bool("DEMO_FINAL_SCREENSHOT", True))


def get_settings() -> Settings:
    return Settings()
