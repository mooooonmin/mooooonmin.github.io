"""Browser regressions for the Ink redesign's navigation and reading flows."""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright
from smoke_render import start_server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", default="_site")
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    server = start_server(Path(args.site_dir).resolve(), "127.0.0.1", 4177)
    base = "http://127.0.0.1:4177"
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)
    checks = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            def visit(route):
                page.goto(base + route, wait_until="networkidle")
                page.evaluate("document.fonts.ready")

            def screenshot(name):
                if args.screenshots:
                    page.screenshot(path=str(args.screenshots / (name + ".png")))

            visit("/")
            assert page.locator("html").get_attribute("data-theme") == "light"
            assert page.evaluate('document.fonts.check(\'16px "Pretendard Variable"\')')
            assert page.locator("main h1").count() == 1
            screenshot("home-desktop")
            page.locator("#toggle-sidebar").click()
            page.keyboard.press("Tab")
            assert not page.evaluate('document.activeElement.closest("#site-sidebar") !== null')
            assert page.locator("#site-sidebar").evaluate("e => e.inert")
            page.locator("#toggle-sidebar").click()
            checks.append("desktop hidden sidebar leaves focus order")

            routes = ["/", "/tags/", "/search/?q=Linux", "/category/d/", "/2026/05/20/Kubernetes_Deployment/", "/404.html"]
            for width in [320, 375, 768, 1024, 1280, 1920]:
                page.set_viewport_size({"width": width, "height": 900})
                for route in routes:
                    visit(route)
                    assert page.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) <= innerWidth + 1"), (width, route)
                    assert page.locator("main h1").count() == 1, route
            checks.append("six routes at six widths: no document overflow and one page heading")

            page.set_viewport_size({"width": 375, "height": 812})
            visit("/")
            screenshot("home-mobile")
            page.locator(".pagination").scroll_into_view_if_needed()
            for selector in [".pagination-prev", ".pagination-next"]:
                box = page.locator(selector).bounding_box()
                assert box["x"] >= 0 and box["x"] + box["width"] <= 375, selector
            assert page.locator(".pagination-current").is_visible()
            screenshot("pagination-mobile")
            checks.append("mobile pagination next/previous visible without horizontal scroll")
            page.locator("#open-nav").click()
            assert page.locator("main").evaluate("e => e.inert")
            for _ in range(40):
                page.keyboard.press("Tab")
                assert not page.evaluate('document.activeElement.closest("main") !== null')
            page.keyboard.press("Escape")
            assert page.locator("#open-nav").get_attribute("aria-expanded") == "false"
            assert page.locator("#open-nav").evaluate("e => e === document.activeElement")
            checks.append("mobile menu traps focus, Escape closes, trigger regains focus")

            visit("/tags/")
            page.locator("#tag-filter").fill("docker")
            assert page.locator(".tag-cloud-button:visible").count() > 0
            page.locator(".tag-cloud-button:visible").first.click()
            page.locator("#tag-result-list li").first.wait_for()
            box = page.locator("#tag-result-title").bounding_box()
            assert 60 <= box["y"] < 812, box
            assert page.locator(".tag-cloud-count").first.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)") >= 12
            screenshot("tags-mobile-selected")
            page.reload(wait_until="networkidle")
            page.locator("#tag-result-list li").first.wait_for()
            assert page.locator('.tag-cloud-button[aria-pressed="true"]').count() == 1
            checks.append("mobile tag filter, visible result, readable count, URL restoration")

            visit("/2026/02/13/Linux/")
            assert page.locator("#post-toc").is_visible()
            command = page.locator("td code").first
            assert command.evaluate("e => getComputedStyle(e).whiteSpace") == "nowrap"
            assert page.locator(".table-scroll[tabindex='0']").count() > 0
            screenshot("table-mobile")
            checks.append("article table commands stay intact and wide tables are keyboard reachable")

            page.route("**/assets/data/search-index.json", lambda route: route.fulfill(status=503, body="Unavailable"))
            visit("/search/?q=Linux")
            page.locator("#search-retry").wait_for(state="visible")
            assert page.locator("#result-search-input").is_visible()
            page.unroute("**/assets/data/search-index.json")
            page.locator("#search-retry").click()
            page.locator("#search-results li").first.wait_for()
            assert "Linux" in page.locator("#search-summary").inner_text()
            assert "```" not in page.locator("#search-results").inner_text()
            screenshot("search-mobile")
            checks.append("search error/retry recovers with query, count and clean snippets")
            visit("/404.html")
            assert page.locator(".recovery-actions a").count() == 2
            screenshot("404-mobile")

            page.set_viewport_size({"width": 1440, "height": 900})
            for route, name in [("/tags/", "tags-desktop"), ("/search/?q=Linux", "search-desktop"), ("/2026/05/20/Kubernetes_Deployment/", "post-desktop")]:
                visit(route)
                screenshot(name)
            page.locator("#theme-toggle").click()
            page.reload(wait_until="networkidle")
            assert page.locator("html").get_attribute("data-theme") == "blue"
            screenshot("post-dark")
            checks.append("neutral night reading preference survives reload")

            nojs = browser.new_context(java_script_enabled=False, viewport={"width": 375, "height": 812})
            fallback = nojs.new_page()
            fallback.goto(base + "/tags/")
            assert fallback.locator(".full-navigation").is_visible()
            assert fallback.locator(".tag-static-list details").count() > 0
            fallback.locator(".tag-static-list summary").first.click()
            assert fallback.locator(".tag-static-list a").first.is_visible()
            checks.append("JavaScript-disabled mobile navigation and static tag links work")
            assert not errors, errors
            browser.close()
        for check in checks:
            print("PASS", check)
        print("Ink UI/UX regressions passed.")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
