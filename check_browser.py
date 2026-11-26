"""Optional real-browser check on port 5001. Use --fixture for a disposable SQL fixture."""
import argparse
from pathlib import Path
from contextlib import ExitStack
from getpass import getpass
from threading import Thread
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from app import app
from check_portal import PASSWORDS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--url", default="http://127.0.0.1:5001")
    parser.add_argument("--student-evidence", type=Path, help="Save the seeded student1 grades dashboard as a PNG")
    args = parser.parse_args()
    base = args.url.rstrip("/")
    if urlsplit(base).hostname not in {"127.0.0.1", "127.0.0.2", "localhost"}:
        parser.error("Use a loopback URL for the local portal")
    with ExitStack() as stack:
        if args.fixture:
            from test_portal import OfflinePortal
            OfflinePortal.setUpClass()
            stack.callback(OfflinePortal.doClassCleanups)
            server = make_server("127.0.0.1", 0, app)
            base = f"http://127.0.0.1:{server.server_port}"
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            stack.callback(server.server_close)
            stack.callback(thread.join)
            stack.callback(server.shutdown)
        else:
            for name in ("student1", "student2", "lecturer1", "admin1"):
                PASSWORDS[name] = getpass(f"Portal password for {name}: ")

        playwright = stack.enter_context(sync_playwright())
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        stack.callback(browser.close)
        for username, title, sections in (
            ("student1", "Thando Mthembu", {"courses":["CS101","CS201"], "grades":["85","78"],"enrolments":["CS201"]}),
            ("student2", "Sarah Meyer", {"courses":["CS101"],"grades":["91"],"enrolments":["CS101"]}),
            ("lecturer1", "Maria Schmidt", {"courses":["CS101"],"students":["CU001","CU002"],"grades":["85","91"]}),
            ("admin1", "admin1", {"students":["CU001"],"lecturers":["Maria"],"courses":["EC101"],"enrolments":["CS201"],"grades":["CU002"]}),
        ):
            page = browser.new_page()
            page.goto(base + "/")
            page.locator("#username").fill(username)
            page.locator("#password").fill(PASSWORDS[username])
            page.locator(".login-button").click()
            expect(page.locator(".userlabel")).to_have_text(title)
            for section, markers in sections.items():
                page.locator(f"[data-view='{section}']").click()
                table = page.locator("#table-" + section)
                for marker in markers:
                    expect(table).to_contain_text(marker)
                if args.student_evidence and username == "student1" and section == "grades":
                    page.screenshot(path=str(args.student_evidence))
                if username in ("student2","lecturer1"):
                    expect(table).not_to_contain_text("CS201")
                if username == "admin1" and section == "grades":
                    table.get_by_role("button", name="Save").first.click()
                    expect(table.get_by_role("status").first).to_have_text("Saved")
            page.locator("#logoutButton").click()
            expect(page.locator("#loginForm")).to_be_visible()
            page.close()
            print("PASS", username, "Edge navigation, tables and logout")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Browser assertion snapshots can include the contents of login fields.
        raise SystemExit(f"Browser check failed ({type(error).__name__}); inspect the local portal.") from None
