import os
import ssl
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context
import undetected_chromedriver as uc
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_stealth(years):
    print("Initializing Stealth Driver...")
    # This opens a version of Chrome that sites cannot easily identify as a bot
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    
    all_data = []
    headers_row = []

    try:
        for year in years:
            print(f"--- Fetching Year: {year} ---")
            url = f"https://www.chittorgarh.com/report/ipo-lead-manager-vs-listing-gain/99/sme/47/?year={year}"
            driver.get(url)

            # Wait for the table to appear (max 20 seconds)
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                
                # Scroll a little to mimic a human looking at the page
                driver.execute_script("window.scrollTo(0, 500);")
                time.sleep(4) # Important: Give the site time to load the dynamic data

                # Identify the main data table
                table = driver.find_element(By.CSS_SELECTOR, "table.table")
                
                # Get Headers only once
                if not headers_row:
                    headers_row = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]
                    headers_row.append("Year")

                # Get rows from the table body
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                year_count = 0
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    # Real data rows in this report usually have ~11 columns
                    if len(cells) > 5:
                        data = [c.text.strip() for c in cells]
                        data.append(year)
                        all_data.append(data)
                        year_count += 1
                
                print(f"Success! Found {year_count} companies for {year}")

            except Exception as e:
                print(f"Error on {year}: Table not found. Try increasing sleep time.")

    finally:
        driver.quit()

    return pd.DataFrame(all_data, columns=headers_row) if all_data else pd.DataFrame()

# Run for 2021-2024
target_years = [2021, 2022, 2023, 2024]
df = scrape_stealth(target_years)

if not df.empty:
    df.to_csv("ipo_final_data.csv", index=False)
    print(f"\nFINISHED: Saved {len(df)} records to ipo_final_data.csv")
else:
    print("\nFAILED: No data found. Please check if the website works in your normal Chrome.")