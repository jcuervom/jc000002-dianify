#!/usr/bin/env python3
"""
Script to verify Playwright installation on Heroku
"""
import os
import glob
import sys

def verify_playwright():
    print("=== Playwright Verification ===")
    
    # Check if we're on Heroku
    if os.getenv("DYNO"):
        print("✓ Running on Heroku")
        
        # Check PLAYWRIGHT_BROWSERS_PATH
        browsers_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
        if browsers_path:
            print(f"✓ PLAYWRIGHT_BROWSERS_PATH: {browsers_path}")
            
            # Look for chromium
            chromium_pattern = os.path.join(browsers_path, "chromium-*/chrome-linux/chrome")
            matches = glob.glob(chromium_pattern)
            if matches:
                print(f"✓ Chromium found: {matches[0]}")
                return True
            else:
                print("✗ Chromium not found in browsers path")
                return False
        else:
            print("✗ PLAYWRIGHT_BROWSERS_PATH not set")
            return False
    else:
        print("ℹ Running locally")
        return True

def verify_import():
    try:
        import playwright
        print(f"✓ Playwright import successful, version: {playwright.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Playwright import failed: {e}")
        return False

if __name__ == "__main__":
    playwright_ok = verify_playwright()
    import_ok = verify_import()
    
    if playwright_ok and import_ok:
        print("\n🎉 All checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed!")
        sys.exit(1)
