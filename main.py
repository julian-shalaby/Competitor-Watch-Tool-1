from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from openai import OpenAI
import json
from cursor_negative_sentiment import save_negative_posts

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_sentiment(title):
    functions = [
        {
            "name": "determine_sentiment",
            "description": "Determine if the post has a positive, negative, or neutral sentiment about the product 'Cursor' (a development tool/company)",
            "parameters": {
                "type": "object",
                "properties": {
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral"],
                        "description": "The sentiment of the post towards Cursor"
                    }
                },
                "required": ["sentiment"]
            }
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a sentiment analyzer specifically focused on analyzing sentiment towards the product/company 'Cursor'. Analyze if the given title expresses positive, negative, or neutral sentiment about Cursor."},
            {"role": "user", "content": f"Analyze the sentiment of this title towards Cursor: {title}"}
        ],
        functions=functions,
        function_call={"name": "determine_sentiment"}
    )

    function_call = response.choices[0].message.function_call
    sentiment_result = json.loads(function_call.arguments)
    return sentiment_result["sentiment"]

def scroll_page(driver, scroll_pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def open_browser_with_url():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    url = "https://www.reddit.com/search/?q=cursor&type=posts&t=week&iId=ec7ca0d8-a79c-4a2b-98a1-7c7b0d8851ed"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="post-title"]'))
        )

        print("Starting to scroll the page...")
        scroll_page(driver)

        post_titles = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="post-title"]')

        print(f"\nFound {len(post_titles)} posts:")
        print("-" * 50)

        negative_posts = []

        for i, title in enumerate(post_titles, 1):
            title_text = title.text
            link = title.get_attribute('href')
            sentiment = analyze_sentiment(title_text)

            print(f"{i}. Title: {title_text}")
            print(f"   Link: {link}")
            print(f"   Sentiment: {sentiment}")
            print("-" * 50)

            if sentiment == "negative":
                negative_posts.append([title_text, link, sentiment])

        if negative_posts:
            filename = save_negative_posts(negative_posts)
            print(f"\nNegative sentiment posts have been saved to: {filename}")
        else:
            print("\nNo negative sentiment posts were found.")

    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        input("Press Enter to close the browser...")
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OPENAI_API_KEY environment variable")
        exit(1)
    open_browser_with_url()