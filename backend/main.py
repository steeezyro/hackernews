from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://news.ycombinator.com/")
        
        # Select the top 10 story links
        items = page.query_selector_all('tr.athing')[:10]
        for idx, item in enumerate(items, 1):
            title = item.query_selector('.titleline a').inner_text()
            url = item.query_selector('.titleline a').get_attribute('href')
            print(f"{idx}. {title} ({url})")
        
        browser.close()


if __name__ == "__main__":
    main()
