from __future__ import annotations

import re
from collections.abc import Iterable

from playwright.sync_api import Error as PlaywrightError, Locator, Page, expect

from src.core.reporting import report_step
from src.pages.base_page import BasePage


CORE_NAVIGATION_LINKS: tuple[tuple[str, str], ...] = (
    ("SALE", "/shop/sale/"),
    ("נעלי נשים", "/shop/woman/shoes/"),
    ("נעלי גברים", "/shop/man/shoes/"),
    ("תיקים", "/shop/bags/"),
    ("NEW IN", "/shop/new-collection/"),
    ("מותגים", "/brands/"),
    ("גיפטקארד", "/gift-card/"),
    ("החנויות שלנו", "/store-locations/"),
    ("לעבוד איתנו", "/wanted/"),
)


FAST_RECRUITER_HEADER_LINKS: tuple[tuple[str, str], ...] = (
    ("SALE - UP TO 30%", "/shop/sale/"),
    ("נעלי נשים", "/shop/woman/shoes/"),
    ("נעלי גברים", "/shop/man/shoes/"),
    ("תיקים", "/shop/bags/"),
    ("גרביים", "/shop/socks/"),
    ("New In", "/shop/new-collection/"),
    ("מותגים", "/brands/"),
    ("גיפטקארד", "/gift-card/"),
    ("לעבוד איתנו", "/wanted/"),
)


CATEGORY_PAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("shop/sale/", ("SALE", "סינון לפי", "פריטים")),
    ("shop/woman/shoes/", ("נעלי נשים", "סינון לפי", "פריטים")),
    ("shop/man/shoes/", ("נעלי גברים", "סינון לפי", "פריטים")),
    ("shop/bags/", ("תיקים", "סינון לפי", "פריטים")),
    ("shop/new-collection/", ("NEW IN", "סינון לפי", "פריטים")),
    ("brands/", ("מותגים", "A.S. 98", "Jeffrey Campbell")),
)


SERVICE_PAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("shipping-and-returns/", ("משלוחים", "החלפות", "החזרות")),
    ("faq/", ("שאלות", "תשובות")),
    ("contact-us/", ("דברו אלינו", "שירות לקוחות")),
    ("accessibility-statement/", ("הצהרת נגישות", "שופרא")),
    ("terms/", ("תקנון", "שופרא")),
    ("privacy-policy/", ("מדיניות פרטיות", "קוקיז")),
    ("about/", ("אודות", "שופרא")),
    ("store-locations/", ("החנויות שלנו", "שופרא")),
    ("customer-club/", ("מועדון לקוחות", "שופרא")),
    ("gift-card/", ("גיפטקארד", "שופרא")),
)

SERVICE_PAGE_LINK_TEXT: dict[str, str] = {
    "shipping-and-returns/": "משלוחים, החלפות והחזרות",
    "faq/": "שאלות ותשובות",
    "contact-us/": "דברו אלינו",
    "accessibility-statement/": "הצהרת נגישות",
    "terms/": "תקנון אתר ומועדון",
    "privacy-policy/": "מדיניות פרטיות וקוקיז",
    "about/": "אודות",
    "store-locations/": "החנויות שלנו",
    "customer-club/": "מועדון לקוחות",
    "gift-card/": "גיפטקארד",
}


PRODUCT_LINK_SELECTOR = ".product a[href*='/brands/'], li.product a[href*='/brands/'], .type-product a[href*='/brands/']"
PRODUCT_TILE_SELECTOR = ".product, li.product, .type-product"


class ShoofraPage(BasePage):
    BLOCK_TEXTS = (
        "security verification",
        "Just a moment",
        "Access denied",
    )

    def __init__(self, page: Page, base_url: str | None = None) -> None:
        super().__init__(page)
        self.base_url = (base_url or "https://www.shoofra.co.il/").rstrip("/")

    def url_for(self, path: str = "") -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}" if path else f"{self.base_url}/"

    def goto_url(self, url: str) -> None:
        last_error: Exception | None = None
        target_url = url.split("?")[0].rstrip("/")

        for attempt in range(3):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                if self.page.url.startswith("chrome-error://"):
                    raise AssertionError(f"Browser error page loaded while navigating to {url}.")
                return
            except (AssertionError, PlaywrightError) as error:
                last_error = error
                if self.page.url.split("?")[0].rstrip("/") == target_url and not self.page.url.startswith(
                    "chrome-error://"
                ):
                    return

                retryable = any(
                    text in str(error)
                    for text in (
                        "ERR_ABORTED",
                        "Timeout",
                        "net::ERR",
                        "Browser error page",
                    )
                )
                if not retryable or attempt == 2:
                    if self.page.url.split("?")[0].rstrip("/") == target_url:
                        return
                    raise

                self.page.wait_for_timeout(900 * (attempt + 1))

        if last_error is not None:
            raise last_error

    def open(self, path: str = "", *, expected_texts: Iterable[str] = ()) -> None:
        with report_step(f"Open Shoofra page: {path or 'home'}"):
            self.goto_url(self.url_for(path))
            self.assert_not_blocked()
            expect(self.locator("body")).to_be_visible()
            self.highlight_page_action(path or "Home page", "OPEN")
            self.assert_body_contains(*expected_texts)

    def assert_not_blocked(self) -> None:
        last_error: PlaywrightError | None = None
        for attempt in range(3):
            try:
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                except PlaywrightError:
                    # The live site can keep the frame busy even when the document is usable.
                    # Continue to body/title checks; those are the real signal we need here.
                    pass

                if self.page.url.startswith("chrome-error://"):
                    raise AssertionError("Shoofra navigation landed on a browser error page.")

                body_text = self.locator("body").inner_text(timeout=10000)
                title = self.page.title()
                if any(text.lower() in f"{title}\n{body_text}".lower() for text in self.BLOCK_TEXTS):
                    raise AssertionError("Shoofra blocked the automated browser session before the site loaded.")
                return
            except PlaywrightError as error:
                last_error = error
                if attempt == 2:
                    raise
                self.page.wait_for_timeout(700 * (attempt + 1))

        if last_error is not None:
            raise last_error

    def assert_body_contains(self, *texts: str) -> None:
        with report_step(f"Verify page text: {', '.join(texts)}"):
            body = self.locator("body")
            for text in texts:
                expect(body).to_contain_text(text)

    def assert_home_page_layout(self) -> None:
        self.assert_body_contains(
            "SALE",
            "נעלי נשים",
            "נעלי גברים",
            "תיקים",
            "מותגים",
            "מידע שימושי",
            "שירות לקוחות",
            "קנייה מאובטחת",
        )

    def assert_navigation_links(self) -> None:
        for link_text, href_fragment in CORE_NAVIGATION_LINKS:
            self.assert_link_destination(link_text, href_fragment)

    def _visible_link_with_destination(self, link_text: str, href_fragment: str) -> Locator:
        links = self.locator(f"a[href*='{href_fragment}']").filter(
            has_text=re.compile(re.escape(link_text), re.IGNORECASE)
        )
        if links.count() == 0:
            links = self.locator(f"a[href*='{href_fragment}']")

        return self._first_visible(links)

    def _first_visible(self, locator: Locator) -> Locator:
        for index in range(locator.count()):
            candidate = locator.nth(index)
            try:
                if candidate.is_visible(timeout=700):
                    return candidate
            except Exception:
                continue

        return locator.first

    def navigate_main_menu_with_highlights(self) -> None:
        with report_step("Click through the main navigation with visible highlights"):
            for link_text, href_fragment in CORE_NAVIGATION_LINKS:
                self.open()
                nav_link = self._visible_link_with_destination(link_text, href_fragment)
                expect(nav_link).to_be_attached()
                nav_href = nav_link.get_attribute("href")
                position = self.highlight_locator(nav_link, f"Main navigation: {link_text}", "CLICK")
                try:
                    if position is None:
                        nav_link.click(timeout=5000)
                    else:
                        nav_link.click(timeout=5000, position=position)
                except Exception:
                    assert nav_href, f"No href was available for navigation link: {link_text}"
                    self.goto_url(nav_href)
                self.page.wait_for_load_state("domcontentloaded")
                self.assert_not_blocked()
                expect(self.page).to_have_url(re.compile(re.escape(href_fragment), re.IGNORECASE))
                self.assert_current_category_page_if_known(href_fragment)
                if self._demo_highlight_enabled():
                    self.page.wait_for_timeout(self._demo_action_pause_ms())

    def navigate_fast_recruiter_headers(self) -> None:
        with report_step("Click through the recruiter-facing header navigation"):
            self.open()
            for link_text, href_fragment in FAST_RECRUITER_HEADER_LINKS:
                nav_link = self._visible_link_with_destination(link_text, href_fragment)
                expect(nav_link).to_be_attached()
                nav_href = nav_link.get_attribute("href") or self.url_for(href_fragment)
                position = self.highlight_locator(nav_link, f"Header: {link_text}", "CLICK")
                try:
                    if position is None:
                        nav_link.click(timeout=5000)
                    else:
                        nav_link.click(timeout=5000, position=position)
                    self.page.wait_for_load_state("domcontentloaded")
                except Exception:
                    self.goto_url(nav_href)
                self.assert_not_blocked()
                expect(self.page).to_have_url(re.compile(re.escape(href_fragment), re.IGNORECASE))
                self.show_demo_pass(f"Header opened: {link_text}")

    def assert_current_category_page_if_known(self, href_fragment: str) -> None:
        normalized_fragment = href_fragment.strip("/")
        for path, expected_texts in CATEGORY_PAGES:
            if path.strip("/") == normalized_fragment:
                self.assert_body_contains(*expected_texts)
                if path != "brands/":
                    self.assert_product_listing()
                return

    def navigate_footer_service_pages_with_highlights(self) -> None:
        with report_step("Click through footer service pages with visible highlights"):
            for path, expected_texts in SERVICE_PAGES:
                self.open()
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.page.wait_for_timeout(350)
                link_text = SERVICE_PAGE_LINK_TEXT[path]
                footer_links = self.locator("footer a, .edgtf-page-footer a, a").filter(
                    has_text=re.compile(re.escape(link_text), re.IGNORECASE)
                )
                footer_link = self._first_visible(footer_links)
                fallback_url = self.url_for(path)
                try:
                    expect(footer_link).to_be_attached()
                    footer_href = footer_link.get_attribute("href") or fallback_url
                    position = self.highlight_locator(footer_link, f"Footer page: {link_text}", "CLICK")
                    if position is None:
                        footer_link.click(timeout=5000)
                    else:
                        footer_link.click(timeout=5000, position=position)
                    self.page.wait_for_load_state("domcontentloaded")
                    if self.page.url == "about:blank" or self.page.url.startswith("chrome-error://"):
                        self.goto_url(footer_href)
                except Exception:
                    self.highlight_page_action(f"Footer page: {link_text}", "OPEN")
                    self.goto_url(fallback_url)

                self.assert_not_blocked()
                expect(self.locator("body")).to_be_visible()
                self.assert_body_contains(*expected_texts)

    def assert_footer_service_links(self) -> None:
        for link_text in (
            "משלוחים, החלפות והחזרות",
            "שאלות ותשובות",
            "דברו אלינו",
            "הצהרת נגישות",
            "תקנון אתר ומועדון",
            "מדיניות פרטיות וקוקיז",
            "אודות",
            "מועדון לקוחות",
        ):
            expect(self.locator("a").filter(has_text=link_text).first).to_be_visible()

    def assert_link_destination(self, link_text: str, href_fragment: str) -> None:
        with report_step(f"Verify link destination: {link_text} -> {href_fragment}"):
            links = self.locator("a").filter(has_text=re.compile(re.escape(link_text), re.IGNORECASE))
            hrefs = [href for href in links.evaluate_all("(nodes) => nodes.map((node) => node.href)") if href]
            assert any(href_fragment.lower() in href.lower() for href in hrefs), (
                f"Expected a '{link_text}' link containing '{href_fragment}'. Found: {hrefs}"
            )

    def _try_search_through_ui(self, term: str) -> bool:
        try:
            self.open()
            openers = self.locator(
                "a.edgtf-search-opener, button.edgtf-search-opener, .edgtf-search-opener, "
                "a[href='#search'], button[aria-label*='search' i]"
            )
            if openers.count() == 0:
                return False

            opener = self._first_visible(openers)
            if not opener.is_visible(timeout=1000):
                return False

            self.click_visible(opener, "Open search")
            search_fields = self.locator("input[type='search'], input[name='s'], input.edgtf-search-field")
            search_field = self._first_visible(search_fields)
            if not search_field.is_visible(timeout=3000):
                return False

            self.fill_visible(search_field, "Search input", term)
            self.highlight_locator(search_field, f"Submit search: {term}", "ENTER")
            search_field.press("Enter")
            self.page.wait_for_load_state("domcontentloaded")
            self.assert_not_blocked()
            if "s=" not in self.page.url and "post_type=product" not in self.page.url:
                return False
            return True
        except Exception:
            return False

    def search(self, term: str) -> None:
        with report_step(f"Open search results for: {term}"):
            if self._try_search_through_ui(term):
                return

            self.highlight_page_action(f"Search products: {term}", "SEARCH")
            self.goto_url(self.url_for(f"?s={term}&post_type=product"))
            self.assert_not_blocked()
            expect(self.locator("body")).to_contain_text(f"תוצאות חיפוש עבור \"{term}\"")

    def assert_product_listing(self) -> None:
        with report_step("Verify product listing"):
            expect(self.locator(PRODUCT_TILE_SELECTOR).first).to_be_visible()
            self.assert_body_contains("סינון לפי", "פריטים")

    def open_first_listed_product(self) -> None:
        with report_step("Open first listed product"):
            product_link = self.locator(PRODUCT_LINK_SELECTOR).first
            expect(product_link).to_be_attached()
            product_href = product_link.get_attribute("href")
            assert product_href, "No product link href was available in the listing."
            position = self.highlight_locator(product_link, "Open first product", "CLICK")
            try:
                if position is None:
                    product_link.click(timeout=5000)
                else:
                    product_link.click(timeout=5000, position=position)
                self.page.wait_for_load_state("domcontentloaded")
            except Exception:
                self.goto_url(product_href)
            self.assert_not_blocked()
            self.assert_product_detail_page()

    def assert_product_detail_page(self) -> None:
        self.assert_body_contains("צבע", "מידה", "הוספה לסל", "מידע נוסף", "משלוחים והחזרות")
        expect(self.locator("select[name='attribute_pa_size']").first).to_be_visible()

    def _first_available_size_value(self) -> str | None:
        size_select = self.locator("select[name='attribute_pa_size']").first
        options = size_select.locator("option").all()
        return next(
            (
                option.get_attribute("value")
                for option in options
                if option.get_attribute("value") and option.get_attribute("disabled") is None
            ),
            None,
        )

    def add_current_product_to_cart(self, label: str = "Current product") -> None:
        with report_step(f"Select size and add product to cart: {label}"):
            size_select = self.locator("select[name='attribute_pa_size']").first
            option_value = self._first_available_size_value()
            assert option_value is not None, "No selectable product size was available."
            self.select_visible(size_select, f"{label} size", option_value)
            add_button = self.locator("button.single_add_to_cart_button").first
            self.click_visible(add_button, f"Add {label} to cart")
            expect(self.locator("body")).to_contain_text("סל")

    def try_add_current_product_to_cart(self, label: str) -> bool:
        try:
            self.assert_product_detail_page()
            self.add_current_product_to_cart(label)
        except Exception:
            return False
        return True

    def product_links_from_current_listing(self, limit: int = 18) -> list[str]:
        with report_step(f"Collect up to {limit} product links"):
            links = self.locator(PRODUCT_LINK_SELECTOR)
            expect(links.first).to_be_attached()
            hrefs = links.evaluate_all(
                """
                (nodes) => [...new Set(nodes.map((node) => node.href).filter(Boolean))]
                """
            )
            return hrefs[:limit]

    def build_cart_with_products(self, minimum_count: int = 6) -> int:
        with report_step(f"Build cart with at least {minimum_count} products"):
            product_links: list[str] = []
            for category_path in ("shop/woman/shoes/", "shop/man/shoes/"):
                self.open(category_path)
                self.assert_product_listing()
                for product_href in self.product_links_from_current_listing(limit=minimum_count * 4):
                    if product_href not in product_links:
                        product_links.append(product_href)

            assert product_links, "No product links were available for the multi-product cart flow."

            added_count = 0
            for product_href in product_links:
                self.highlight_page_action(f"Open product candidate {added_count + 1}", "OPEN")
                self.goto_url(product_href)
                self.assert_not_blocked()
                if self.try_add_current_product_to_cart(f"Product {added_count + 1}"):
                    added_count += 1
                    self.open_cart()
                    confirmed_count = self.current_cart_item_count()
                    self.show_demo_pass(f"Cart currently has {confirmed_count} items")
                    if confirmed_count >= minimum_count:
                        return confirmed_count

            self.open_cart()
            confirmed_count = self.current_cart_item_count()
            assert confirmed_count >= minimum_count, (
                f"Expected at least {minimum_count} cart items, confirmed {confirmed_count} after "
                f"{added_count} add attempts."
            )
            return confirmed_count

    def build_cart_with_products_fast(self, minimum_count: int = 6) -> int:
        with report_step(f"Fast cart build with {minimum_count} products"):
            product_links: list[str] = []
            for category_path in ("shop/woman/shoes/", "shop/man/shoes/", "shop/sale/"):
                if len(product_links) >= minimum_count * 2:
                    break
                self.open(category_path)
                self.assert_product_listing()
                for product_href in self.product_links_from_current_listing(limit=minimum_count * 3):
                    if product_href not in product_links:
                        product_links.append(product_href)

            assert product_links, "No product links were available for the fast cart flow."

            added_count = 0
            confirmed_count = 0
            for product_href in product_links:
                self.highlight_page_action(f"Open product {added_count + 1}/{minimum_count}", "OPEN")
                self.goto_url(product_href)
                self.assert_not_blocked()
                if self.try_add_current_product_to_cart(f"Product {added_count + 1} of {minimum_count}"):
                    added_count += 1
                    self.show_demo_pass(f"Size selected and product added {added_count}/{minimum_count}")
                    if added_count % 2 == 0 or added_count >= minimum_count:
                        self.open_cart()
                        confirmed_count = self.current_cart_item_count()
                        self.show_demo_pass(f"Cart currently has {confirmed_count}/{minimum_count} items")
                        if confirmed_count >= minimum_count:
                            return confirmed_count

            self.open_cart()
            confirmed_count = self.current_cart_item_count()
            assert confirmed_count >= minimum_count, (
                f"Expected at least {minimum_count} cart items, confirmed {confirmed_count} "
                f"after {added_count} add attempts."
            )
            return self.assert_cart_contains_at_least(minimum_count)

    def open_cart(self) -> None:
        self.open("cart/", expected_texts=("סל",))

    def assert_cart_page(self) -> None:
        self.assert_body_contains("סל")

    def current_cart_item_count(self) -> int:
        rows = self.locator(".woocommerce-cart-form__cart-item, tr.cart_item")
        if rows.count() == 0:
            return 0
        quantities = self.locator(".woocommerce-cart-form__cart-item input.qty, tr.cart_item input.qty")
        if quantities.count() > 0:
            return sum(
                int(value)
                for value in quantities.evaluate_all(
                    "(nodes) => nodes.map((node) => node.value || node.getAttribute('value') || '0')"
                )
            )
        return rows.count()

    def assert_cart_contains_at_least(self, minimum_count: int) -> int:
        with report_step(f"Verify cart contains at least {minimum_count} items"):
            rows = self.locator(".woocommerce-cart-form__cart-item, tr.cart_item")
            expect(rows.first).to_be_visible()
            item_count = self.current_cart_item_count()
            assert item_count >= minimum_count, f"Expected at least {minimum_count} cart items, found {item_count}."
            self.highlight_page_action(f"Cart verified: {item_count} items", "PASS")
            return item_count

    def open_account_modal(self) -> None:
        with report_step("Open login/register modal"):
            opener = self.locator("a.edgtf-login-opener").first
            self.click_visible(opener, "Open account window")
            self.assert_body_contains("התחברות", "איפוס סיסמה", "פעם ראשונה באתר")
            expect(self.locator(".edgtf-login-form").first).to_be_visible()
            expect(self.locator("#user_login_name")).to_be_visible()
            expect(self.locator("#user_login_password")).to_be_visible()

    def assert_registration_fields(self) -> None:
        self.assert_body_contains("שם פרטי", "שם משפחה")
        for selector in (
            "input[name='first_name']",
            "input[name='last_name']",
            "input[name='email']",
            "input[name='phone']",
            "input[name='password']",
            "input[name='repeat_password']",
        ):
            expect(self.locator(selector).first).to_be_attached()

    def fill_login_form_without_submit(self) -> None:
        with report_step("Fill login form without submitting real credentials"):
            email = self.locator("#user_login_name").first
            password = self.locator("#user_login_password").first
            remember_me = self.locator("#rememberme").first

            if not email.is_visible():
                login_tab = self.locator("a[href='#edgtf-login-content'], #ui-id-1").first
                self.click_visible(login_tab, "Open login form")
                expect(email).to_be_visible()

            self.fill_visible(email, "Login email", "demo.recruiter@example.com")
            self.fill_visible(password, "Login password", "DemoPassword!234")
            if not remember_me.is_checked():
                self.check_visible(remember_me, "Remember me")

            expect(email).to_have_value("demo.recruiter@example.com")
            expect(password).to_have_value("DemoPassword!234")

    def fill_password_reset_without_submit(self) -> None:
        with report_step("Fill password reset form without submitting"):
            reset_email = self.locator("#user_reset_password_login").first
            if not reset_email.is_visible():
                reset_link = self.locator("a[href='#edgtf-recover-content'], a.edgtf-login-action-btn").filter(
                    has_text=re.compile("שכחת|סיסמה")
                ).first
                if not reset_link.is_visible():
                    login_tab = self.locator("a[href='#edgtf-login-content'], #ui-id-1").first
                    self.click_visible(login_tab, "Back to login form")
                self.click_visible(reset_link, "Open password reset")
            expect(reset_email).to_be_visible()
            self.fill_visible(reset_email, "Password reset email", "demo.recruiter@example.com")
            expect(reset_email).to_have_value("demo.recruiter@example.com")

    def select_registration_shoe_size(self, value: str) -> None:
        with report_step(f"Select registration shoe size: {value}"):
            size_select = self.locator("#shooes_size").first
            visible_size_control = self.locator("button").filter(has_text=re.compile("בחר מידה")).first
            self.highlight_locator(visible_size_control, f"Shoe size {value}", "SELECT")
            size_select.evaluate(
                """
                (select, value) => {
                  for (const option of select.options) {
                    option.selected = option.value === value;
                  }
                  select.dispatchEvent(new Event("change", { bubbles: true }));
                  select.dispatchEvent(new Event("input", { bubbles: true }));
                }
                """,
                value,
            )
            selected_values = size_select.evaluate("(select) => [...select.selectedOptions].map((option) => option.value)")
            assert value in selected_values, f"Expected shoe size {value} to be selected, found {selected_values}."

    def fill_registration_form_without_submit(self) -> None:
        with report_step("Fill registration form without creating a real account"):
            self.assert_registration_fields()
            first_name = self.locator("input[name='first_name']").first
            if not first_name.is_visible():
                register_tab = self.locator("a[href='#edgtf-register-content'], #ui-id-3").first
                self.click_visible(register_tab, "Open registration form")
            expect(first_name).to_be_visible()

            self.fill_visible(first_name, "Registration first name", "QA")
            self.fill_visible(self.locator("input[name='last_name']").first, "Registration last name", "Candidate")
            self.fill_visible(self.locator("input[name='tz']").first, "Registration ID number", "123456789")
            self.fill_visible(self.locator("input[name='email']").first, "Registration email", "qa.candidate@example.com")
            self.fill_visible(self.locator("input[name='phone']").first, "Registration phone", "0501234567")
            self.select_visible(self.locator("select[name='birthday_year']").first, "Birth year", "1990")
            self.select_visible(self.locator("select[name='birthday_month']").first, "Birth month", "06")
            self.select_visible(self.locator("select[name='birthday_day']").first, "Birth day", "15")
            self.fill_visible(self.locator("#city").first, "Registration city", "Tel Aviv")
            self.select_index_visible(self.locator("select[name='gender']").first, "Gender", 2)
            self.select_registration_shoe_size("38")
            self.fill_visible(self.locator("#password").first, "Registration password", "DemoPassword!234")
            self.fill_visible(self.locator("input[name='repeat_password']").first, "Confirm password", "DemoPassword!234")

            expect(self.locator("input[name='first_name']").first).to_have_value("QA")
            expect(self.locator("input[name='last_name']").first).to_have_value("Candidate")
            expect(self.locator("input[name='email']").first).to_have_value("qa.candidate@example.com")
            expect(self.locator("#password").first).to_have_value("DemoPassword!234")

    def assert_external_social_links(self) -> None:
        for href_fragment in ("instagram", "facebook", "tiktok", "youtube", "spotify"):
            assert self.locator(f"a[href*='{href_fragment}']").count() > 0, (
                f"Expected a social link containing '{href_fragment}'."
            )
