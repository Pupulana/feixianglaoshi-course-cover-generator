from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

def capture_from_url(url, output_path="input_screenshot.png"):
    """Capture a screenshot from a URL using Selenium."""
    print(f"Starting browser to capture: {url}")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,800")
    chrome_options.add_argument("--force-device-scale-factor=2")
    
    # Auto-download and setup ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Go to URL
        driver.get(url)
        
        # Wait for page load
        time.sleep(3)
        
        # Try to find .iframe-container element
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".iframe-container"))
            )
            print("Found .iframe-container")
            
            # Wait for animation rendering
            time.sleep(3)
            
            # Screenshot the element
            element.screenshot(output_path)
            print(f"Captured screenshot of content container to {output_path}")
        except Exception as e:
            print(f"Timeout waiting for .iframe-container: {e}")
            # Fallback to full page screenshot
            time.sleep(3)
            driver.save_screenshot(output_path)
            print(f"Captured full page screenshot to {output_path}")
        
        return output_path

    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    TARGET_URL = "https://musk-online.fbcontent.cn/pub-musk-ai-studio/workflow/file/document/VcXtodDJ7Zeep4GcJ8vMxT.html"
    OUTPUT_FILE = "input_screenshot.png"
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    capture_from_url(TARGET_URL, OUTPUT_FILE)
