<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-2.x-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/Selenium-4.x-43B02A?style=for-the-badge&logo=selenium&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" />
</p>

# 🤖 Python Developer Assessment — Automation & Web Crawling

> A comprehensive technical assessment demonstrating expertise in **browser automation**, **CAPTCHA bypass**, **network interception**, and **DOM analysis** using Python, Playwright, and Selenium.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Task 1 — Turnstile CAPTCHA Bypass](#-task-1--turnstile-captcha-bypass)
- [Task 2 — Network Interception & Token Injection](#-task-2--network-interception--token-injection)
- [Task 3 — DOM Scraping & Image Extraction](#-task-3--dom-scraping--image-extraction)
- [Task 4 — System Architecture Design](#-task-4--system-architecture-design)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Results](#-results)

---

## 🔍 Overview

This repository contains solutions for a **Python Developer Assessment** focused on automation and web crawling. The assessment is divided into four tasks, each targeting a different aspect of browser automation and anti-bot systems.

---

## 🛡️ Task 1 — Turnstile CAPTCHA Bypass

**Objective:** Automate Cloudflare Turnstile CAPTCHA solving across **headed** and **headless** browser modes with a success rate ≥ 60%.

### Approach
- **Playwright** with persistent browser contexts using Microsoft Edge
- **Stealth techniques** to evade bot detection:
  - `navigator.webdriver` override
  - Chrome runtime spoofing
  - WebGL renderer masking
  - Plugin & hardware fingerprint emulation
- Headed mode (7 attempts) + Headless mode (3 attempts) across 10 total runs
- Automatic form fill, widget click, and token extraction

### Key Features
- Session isolation via temporary browser profiles
- Full video recording of each attempt
- Automatic cleanup of temporary data

📹 **Demo:** [`Task1/Video.mp4`](Task1/Video.mp4)

---

## 🌐 Task 2 — Network Interception & Token Injection

**Objective:** Intercept Cloudflare Turnstile network requests, block CAPTCHA loading, capture metadata, and inject a pre-obtained valid token.

### Approach — Two-Phase Strategy

| Phase | Description |
|-------|-------------|
| **Phase 1** | Launch a clean headed session to solve Turnstile normally and capture a valid token |
| **Phase 2** | Open a new session with route interception — block all `challenges.cloudflare.com` requests, extract `sitekey`, `action`, `cdata`, `pagedata`, inject the captured token, and submit the form |

### Key Features
- Network-level request blocking via Playwright route handlers
- Automatic extraction of Turnstile widget configuration (`sitekey`, `action`, `cdata`, `pagedata`)
- Hidden input creation & token injection into the DOM
- Server-side verification of the injected token

📹 **Demo:** [`Task2/Video.mp4`](Task2/Video.mp4)

---

## 🖼️ Task 3 — DOM Scraping & Image Extraction

**Objective:** Scrape a CAPTCHA challenge page to extract all images, identify the 9 currently visible images, and retrieve the text instruction.

### Approach
- **Selenium WebDriver** with headless Chrome
- Visibility resolution using **z-index** and **coordinate grouping**
- Base64 image extraction from `data:image` `src` attributes
- Grid-ordered output based on `(x, y)` position sorting

### Output Files

| File | Description |
|------|-------------|
| `allimages.json` | All CAPTCHA images (base64-encoded) found in the DOM |
| `visible_images_only.json` | The 9 visible images resolved by z-index stacking |
| `instruction.txt` | The visible text instruction (e.g., *"Please select all boxes with number 149"*) |

---

## 🏗️ Task 4 — System Architecture Design

**Objective:** Design a scalable system architecture for an automated CAPTCHA-solving pipeline.

### Diagram

<p align="center">
  <img src="Task4/Task4_System_Diagram.png" alt="System Architecture Diagram" width="700"/>
</p>

The architecture covers the end-to-end flow including browser orchestration, CAPTCHA detection, solving strategies, token management, and result delivery.

---

## 🧰 Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core language |
| **Playwright** | Browser automation (Tasks 1 & 2) |
| **Selenium** | DOM scraping (Task 3) |
| **playwright-stealth** | Bot detection evasion |
| **Microsoft Edge** | Browser engine (Chromium-based) |
| **webdriver-manager** | Automatic ChromeDriver management |

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.10+
pip
Microsoft Edge (for Playwright tasks)
Google Chrome (for Selenium tasks)
```

### Installation

```bash
# Clone the repository
git clone https://github.com/ALIADE1/ABM-Egypt-Tasl.git
cd ABM-Egypt-Tasl

# Install dependencies
pip install playwright playwright-stealth selenium webdriver-manager

# Install Playwright browsers
playwright install
```

### Running the Tasks

```bash
# Task 1 — Turnstile Bypass
cd Task1
python automation.py

# Task 2 — Network Interception
cd Task2
python automation.py

# Task 3 — DOM Scraping
cd Task3
python automation.py
```

---

## 📁 Project Structure

```
├── 📄 README.md
├── 📄 Python Developer Assessment (Automation & Crawling).pdf
│
├── 📂 Task1/                          # Turnstile CAPTCHA Bypass
│   ├── automation.py                  # Main automation script
│   └── Video.mp4                      # Demo recording
│
├── 📂 Task2/                          # Network Interception
│   ├── automation.py                  # Intercept & inject script
│   └── Video.mp4                      # Demo recording
│
├── 📂 Task3/                          # DOM Scraping
│   ├── automation.py                  # Selenium scraper
│   ├── allimages.json                 # All extracted images
│   ├── visible_images_only.json       # 9 visible images
│   └── instruction.txt                # Scraped instruction text
│
└── 📂 Task4/                          # System Architecture
    └── Task4_System_Diagram.png       # Architecture diagram
```

---

## 📊 Results

| Task | Objective | Status |
|------|-----------|--------|
| Task 1 | Turnstile bypass ≥ 60% success rate | ✅ Achieved |
| Task 2 | Network interception & token injection | ✅ Completed |
| Task 3 | DOM scraping with visibility resolution | ✅ Completed |
| Task 4 | System architecture diagram | ✅ Completed |

---

<p align="center">
  <b>Built with 🐍 Python &nbsp;•&nbsp; Playwright &nbsp;•&nbsp; Selenium</b>
</p>
