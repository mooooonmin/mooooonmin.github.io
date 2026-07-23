import argparse
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SITE_DIR = BASE_DIR / "_site"

# 화면 회귀가 자주 발생했던 대표 경로만 빠르게 확인한다.
ROUTES = [
    ("/", "Home"),
    ("/tags/", "Tags"),
    ("/category/d/", "Category D"),
    ("/category/d/page2/", "Category D page 2"),
    ("/search/?q=Linux", "Search results"),
    ("/search/?q=accessmodes", "Search full-body index"),
    ("/search/?q=no-result-token", "Search empty results"),
    ("/2026/05/20/Kubernetes_Deployment/", "Post with code and source"),
    ("/2026/02/13/Linux/", "Linux command post"),
    ("/2026/02/12/OSI_7_vs_TCP_IP_4/", "Post with images"),
    ("/404.html", "404 page"),
]

VIEWPORTS = [
    ("desktop", {"width": 1366, "height": 768}),
    ("mobile", {"width": 390, "height": 844}),
]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run browser smoke checks against the generated Jekyll _site output.",
    )
    parser.add_argument(
        "--site-dir",
        default=str(DEFAULT_SITE_DIR),
        help="Generated static site directory. Default: _site",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser visibly instead of headless.",
    )
    parser.add_argument(
        "--skip-browser-if-unavailable",
        action="store_true",
        help="Exit 0 with an explanation when Playwright is not installed.",
    )
    return parser.parse_args()


def load_playwright(skip_if_unavailable):
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        message = (
            "Python Playwright is not installed. Install it with "
            "`python -m pip install playwright` and `python -m playwright install chromium`."
        )
        if skip_if_unavailable:
            print(message)
            return None, None
        raise SystemExit(message)
    return sync_playwright, PlaywrightError


def start_server(site_dir, host, port):
    if not (site_dir / "index.html").exists():
        raise SystemExit(
            f"{site_dir} does not contain index.html. Build the site before running this script.",
        )

    handler = functools.partial(QuietHandler, directory=str(site_dir))
    httpd = ReusableThreadingTCPServer((host, port), handler)
    httpd.daemon_threads = True
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def check_no_horizontal_overflow(page, label):
    metrics = page.evaluate(
        """() => ({
            innerWidth: window.innerWidth,
            documentWidth: document.documentElement.scrollWidth,
            bodyWidth: document.body.scrollWidth
        })""",
    )
    max_width = max(metrics["documentWidth"], metrics["bodyWidth"])
    assert_true(
        max_width <= metrics["innerWidth"] + 2,
        f"{label}: horizontal overflow detected: {metrics}",
    )


def check_sidebar_fixed(page, label):
    header = page.locator("#site-sidebar")
    if not header.is_visible():
        return

    position = header.evaluate("element => getComputedStyle(element).position")
    viewport_width = page.viewport_size["width"]
    if viewport_width >= 700:
        assert_true(position == "fixed", f"{label}: desktop sidebar is not fixed")


def check_theme_toggle(page, label):
    toggle = page.locator("#theme-toggle")
    assert_true(toggle.count() == 1, f"{label}: theme toggle is missing")
    before = page.locator("html").get_attribute("data-theme")
    toggle.click()
    after = page.locator("html").get_attribute("data-theme")
    assert_true(before != after, f"{label}: theme toggle did not change theme")
    expected_pressed = "true" if after == "blue" else "false"
    assert_true(
        toggle.get_attribute("aria-pressed") == expected_pressed,
        f"{label}: theme aria-pressed does not match {after}",
    )

    page.reload(wait_until="networkidle")
    assert_true(
        page.locator("html").get_attribute("data-theme") == after,
        f"{label}: saved theme was not restored",
    )


def check_sidebar_persistence(page, label, route, viewport_name):
    if route != "/" or viewport_name != "desktop":
        return

    toggle = page.locator("#toggle-sidebar")
    toggle.click()
    assert_true("nav-collapsed" in page.locator("body").get_attribute("class"), f"{label}: sidebar did not collapse")
    page.reload(wait_until="networkidle")
    assert_true(
        "nav-collapsed" in page.locator("body").get_attribute("class"),
        f"{label}: collapsed sidebar state was not restored",
    )
    assert_true(toggle.get_attribute("aria-expanded") == "false", f"{label}: sidebar aria state was not restored")
    toggle.click()
    assert_true("nav-collapsed" not in page.locator("body").get_attribute("class"), f"{label}: sidebar did not expand")


def check_search_submit(page, base_url, label, route, viewport_name):
    if route != "/" or viewport_name != "desktop":
        return

    search_input = page.locator("#search-input")
    search_input.fill("Linux")
    with page.expect_navigation(wait_until="networkidle"):
        search_input.press("Enter")
    assert_true(page.url == f"{base_url}/search/?q=Linux", f"{label}: search Enter navigation failed")
    assert_true(page.locator("#search-results li").count() > 0, f"{label}: submitted search has no results")


def check_mobile_navigation(page, base_url, route, label, viewport_name):
    if viewport_name != "mobile" or route != "/":
        return

    open_button = page.locator("#open-nav")
    assert_true(open_button.count() == 1, f"{label}: mobile nav button missing")
    assert_true(open_button.is_visible(), f"{label}: mobile nav button hidden")

    open_button.click()
    assert_true("nav-open" in page.locator("body").get_attribute("class"), f"{label}: mobile nav did not open")

    navigation = page.locator(".full-navigation")
    assert_true(navigation.is_visible(), f"{label}: mobile navigation hidden after open")

    toggle = page.locator("#theme-toggle")
    assert_true(toggle.is_visible(), f"{label}: mobile theme toggle hidden after nav open")
    before_theme = page.locator("html").get_attribute("data-theme")
    toggle.click()
    after_theme = page.locator("html").get_attribute("data-theme")
    assert_true(before_theme != after_theme, f"{label}: mobile theme toggle did not change theme")

    category_link = page.locator('a[href="/category/d/"]')
    assert_true(category_link.count() == 1, f"{label}: category D link missing")
    with page.expect_navigation(wait_until="load"):
        category_link.click()
    assert_true(page.url == f"{base_url}/category/d/", f"{label}: category link did not navigate: {page.url}")


def check_visual_surfaces(page, label):
    assert_true(page.locator("#site-sidebar").count() == 1, f"{label}: sidebar missing")
    assert_true(page.locator(".content").count() == 1, f"{label}: content missing")
    assert_true(page.locator("img[alt*='logo']").count() >= 1, f"{label}: logo missing")

    if page.locator("table").count() > 0:
        table_style = page.locator("table").first.evaluate(
            """element => {
                const style = getComputedStyle(element);
                return { color: style.color, background: style.backgroundColor };
            }""",
        )
        assert_true(table_style["color"], f"{label}: table text color missing")

    if page.locator(".pagination").count() > 0:
        current = page.locator(".pagination-current")
        assert_true(current.count() == 1, f"{label}: pagination current marker missing")
        assert_true(current.is_visible(), f"{label}: pagination current marker hidden")


def check_search_state(page, label, route):
    if not route.startswith("/search/"):
        return

    if "no-result-token" in route:
        empty_state = page.locator("#search-empty")
        assert_true(empty_state.is_visible(), f"{label}: empty search state is hidden")
        assert_true(
            "No results found." in empty_state.inner_text(),
            f"{label}: empty search message missing",
        )
        return

    results = page.locator("#search-results li")
    assert_true(results.count() > 0, f"{label}: search results missing")
    if "accessmodes" in route:
        result_url = results.first.locator("a").get_attribute("href")
        assert_true(
            result_url == "/2026/05/22/Kubernetes_MySQL_Volume/",
            f"{label}: full-body search returned an unexpected post: {result_url}",
        )
        return
    assert_true(page.locator("#search-results mark").count() > 0, f"{label}: search highlight missing")


def check_tag_state(page, label, route):
    if route != "/tags/":
        return

    button = page.locator(".tag-cloud-button").first
    assert_true(button.count() == 1, f"{label}: tag button missing")
    button.click()
    page.locator("#tag-result-list li").first.wait_for(state="visible")
    assert_true(button.get_attribute("aria-pressed") == "true", f"{label}: active tag state missing")
    assert_true(page.locator("#tag-results").is_visible(), f"{label}: tag results hidden")
    page.reload(wait_until="networkidle")
    restored_button = page.locator(".tag-cloud-button.is-active")
    assert_true(restored_button.count() == 1, f"{label}: restored tag selection missing")
    assert_true(restored_button.get_attribute("aria-pressed") == "true", f"{label}: tag hash state was not restored")
    assert_true(page.locator("#tag-result-list li").count() > 0, f"{label}: restored tag results missing")


def check_static_assets(page, label, route):
    stylesheet = page.locator('link[rel="stylesheet"][href="/css/main.css"]')
    assert_true(stylesheet.count() == 1, f"{label}: stable main.css reference missing")

    font_preload = page.locator(
        'link[rel="preload"][as="font"][type="font/woff2"][href="/assets/fonts/neodgm.woff2"]',
    )
    assert_true(font_preload.count() == 1, f"{label}: base font preload missing")

    assert_true(page.locator('script[src="/assets/js/site.js"]').count() == 1, f"{label}: stable site.js reference missing")
    if route.startswith("/search/"):
        assert_true(
            page.locator('script[src="/assets/js/search.js"]').count() == 1,
            f"{label}: stable search.js reference missing",
        )
    if route == "/tags/":
        assert_true(
            page.locator('script[src="/assets/js/tags.js"]').count() == 1,
            f"{label}: stable tags.js reference missing",
        )


def check_post_images(page, label, route):
    if route != "/2026/02/12/OSI_7_vs_TCP_IP_4/":
        return

    images = page.locator(".content img")
    assert_true(images.count() == 3, f"{label}: expected three content images")
    for index in range(images.count()):
        image = images.nth(index)
        image.scroll_into_view_if_needed()
        image.evaluate("element => element.decode()")
        attributes = image.evaluate(
            """element => ({
                alt: element.getAttribute("alt"),
                width: element.getAttribute("width"),
                height: element.getAttribute("height"),
                loading: element.getAttribute("loading"),
                decoding: element.getAttribute("decoding"),
                complete: element.complete,
                naturalWidth: element.naturalWidth
            })""",
        )
        assert_true(attributes["alt"], f"{label}: image {index + 1} has no alt text")
        assert_true(attributes["width"] and attributes["height"], f"{label}: image {index + 1} has no dimensions")
        assert_true(attributes["loading"] == "lazy", f"{label}: image {index + 1} is not lazy-loaded")
        assert_true(attributes["decoding"] == "async", f"{label}: image {index + 1} is not asynchronously decoded")
        assert_true(
            attributes["complete"] and attributes["naturalWidth"] > 0,
            f"{label}: image {index + 1} failed to load",
        )


def check_route(page, base_url, route, label, viewport_name, blue_mode):
    console_messages = []
    page.on(
        "console",
        lambda msg: console_messages.append(f"{msg.type}: {msg.text}")
        if msg.type == "error"
        else None,
    )

    response = page.goto(f"{base_url}{route}", wait_until="networkidle")
    assert_true(response is not None, f"{label}: no response")
    assert_true(response.status < 400, f"{label}: HTTP {response.status}")

    body_text = page.locator("body").inner_text(timeout=5000).strip()
    assert_true(len(body_text) > 30, f"{label}: page appears blank")
    assert_true(
        not any(token in body_text for token in ["Build Error", "Webpack", "Vite"]),
        f"{label}: framework error overlay text detected",
    )

    expected_theme = "blue" if blue_mode else "light"
    actual_theme = page.locator("html").get_attribute("data-theme")
    assert_true(actual_theme == expected_theme, f"{label}: expected {expected_theme} theme")
    assert_true(page.title() != "Repository", f"{label}: document title is not page-specific")

    check_visual_surfaces(page, label)
    check_static_assets(page, label, route)
    check_post_images(page, label, route)
    check_search_state(page, label, route)
    check_tag_state(page, label, route)
    check_no_horizontal_overflow(page, label)
    check_sidebar_fixed(page, label)
    check_mobile_navigation(page, base_url, route, label, viewport_name)

    if route in {"/", "/category/d/"} and viewport_name == "desktop":
        check_sidebar_persistence(page, label, route, viewport_name)
        check_theme_toggle(page, label)

    check_search_submit(page, base_url, label, route, viewport_name)

    relevant_console_messages = [
        message
        for message in console_messages
        if not any(
            ignored in message
            for ignored in [
                "cdn.jsdelivr.net",
                "Pretendard",
                "Failed to load resource",
                "net::ERR",
            ]
        )
    ]
    assert_true(
        not relevant_console_messages,
        f"{label}: console errors: {relevant_console_messages}",
    )


def run_smoke(args):
    sync_playwright, PlaywrightError = load_playwright(args.skip_browser_if_unavailable)
    if sync_playwright is None:
        return 0

    site_dir = Path(args.site_dir).resolve()
    server = start_server(site_dir, args.host, args.port)
    base_url = f"http://{args.host}:{args.port}"
    failures = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not args.headed)

            for viewport_name, _ in VIEWPORTS:
                for route, label in ROUTES:
                    blue_mode = viewport_name == "desktop"
                    route_label = f"{viewport_name} {label} {route}"
                    context = browser.new_context(viewport=dict(VIEWPORTS_BY_NAME[viewport_name]))
                    page = context.new_page()
                    theme_value = "blue" if blue_mode else "light"
                    page.goto(base_url, wait_until="domcontentloaded")
                    page.evaluate(
                        """theme => {
                            window.localStorage.setItem("theme-mode", theme);
                            window.localStorage.removeItem("sidebar-collapsed");
                        }""",
                        theme_value,
                    )
                    try:
                        check_route(page, base_url, route, route_label, viewport_name, blue_mode)
                        print(f"PASS {route_label}")
                    except (AssertionError, PlaywrightError) as error:
                        failures.append(f"FAIL {route_label}: {error}")
                    finally:
                        context.close()

            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    if failures:
        print("\n".join(failures))
        return 1

    print("Render smoke checks passed.")
    return 0


VIEWPORTS_BY_NAME = dict(VIEWPORTS)


if __name__ == "__main__":
    sys.exit(run_smoke(parse_args()))
