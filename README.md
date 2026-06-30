# Shoofra Fast E2E Demo

Fast recruiter-facing Playwright automation for:

```text
https://www.shoofra.co.il/
```

This project now keeps one focused live-site demo instead of many slow page-by-page checks.
It intentionally stops before real account creation, payment, or order submission.

## Current Flow

The single demo test covers:

- Open Shoofra home page
- Fill registration form without submitting
- Fill login form without submitting
- Click the main header links shown in the site navigation:
  `SALE`, women shoes, men shoes, bags, socks, `New In`, brands, gift card, and careers
- Open product listings dynamically
- Select a size for each product
- Add 6 products to the cart
- Open the cart once at the end
- Verify the cart contains at least 6 items
- Show visible click markers, step labels, PASS labels, and a final summary

## Run Visible Demo

```powershell
.\present.cmd
```

Default visible speed is intentionally faster now:

```text
SLOW_MO_MS=180
TEST_PAUSE_MS=250
DEMO_ACTION_PAUSE_MS=220
```

## Run Fast Headless

```powershell
.\test-fast.cmd
```

## Project Structure

```text
.
|-- present.cmd
|-- present.ps1
|-- test-fast.cmd
|-- test-fast.ps1
|-- src
|   |-- core
|   |   |-- fixtures.py
|   |   |-- reporting.py
|   |   `-- settings.py
|   `-- pages
|       |-- base_page.py
|       `-- shoofra_page.py
`-- tests
    |-- conftest.py
    `-- test_ordered_recruiter_demo_journey.py
```

## Notes

- Shoofra is a live site, not a demo sandbox.
- Registration and login are filled only, not submitted.
- Checkout/payment is not performed.
- Product and stock availability can change, so products are collected dynamically from live listings.
