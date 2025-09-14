#!/usr/bin/env python3
"""
Debug script to check Heroku environment for Playwright browsers
"""
import os
import glob

def debug_heroku_environment():
    print("=== Heroku Environment Debug ===")
    
    # Check if we're on Heroku
    print(f"DYNO: {os.getenv('DYNO')}")
    
    # Check all playwright-related environment variables
    playwright_vars = [
        'CHROMIUM_EXECUTABLE_PATH',
        'FIREFOX_EXECUTABLE_PATH', 
        'WEBKIT_EXECUTABLE_PATH',
        'PLAYWRIGHT_BROWSERS_PATH',
        'BUILDPACK_BROWSERS_INSTALL_PATH',
        'PLAYWRIGHT_BUILDPACK_BROWSERS'
    ]
    
    print("\n=== Environment Variables ===")
    for var in playwright_vars:
        value = os.getenv(var)
        print(f"{var}: {value}")
        
        # If it's a path, check if it exists
        if value and ('PATH' in var or 'chrome' in value.lower()):
            exists = os.path.exists(value) if value != '0' else False
            print(f"  → Exists: {exists}")
    
    # Search for browser installations
    print("\n=== Searching for Browser Installations ===")
    search_patterns = [
        "/app/browsers/*",
        "/app/browsers/*/*", 
        "/app/browsers/*/*/*",
        "/app/.cache/ms-playwright/*",
        "/tmp/playwright_browsers/*",
        "/usr/bin/google-chrome*",
        "/usr/bin/chromium*"
    ]
    
    for pattern in search_patterns:
        matches = glob.glob(pattern)
        if matches:
            print(f"{pattern}:")
            for match in matches[:5]:  # Limit to first 5 matches
                print(f"  → {match}")
                
    # Check for chrome executables specifically
    print("\n=== Chrome Executable Search ===")
    chrome_patterns = [
        "/app/**/chrome",
        "/app/**/chromium"
    ]
    
    for pattern in chrome_patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            print(f"{pattern}:")
            for match in matches[:5]:  # Limit to first 5 matches
                is_executable = os.access(match, os.X_OK)
                print(f"  → {match} (executable: {is_executable})")

if __name__ == "__main__":
    debug_heroku_environment()