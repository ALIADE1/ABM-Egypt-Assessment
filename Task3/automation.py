import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape_dom_assessment(url):
    # Setup Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Uncomment to run invisibly once tested
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        print("Navigating to the assessment URL...")
        driver.get(url)

        # Give the DOM and dynamic scripts a moment to fully render
        time.sleep(3)

        all_images_b64 = []
        visible_images_b64 = []

        # ---------------------------------------------------------
        # Requirement 1 & 2: Scrape All Images & Visible Images Only
        # ---------------------------------------------------------
        print("Locating image elements...")
        all_imgs = driver.find_elements(By.CSS_SELECTOR, ".captcha-img")

        for img in all_imgs:
            # In these specific DOM assessments, images are usually embedded
            # directly in the DOM as base64 data URIs.
            src = img.get_attribute("src")
            if src:
                if "base64," in src:
                    b64 = src.split("base64,")[1]
                else:
                    b64 = src
                all_images_b64.append(b64)

        # Save the full list to JSON
        with open("allimages.json", "w", encoding="utf-8") as f:
            json.dump(all_images_b64, f, indent=4)
        print(f"✅ Saved {len(all_images_b64)} total images to 'allimages.json'")

        print("Extracting 9 visible images...")
        containers = driver.find_elements(By.CSS_SELECTOR, ".col-4")
        visible_containers = []
        for c in containers:
            if c.is_displayed():
                z_str = c.value_of_css_property("z-index")
                try:
                    z = int(z_str)
                except ValueError:
                    z = -1

                rect = c.rect
                x, y = round(rect["x"]), round(rect["y"])
                visible_containers.append({"el": c, "z": z, "x": x, "y": y})

        # Group by coordinates (x, y) to find exactly 9 overlapping spots
        groups = {}
        for vc in visible_containers:
            if vc["z"] == -1:
                continue  # ignore 'auto' z-index containers, like buttons

            key = None
            for k in groups.keys():
                if abs(k[0] - vc["x"]) < 10 and abs(k[1] - vc["y"]) < 10:
                    key = k
                    break
            if not key:
                key = (vc["x"], vc["y"])
                groups[key] = []
            groups[key].append(vc)

        visible_9_images = []
        # Sort by y, then by x to ensure grid order
        sorted_keys = sorted(groups.keys(), key=lambda k: (k[1], k[0]))
        for key in sorted_keys:
            group = groups[key]
            best = max(group, key=lambda item: item["z"])
            img = best["el"].find_element(By.CSS_SELECTOR, ".captcha-img")
            src = img.get_attribute("src")
            if src and "base64," in src:
                b64 = src.split("base64,")[1]
            else:
                b64 = src
            visible_9_images.append(b64)

        with open("visible_images_only.json", "w") as f:
            json.dump(visible_9_images, f, indent=4)
        print(
            f"✅ Saved {len(visible_9_images)} visible images to 'visible_images_only.json'"
        )

        # ---------------------------------------------------------
        # Requirement 3: Scrape the Visible Text Instruction
        # ---------------------------------------------------------
        print("\nSearching for visible instructions...")
        labels = driver.find_elements(By.CSS_SELECTOR, ".box-label")
        visible_labels = []
        for l in labels:
            if l.is_displayed():
                z_str = l.value_of_css_property("z-index")
                try:
                    z = int(z_str)
                except ValueError:
                    z = -1
                # get attribute textContent instead of text if hidden by transparency etc
                text_content = l.get_attribute("textContent")
                if text_content:
                    visible_labels.append({"text": text_content.strip(), "z": z})

        if visible_labels:
            best_label = max(visible_labels, key=lambda item: item["z"])
            instruction = best_label["text"]
            print("\n--- Scraping Results ---")
            print(f"Visible Instruction: '{instruction}'")
            with open("instruction.txt", "w") as f:
                f.write(instruction)
            print("Saved instruction to instruction.txt")
        else:
            print("No visible instruction found.")

    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    TARGET_URL = "https://egypt.blsspainglobal.com/Global/CaptchaPublic/GenerateCaptcha?data=4CDiA9odF2%2b%2bsWCkAU8htqZkgDyUa5SR6waINtJfg1ThGb6rPIIpxNjefP9UkAaSp%2fGsNNuJJi5Zt1nbVACkDRusgqfb418%2bScFkcoa1F0I%3d"
    scrape_dom_assessment(TARGET_URL)
