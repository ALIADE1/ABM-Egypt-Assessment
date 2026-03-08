import os
import time
import shutil
from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import stealth_sync

    STEALTH_LIB = True
except ImportError:
    STEALTH_LIB = False

HEADLESS_STEALTH_JS = """
(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.chrome = { runtime: { connect: () => {}, sendMessage: () => {} }, loadTimes: () => {}, csi: () => {}, app: {} };
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    Object.defineProperty(navigator, 'language',  { get: () => 'en-US' });
    Object.defineProperty(navigator, 'platform',            { get: () => 'Win32' });
    Object.defineProperty(navigator, 'vendor',              { get: () => 'Google Inc.' });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
    Object.defineProperty(navigator, 'deviceMemory',        { get: () => 8 });
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const arr = [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client',     filename: 'internal-nacl-plugin' },
            ];
            arr.__proto__ = PluginArray.prototype;
            return arr;
        }
    });
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter.call(this, parameter);
    };
})();
"""


def start_session(headless, i):
    success = False
    token = None
    user_dir = os.path.join(os.getcwd(), f"tmp_profile_{i}")

    if os.path.exists(user_dir):
        shutil.rmtree(user_dir, ignore_errors=True)

    os.makedirs(f"videos/attempt_{i}", exist_ok=True)

    with sync_playwright() as p:
        opts = {
            "user_data_dir": user_dir,
            "headless": headless,
            "channel": "msedge",
            "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            "viewport": {"width": 1920, "height": 1080}
            if headless
            else {"width": 1280, "height": 720},
            "record_video_dir": f"videos/attempt_{i}/",
            "record_video_size": {"width": 1280, "height": 720},
        }

        if headless:
            opts["user_agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )

        try:
            context = p.chromium.launch_persistent_context(**opts)

            if headless:
                context.add_init_script(HEADLESS_STEALTH_JS)

            page = context.new_page()

            if headless and STEALTH_LIB:
                stealth_sync(page)

            print(f"[{i}] Opening site...")
            page.goto(
                "https://cd.captchaaiplus.com/turnstile.html",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            try:
                page.fill('input[name="firstname"]', "Jane", timeout=5000)
                page.fill('input[name="lastname"]', "Smith", timeout=5000)
                print(f"[{i}] Form filled")
            except:
                try:
                    inputs = page.locator("input[type='text']").all()
                    if len(inputs) >= 2:
                        inputs[0].fill("Jane")
                        inputs[1].fill("Smith")
                        print(f"[{i}] Form filled (fallback)")
                except:
                    print(f"[{i}] Form fill skipped")

            time.sleep(1)

            try:
                page.wait_for_selector(".cf-turnstile", timeout=15000)
            except:
                print(f"[{i}] Turnstile not found")
                context.close()
                return False, None

            start = time.time()
            while time.time() - start < 45:
                token = page.evaluate(
                    "document.querySelector('[name=cf-turnstile-response]')?.value || ''"
                )

                if token and len(token) > 10:
                    print(f"[{i}] Token captured!")
                    print(f"TOKEN: {token}")
                    print("-" * 50)
                    break

                if 10 < (time.time() - start) < 12:
                    try:
                        widget = page.locator(".cf-turnstile").first
                        if widget.is_visible():
                            widget.click()
                            print(f"[{i}] Widget clicked")
                    except:
                        pass

                time.sleep(2)

            if token and len(token) > 10:
                page.get_by_role("button", name="Submit").click()
                time.sleep(4)
                content = page.content()
                if "Success!" in content or "verified" in content.lower():
                    success = True
                    print(f"[{i}] Success verified!")
                else:
                    print(f"[{i}] Submit failed")
            else:
                print(f"[{i}] No token captured (timeout)")

            context.close()

        except Exception as e:
            print(f"[{i}] Error: {str(e)[:80]}")
        finally:
            shutil.rmtree(user_dir, ignore_errors=True)

    return success, token


if __name__ == "__main__":
    if not STEALTH_LIB:
        print("[!] playwright-stealth not found. Run: pip install playwright-stealth")
        print("[!] Headless attempts may fail without it.\n")

    count = 10
    passed = 0

    print("--- Running Turnstile Assessment ---")

    for x in range(1, count + 1):
        is_headless = x > 7
        mode = "Headless" if is_headless else "Headed"

        print(f"\nAttempt {x} ({mode})")
        ok, _ = start_session(is_headless, x)

        if ok:
            passed += 1
            print("Result: OK")
        else:
            print("Result: FAIL")

        time.sleep(1)

    rate = (passed / count) * 100
    print(f"\nFinal Score: {passed}/{count} ({rate:.2f}%)")
    print("STATUS: " + ("PASS" if rate >= 60 else "FAIL"))
