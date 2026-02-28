#!/usr/bin/env python3
"""
Complete GitHub Signup Automation
Run this directly: python3 github_signup.py
"""

import os
import sys
import time
import random
import string
import json
import subprocess

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    from playwright.sync_api import sync_playwright

EMAIL = "annoyedcare990@agentmail.to"
API_KEY = "am_4442cf45463cc0a689ae60d8a7b4cb8a4b807d561f1c6e41bd7a30a036a3644c"

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(16))

def check_agentmail_inbox():
    """Check AgentMail for verification emails."""
    try:
        import requests
        headers = {"Authorization": f"Bearer {API_KEY}"}
        resp = requests.get(
            f"https://api.agentmail.to/v1/inboxes/{EMAIL}/messages",
            headers=headers
        )
        if resp.status_code == 200:
            messages = resp.json().get("messages", [])
            for msg in messages:
                if "github" in msg.get("subject", "").lower():
                    return msg
        return None
    except Exception as e:
        print(f"Could not check email: {e}")
        return None

def main():
    password = generate_password()
    username = f"raczek-{random.randint(1000,9999)}"
    
    print("="*60)
    print("GITHUB SIGNUP AUTOMATION")
    print("="*60)
    print(f"Email: {EMAIL}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Set to True if you don't want to see the browser
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        
        try:
            # Step 1: Email
            print("Step 1: Opening GitHub signup...")
            page.goto("https://github.com/signup", wait_until="networkidle")
            page.wait_for_selector('input#email', timeout=10000)
            print("Entering email...")
            page.fill('input#email', EMAIL)
            page.click('button:has-text("Continue")')
            time.sleep(3)
            
            # Step 2: Password
            print("Step 2: Entering password...")
            page.wait_for_selector('input#password', timeout=10000)
            page.fill('input#password', password)
            page.click('button:has-text("Continue")')
            time.sleep(3)
            
            # Step 3: Username
            print("Step 3: Entering username...")
            page.wait_for_selector('input#login', timeout=10000)
            page.fill('input#login', username)
            page.click('button:has-text("Continue")')
            time.sleep(3)
            
            # Step 4: Newsletter preference
            print("Step 4: Skipping newsletter...")
            page.click('button:has-text("Continue")')
            time.sleep(3)
            
            # Check for CAPTCHA
            if page.is_visible('iframe[src*="recaptcha"]', timeout=5000) or \
               page.is_visible('.captcha', timeout=5000):
                print("\n⚠️  CAPTCHA DETECTED!")
                print("Please solve the CAPTCHA manually in the browser window.")
                print("Press Enter when done...")
                input()
            
            # Save credentials
            print("\n✅ Saving credentials...")
            with open("github-credentials.txt", "w") as f:
                f.write(f"Username: {username}\n")
                f.write(f"Email: {EMAIL}\n")
                f.write(f"Password: {password}\n")
            
            print("\n" + "="*60)
            print("SIGNUP PROGRESS SAVED!")
            print("="*60)
            print("\nNext steps:")
            print("1. Check your email for verification link")
            print("2. Click the link to verify your account")
            print("3. Login to GitHub with your credentials")
            
            # Keep browser open for manual steps
            print("\nBrowser will stay open for 60 seconds...")
            time.sleep(60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            page.screenshot(path="error-screenshot.png")
            print("Screenshot saved to error-screenshot.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    main()
