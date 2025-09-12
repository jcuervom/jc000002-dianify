#!/usr/bin/env python3
"""
Test script to verify Playwright can launch and access a basic webpage
"""
import asyncio
import os
from playwright.async_api import async_playwright

async def test_playwright():
    print("=== Testing Playwright ===")
    
    async with async_playwright() as p:
        print("Launching browser...")
        
        try:
            # Use the same configuration as the main scraper
            browser_args = [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-back-forward-cache",
                "--disable-ipc-flooding-protection",
                "--single-process"
            ]
            
            # Check if we're on Heroku and need to specify executable path
            chromium_path = None
            if os.getenv("DYNO"):  # On Heroku
                browsers_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
                if browsers_path:
                    import glob
                    chromium_pattern = os.path.join(browsers_path, "chromium-*/chrome-linux/chrome")
                    matches = glob.glob(chromium_pattern)
                    if matches:
                        chromium_path = matches[0]
                        print(f"Using Chromium: {chromium_path}")
            
            browser = await p.chromium.launch(
                headless=True,
                executable_path=chromium_path if chromium_path else None,
                args=browser_args
            )
            
            print("✓ Browser launched successfully")
            
            page = await browser.new_page()
            print("✓ New page created")
            
            # Test navigation to a simple page
            await page.goto("https://httpbin.org/html", wait_until="networkidle")
            print("✓ Navigation successful")
            
            # Test basic interaction
            title = await page.title()
            print(f"✓ Page title: {title}")
            
            await browser.close()
            print("✓ Browser closed successfully")
            
            print("\n🎉 All Playwright tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Playwright test failed: {e}")
            return False

if __name__ == "__main__":
    result = asyncio.run(test_playwright())
    exit(0 if result else 1)
