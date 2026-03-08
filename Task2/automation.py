import os
import sys
import time
import shutil
from playwright.sync_api import sync_playwright

TARGET_URL = "https://cd.captchaaiplus.com/turnstile.html"
TURNSTILE_SCRIPT = "challenges.cloudflare.com/turnstile"


def obtain_valid_token():
    print("\n" + "=" * 60)
    print("PHASE 1 – Obtaining a valid Turnstile token")
    print("=" * 60)

    user_dir = os.path.join(os.getcwd(), "tmp_profile_token")
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir, ignore_errors=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_dir,
            headless=False,
            channel="msedge",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            viewport={"width": 1280, "height": 720},
        )

        page = context.new_page()
        print("[token] Opening site...")
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)

        try:
            page.fill('input[name="first_name"]', "Jane", timeout=5000)
            page.fill('input[name="last_name"]', "Smith", timeout=5000)
        except Exception:
            pass

        try:
            page.wait_for_selector(".cf-turnstile", timeout=15000)
        except Exception:
            print("[token] Turnstile widget not found")
            context.close()
            shutil.rmtree(user_dir, ignore_errors=True)
            return None

        token = ""
        start = time.time()
        while time.time() - start < 60:
            token = page.evaluate(
                "document.querySelector('[name=cf-turnstile-response]')?.value || ''"
            )
            if token and len(token) > 10:
                print("[token] Token captured!")
                break

            if 10 < (time.time() - start) < 12:
                try:
                    widget = page.locator(".cf-turnstile").first
                    if widget.is_visible():
                        widget.click()
                except Exception:
                    pass

            time.sleep(2)

        if not token or len(token) <= 10:
            print("[token] Failed to capture token")
            context.close()
            shutil.rmtree(user_dir, ignore_errors=True)
            return None

        print(f"[token] Token (first 80 chars): {token[:80]}...")
        context.close()

    shutil.rmtree(user_dir, ignore_errors=True)
    return token


def intercept_and_inject(token):
    print("\n" + "=" * 60)
    print("PHASE 2 – Block Turnstile + Inject token")
    print("=" * 60)

    captured_details = {}

    user_dir = os.path.join(os.getcwd(), "tmp_profile_intercept")
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir, ignore_errors=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_dir,
            headless=False,
            channel="msedge",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            viewport={"width": 1280, "height": 720},
        )

        page = context.new_page()
        blocked_urls = []

        def handle_route(route):
            url = route.request.url
            if TURNSTILE_SCRIPT in url or "challenges.cloudflare.com" in url:
                blocked_urls.append(url)
                print(f"[intercept] BLOCKED: {url}")
                route.abort()
            else:
                route.continue_()

        page.route("**/*", handle_route)

        print("[intercept] Opening site with Turnstile BLOCKED...")
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        details = page.evaluate("""() => {
            const el = document.querySelector('.cf-turnstile');
            if (!el) return null;
            return {
                sitekey: el.getAttribute('data-sitekey'),
                action: el.getAttribute('data-action'),
                cdata: el.getAttribute('data-cdata'),
                pagedata: el.getAttribute('data-pagedata'),
            };
        }""")

        if details:
            captured_details = details
            print("\nCaptured Turnstile Details:")
            print(f"  Sitekey  : {details['sitekey']}")
            print(f"  Action   : {details['action']}")
            print(f"  Cdata    : {details['cdata']}")
            print(f"  Pagedata : {details['pagedata']}\n")
        else:
            print("[intercept] Could not find .cf-turnstile element")

        turnstile_iframe = page.query_selector(
            "iframe[src*='challenges.cloudflare.com']"
        )
        if turnstile_iframe:
            print("[intercept] Turnstile iframe still present (unexpected)")
        else:
            print("[intercept] Turnstile did NOT load (blocked successfully)")

        print(f"[intercept] Blocked requests: {len(blocked_urls)}")
        print("[intercept] Injecting token...")

        page.evaluate(
            """(tok) => {
            let inp = document.querySelector('[name="cf-turnstile-response"]');
            if (!inp) {
                inp = document.createElement('input');
                inp.type = 'hidden';
                inp.name = 'cf-turnstile-response';
                document.getElementById('turnstile-form').appendChild(inp);
            }
            inp.value = tok;
        }""",
            token,
        )

        injected_value = page.evaluate(
            "document.querySelector('[name=\"cf-turnstile-response\"]')?.value?.length"
        )
        print(f"[intercept] Token injected (length={injected_value})")

        time.sleep(2)

        print("[intercept] Submitting form...")
        page.click('input[type="submit"]')
        time.sleep(5)

        result_text = page.evaluate(
            "document.getElementById('result')?.innerText || ''"
        )

        print(f"\nServer Response: {result_text}\n")

        if "Success" in result_text or "Verified" in result_text:
            print("[intercept] SUCCESS! The injected token was accepted!")
        else:
            print("[intercept] Verification failed. Token may have expired.")

        time.sleep(4)
        context.close()

    shutil.rmtree(user_dir, ignore_errors=True)
    return captured_details, result_text


if __name__ == "__main__":
    print("Task 2 - Network Interception")
    print("=" * 60)

    valid_token = obtain_valid_token()

    if not valid_token:
        print("\nCould not obtain a valid token. Exiting.")
        sys.exit(1)

    details, result = intercept_and_inject(valid_token)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Sitekey  : {details.get('sitekey', 'N/A')}")
    print(f"  Action   : {details.get('action', 'N/A')}")
    print(f"  Cdata    : {details.get('cdata', 'N/A')}")
    print(f"  Pagedata : {details.get('pagedata', 'N/A')}")
    print(f"  Result   : {result}")
    print("=" * 60)
