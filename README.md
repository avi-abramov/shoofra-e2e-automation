# Shoofra E2E Automation

Recruiter-ready Playwright + Pytest automation for the live Shoofra store:

```text
https://www.shoofra.co.il/
```

The project is intentionally safe for a production retail site: it fills account forms with demo data, selects product sizes, and builds carts, but it does not submit registration, login, payment, or a real order.

## What This Project Covers

- Home page availability and core storefront links
- Login, registration, and password reset forms without submission
- Header navigation from the visible Shoofra menu
- Catalog listing and product detail validation
- Size selection before add-to-cart
- Fast cart smoke with 2 products
- Visible recruiter demo with 6 products
- Allure reporting, screenshots, traces on failure, and GitHub Actions smoke CI

## Test Layout

```text
tests/
|-- test_account_forms.py
|-- test_cart_smoke.py
|-- test_catalog_product_smoke.py
|-- test_fast_recruiter_journey.py
|-- test_homepage_smoke.py
`-- test_navigation_smoke.py
```

The suite has two modes:

- Fast smoke tests: split by feature, short, better for CI and daily confidence.
- Visible demo test: one polished end-to-end journey for recruiters.

## Run Visible Demo

```powershell
.\present.cmd
```

This opens a real browser and shows action markers, step labels, PASS labels, and a final summary.

## Run Fast Smoke Suite

```powershell
.\test-fast.cmd
```

Default smoke run:

```text
pytest -q tests -m "smoke and not demo"
```

## Run Everything

```powershell
.\test-all.cmd
```

## Useful Direct Commands

```powershell
python -m pytest -q tests -m demo
python -m pytest -q tests/test_cart_smoke.py
python -m pytest -q tests -m "account or catalog"
```

## Local Setup

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Reports And Artifacts

Generated output is ignored by git:

```text
allure-results/
artifacts/screenshots/
artifacts/traces/
artifacts/demo/
```

If the Allure CLI is installed, open the latest report with:

```powershell
allure serve allure-results
```

## Demo Settings

The visible demo defaults are tuned to be clear but not too slow:

```text
SLOW_MO_MS=100
TEST_PAUSE_MS=120
DEMO_ACTION_PAUSE_MS=120
VIEWPORT_WIDTH=2560
VIEWPORT_HEIGHT=1440
```

Change them in `.env` or pass values to `present.ps1`.

## GitHub Actions

The workflow in `.github/workflows/e2e.yml` runs the fast smoke suite on push, pull request, or manual dispatch.

CI intentionally excludes the visible demo because it is designed for a headed presentation run.

## Notes

- Shoofra is a live site, so product availability and stock can change.
- Product links are collected dynamically from live listings.
- Unavailable products are skipped during cart building.
- The project avoids checkout and payment by design.
