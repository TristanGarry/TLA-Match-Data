import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd


def get_patch_dates():
    # URL of the Tough Love Arena log page
    url = 'https://about.toughlovearena.com/log/'

    # Start a Selenium WebDriver
    driver = webdriver.Chrome()  # Use the appropriate WebDriver for your browser

    # Open the URL
    driver.get(url)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "Changelog_version__zd1GB")))

    # Lists to store the data
    dates = []
    patches = []

    # Scroll to the bottom of the page to load more content
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for some time to load the new content
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parse the loaded content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all patch entries
    patch_entries = soup.find_all('div', class_='Changelog_version__zd1GB')

    # Loop through each patch entry and extract the version and date
    for entry in patch_entries:
        # Extract the patch number
        patch_element = entry.find('a', class_='Changelog_patch__J1sLl')
        if not patch_element:
            patch_element = entry.find('a', class_='Changelog_minor__YRDzc')
        if patch_element:
            patch = patch_element.text.strip()
            patches.append(patch)


        # Extract the date
        date_element = entry.find('span', class_='Changelog_date__Hhk0J')
        if date_element:
            date = date_element.text.strip()
            dates.append(date)

    # Create a DataFrame with the extracted data
    df = pd.DataFrame({
        'date': dates,
        'patch': patches
    })

    # Save the DataFrame to a CSV file
    df.to_csv('tough_love_arena_patches.csv', index=False)

    # Close the WebDriver
    driver.quit()

    print("Data successfully saved to tough_love_arena_patches.csv")


if __name__ == "__main__":
    get_patch_dates()

