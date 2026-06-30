from __future__ import annotations

import os

from playwright.sync_api import Locator, Page, expect


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, path: str = "/") -> None:
        self.page.goto(path, wait_until="domcontentloaded")

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def assert_title_contains(self, value: str) -> None:
        expect(self.page).to_have_title(value)

    def _demo_highlight_enabled(self) -> bool:
        return os.getenv("DEMO_HIGHLIGHT", "true").strip().lower() in {"1", "true", "yes", "on"}

    def _demo_action_pause_ms(self) -> int:
        return int(os.getenv("DEMO_ACTION_PAUSE_MS", "450"))

    def highlight_locator(self, locator: Locator, label: str, action: str = "ACTION") -> dict[str, float] | None:
        if not self._demo_highlight_enabled():
            return None

        pause_ms = self._demo_action_pause_ms()
        try:
            locator.scroll_into_view_if_needed(timeout=3000)
            box = locator.bounding_box()
            if box is None:
                return None

            local_x = box["width"] / 2
            local_y = box["height"] / 2
            marker_data = {
                "action": action,
                "label": label,
                "pauseMs": pause_ms,
                "left": box["x"],
                "top": box["y"],
                "width": box["width"],
                "height": box["height"],
                "clickX": box["x"] + local_x,
                "clickY": box["y"] + local_y,
            }
            self.page.evaluate(
                """
                (data) => {
                  if (!document.body) return;

                  const styleId = "codex-demo-action-style";
                  if (!document.getElementById(styleId)) {
                    const style = document.createElement("style");
                    style.id = styleId;
                    style.textContent = `
                      @keyframes codexDemoPulse {
                        0% { transform: scale(0.96); opacity: 0.65; }
                        55% { transform: scale(1.04); opacity: 1; }
                        100% { transform: scale(1); opacity: 1; }
                      }
                    `;
                    document.head.appendChild(style);
                  }

                  document.querySelectorAll("[data-codex-demo-marker]").forEach((node) => node.remove());

                  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
                  const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
                  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
                  const outlineTop = Math.max(4, data.top - 6);
                  const outlineLeft = Math.max(4, data.left - 6);
                  const outlineWidth = Math.max(18, data.width + 12);
                  const outlineHeight = Math.max(18, data.height + 12);
                  const clickX = clamp(data.clickX, 16, viewportWidth - 16);
                  const clickY = clamp(data.clickY, 16, viewportHeight - 16);

                  const outline = document.createElement("div");
                  outline.dataset.codexDemoMarker = "true";
                  Object.assign(outline.style, {
                    position: "fixed",
                    top: `${outlineTop}px`,
                    left: `${outlineLeft}px`,
                    width: `${outlineWidth}px`,
                    height: `${outlineHeight}px`,
                    border: "2px solid rgba(255, 55, 95, 0.82)",
                    borderRadius: "8px",
                    boxShadow: "0 0 0 9999px rgba(8, 12, 20, 0.08)",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    animation: "codexDemoPulse 520ms ease-out"
                  });

                  const ring = document.createElement("div");
                  ring.dataset.codexDemoMarker = "true";
                  Object.assign(ring.style, {
                    position: "fixed",
                    top: `${clickY - 18}px`,
                    left: `${clickX - 18}px`,
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    border: "4px solid #ff375f",
                    background: "rgba(255, 55, 95, 0.12)",
                    boxShadow: "0 0 0 10px rgba(255, 55, 95, 0.20), 0 0 28px rgba(255, 55, 95, 0.88)",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    animation: "codexDemoPulse 520ms ease-out"
                  });

                  const dot = document.createElement("div");
                  dot.dataset.codexDemoMarker = "true";
                  Object.assign(dot.style, {
                    position: "fixed",
                    top: `${clickY - 4}px`,
                    left: `${clickX - 4}px`,
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: "#ff375f",
                    pointerEvents: "none",
                    zIndex: "2147483647"
                  });

                  const horizontal = document.createElement("div");
                  horizontal.dataset.codexDemoMarker = "true";
                  Object.assign(horizontal.style, {
                    position: "fixed",
                    top: `${clickY - 1}px`,
                    left: `${clickX - 24}px`,
                    width: "48px",
                    height: "2px",
                    background: "#ff375f",
                    pointerEvents: "none",
                    zIndex: "2147483647"
                  });

                  const vertical = document.createElement("div");
                  vertical.dataset.codexDemoMarker = "true";
                  Object.assign(vertical.style, {
                    position: "fixed",
                    top: `${clickY - 24}px`,
                    left: `${clickX - 1}px`,
                    width: "2px",
                    height: "48px",
                    background: "#ff375f",
                    pointerEvents: "none",
                    zIndex: "2147483647"
                  });

                  const badge = document.createElement("div");
                  badge.dataset.codexDemoMarker = "true";
                  badge.textContent = `${data.action}: ${data.label}`;
                  const badgeTop = clickY > 72 ? clickY - 62 : clickY + 34;
                  const badgeLeft = clickX < viewportWidth / 2 ? clickX + 26 : clickX - 386;
                  Object.assign(badge.style, {
                    position: "fixed",
                    top: `${Math.max(8, badgeTop)}px`,
                    left: `${clamp(badgeLeft, 10, viewportWidth - 380)}px`,
                    maxWidth: "360px",
                    padding: "9px 12px",
                    color: "#ffffff",
                    background: "#111827",
                    border: "2px solid #ff375f",
                    borderRadius: "8px",
                    boxShadow: "0 10px 26px rgba(0, 0, 0, 0.28)",
                    font: "700 14px/1.25 Arial, sans-serif",
                    letterSpacing: "0",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    direction: "ltr",
                    animation: "codexDemoPulse 520ms ease-out"
                  });

                  document.body.append(outline, ring, dot, horizontal, vertical, badge);
                  window.setTimeout(() => {
                    outline.remove();
                    ring.remove();
                    dot.remove();
                    horizontal.remove();
                    vertical.remove();
                    badge.remove();
                  }, Math.max(1500, data.pauseMs * 3));
                }
                """,
                marker_data,
            )
            self.page.wait_for_timeout(pause_ms)
            return {"x": local_x, "y": local_y}
        except Exception:
            return None

    def highlight_page_action(self, label: str, action: str = "OPEN") -> None:
        if not self._demo_highlight_enabled():
            return

        pause_ms = self._demo_action_pause_ms()
        try:
            self.page.evaluate(
                """
                (data) => {
                  if (!document.body) return;

                  const styleId = "codex-demo-action-style";
                  if (!document.getElementById(styleId)) {
                    const style = document.createElement("style");
                    style.id = styleId;
                    style.textContent = `
                      @keyframes codexDemoPulse {
                        0% { transform: scale(0.96); opacity: 0.65; }
                        55% { transform: scale(1.04); opacity: 1; }
                        100% { transform: scale(1); opacity: 1; }
                      }
                    `;
                    document.head.appendChild(style);
                  }

                  document.querySelectorAll("[data-codex-demo-marker]").forEach((node) => node.remove());

                  const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
                  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
                  const clickX = Math.round(viewportWidth / 2);
                  const clickY = Math.min(190, Math.max(120, Math.round(viewportHeight * 0.18)));

                  const ring = document.createElement("div");
                  ring.dataset.codexDemoMarker = "true";
                  Object.assign(ring.style, {
                    position: "fixed",
                    top: `${clickY - 22}px`,
                    left: `${clickX - 22}px`,
                    width: "44px",
                    height: "44px",
                    borderRadius: "50%",
                    border: "4px solid #ff375f",
                    background: "rgba(255, 55, 95, 0.12)",
                    boxShadow: "0 0 0 9999px rgba(8, 12, 20, 0.06), 0 0 0 10px rgba(255, 55, 95, 0.20), 0 0 28px rgba(255, 55, 95, 0.88)",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    animation: "codexDemoPulse 520ms ease-out"
                  });

                  const dot = document.createElement("div");
                  dot.dataset.codexDemoMarker = "true";
                  Object.assign(dot.style, {
                    position: "fixed",
                    top: `${clickY - 4}px`,
                    left: `${clickX - 4}px`,
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: "#ff375f",
                    pointerEvents: "none",
                    zIndex: "2147483647"
                  });

                  const badge = document.createElement("div");
                  badge.dataset.codexDemoMarker = "true";
                  badge.textContent = `${data.action}: ${data.label}`;
                  Object.assign(badge.style, {
                    position: "fixed",
                    top: `${clickY + 34}px`,
                    left: `${Math.max(12, clickX - 210)}px`,
                    maxWidth: "420px",
                    padding: "10px 14px",
                    color: "#ffffff",
                    background: "#111827",
                    border: "2px solid #ff375f",
                    borderRadius: "8px",
                    boxShadow: "0 10px 26px rgba(0, 0, 0, 0.28)",
                    font: "700 15px/1.25 Arial, sans-serif",
                    letterSpacing: "0",
                    textAlign: "center",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    direction: "ltr",
                    animation: "codexDemoPulse 520ms ease-out"
                  });

                  document.body.append(ring, dot, badge);
                  window.setTimeout(() => {
                    ring.remove();
                    dot.remove();
                    badge.remove();
                  }, Math.max(1500, data.pauseMs * 3));
                }
                """,
                {"action": action, "label": label, "pauseMs": pause_ms},
            )
            self.page.wait_for_timeout(pause_ms)
        except Exception:
            return

    def show_demo_step(self, current: int, total: int, label: str) -> None:
        if not self._demo_highlight_enabled():
            return

        pause_ms = self._demo_action_pause_ms()
        try:
            self.page.evaluate(
                """
                (data) => {
                  if (!document.body) return;

                  document.querySelectorAll("[data-codex-demo-step]").forEach((node) => node.remove());

                  const step = document.createElement("div");
                  step.dataset.codexDemoStep = "true";
                  step.textContent = `Step ${data.current}/${data.total}: ${data.label}`;
                  Object.assign(step.style, {
                    position: "fixed",
                    top: "18px",
                    left: "18px",
                    maxWidth: "520px",
                    padding: "12px 16px",
                    color: "#ffffff",
                    background: "#111827",
                    border: "2px solid #38bdf8",
                    borderRadius: "8px",
                    boxShadow: "0 12px 30px rgba(0, 0, 0, 0.28)",
                    font: "800 17px/1.25 Arial, sans-serif",
                    letterSpacing: "0",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    direction: "ltr"
                  });

                  document.body.append(step);
                  window.setTimeout(() => step.remove(), Math.max(2200, data.pauseMs * 4));
                }
                """,
                {"current": current, "total": total, "label": label, "pauseMs": pause_ms},
            )
            self.page.wait_for_timeout(max(350, pause_ms))
        except Exception:
            return

    def show_demo_pass(self, label: str) -> None:
        if not self._demo_highlight_enabled():
            return

        pause_ms = self._demo_action_pause_ms()
        try:
            self.page.evaluate(
                """
                (data) => {
                  if (!document.body) return;

                  document.querySelectorAll("[data-codex-demo-pass]").forEach((node) => node.remove());

                  const pass = document.createElement("div");
                  pass.dataset.codexDemoPass = "true";
                  pass.textContent = `PASS: ${data.label}`;
                  Object.assign(pass.style, {
                    position: "fixed",
                    right: "18px",
                    top: "18px",
                    maxWidth: "440px",
                    padding: "12px 16px",
                    color: "#052e16",
                    background: "#bbf7d0",
                    border: "2px solid #16a34a",
                    borderRadius: "8px",
                    boxShadow: "0 12px 30px rgba(0, 0, 0, 0.24)",
                    font: "800 16px/1.25 Arial, sans-serif",
                    letterSpacing: "0",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    direction: "ltr"
                  });

                  document.body.append(pass);
                  window.setTimeout(() => pass.remove(), Math.max(2200, data.pauseMs * 4));
                }
                """,
                {"label": label, "pauseMs": pause_ms},
            )
            self.page.wait_for_timeout(max(350, pause_ms))
        except Exception:
            return

    def show_demo_notice(self, title: str, lines: list[str]) -> None:
        if not self._demo_highlight_enabled():
            return

        pause_ms = self._demo_action_pause_ms()
        try:
            self.page.evaluate(
                """
                (data) => {
                  if (!document.body) return;

                  document.querySelectorAll("[data-codex-demo-notice]").forEach((node) => node.remove());

                  const panel = document.createElement("div");
                  panel.dataset.codexDemoNotice = "true";

                  const title = document.createElement("div");
                  title.textContent = data.title;
                  Object.assign(title.style, {
                    font: "900 20px/1.2 Arial, sans-serif",
                    marginBottom: "10px"
                  });

                  const list = document.createElement("div");
                  Object.assign(list.style, {
                    display: "grid",
                    gap: "6px"
                  });

                  data.lines.forEach((line) => {
                    const row = document.createElement("div");
                    row.textContent = line;
                    Object.assign(row.style, {
                      font: "700 14px/1.35 Arial, sans-serif"
                    });
                    list.append(row);
                  });

                  Object.assign(panel.style, {
                    position: "fixed",
                    left: "50%",
                    top: "50%",
                    transform: "translate(-50%, -50%)",
                    width: "min(560px, calc(100vw - 36px))",
                    padding: "20px",
                    color: "#111827",
                    background: "#ffffff",
                    border: "3px solid #38bdf8",
                    borderRadius: "8px",
                    boxShadow: "0 0 0 9999px rgba(8, 12, 20, 0.20), 0 22px 60px rgba(0, 0, 0, 0.30)",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    direction: "ltr"
                  });

                  panel.append(title, list);
                  document.body.append(panel);
                  window.setTimeout(() => panel.remove(), Math.max(3200, data.pauseMs * 5));
                }
                """,
                {"title": title, "lines": lines, "pauseMs": pause_ms},
            )
            self.page.wait_for_timeout(max(1000, pause_ms * 2))
        except Exception:
            return

    def show_demo_summary(self, items: list[str]) -> None:
        if not self._demo_highlight_enabled():
            return

        pause_ms = self._demo_action_pause_ms()
        try:
            self.page.evaluate(
                """
                (data) => {
                  if (!document.body) return;

                  document.querySelectorAll("[data-codex-demo-summary]").forEach((node) => node.remove());

                  const panel = document.createElement("div");
                  panel.dataset.codexDemoSummary = "true";

                  const title = document.createElement("div");
                  title.textContent = "Shoofra E2E Demo Summary";
                  Object.assign(title.style, {
                    font: "900 22px/1.2 Arial, sans-serif",
                    marginBottom: "14px"
                  });

                  const list = document.createElement("div");
                  Object.assign(list.style, {
                    display: "grid",
                    gap: "9px"
                  });

                  data.items.forEach((item) => {
                    const row = document.createElement("div");
                    row.textContent = `PASS - ${item}`;
                    Object.assign(row.style, {
                      padding: "9px 10px",
                      background: "#f0fdf4",
                      border: "1px solid #86efac",
                      borderRadius: "6px",
                      color: "#052e16",
                      font: "800 15px/1.25 Arial, sans-serif"
                    });
                    list.append(row);
                  });

                  Object.assign(panel.style, {
                    position: "fixed",
                    left: "50%",
                    top: "50%",
                    transform: "translate(-50%, -50%)",
                    width: "min(620px, calc(100vw - 36px))",
                    padding: "22px",
                    color: "#111827",
                    background: "#ffffff",
                    border: "3px solid #16a34a",
                    borderRadius: "8px",
                    boxShadow: "0 0 0 9999px rgba(8, 12, 20, 0.24), 0 22px 60px rgba(0, 0, 0, 0.35)",
                    pointerEvents: "none",
                    zIndex: "2147483647",
                    direction: "ltr"
                  });

                  panel.append(title, list);
                  document.body.append(panel);
                  window.setTimeout(() => panel.remove(), Math.max(4500, data.pauseMs * 8));
                }
                """,
                {"items": items, "pauseMs": pause_ms},
            )
            self.page.wait_for_timeout(max(1200, pause_ms * 3))
        except Exception:
            return

    def click_visible(self, locator: Locator, label: str) -> None:
        position = self.highlight_locator(locator, label, "CLICK")
        if position is None:
            locator.click()
        else:
            locator.click(position=position)
        if self._demo_highlight_enabled():
            self.page.wait_for_timeout(max(250, self._demo_action_pause_ms() // 2))

    def fill_visible(self, locator: Locator, label: str, value: str) -> None:
        self.highlight_locator(locator, label, "FILL")
        locator.fill(value)

    def select_visible(self, locator: Locator, label: str, value: str) -> None:
        self.highlight_locator(locator, label, "SELECT")
        locator.select_option(value=value)

    def select_index_visible(self, locator: Locator, label: str, index: int) -> None:
        self.highlight_locator(locator, label, "SELECT")
        locator.select_option(index=index)

    def check_visible(self, locator: Locator, label: str) -> None:
        self.highlight_locator(locator, label, "CHECK")
        locator.check()
