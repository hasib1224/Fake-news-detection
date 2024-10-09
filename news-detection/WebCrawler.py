import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import pandas as pd


class WebScraper:
    def __init__(self, base_url, max_depth=3, delay=1):
        self.base_url = base_url
        self.visited_urls = set()
        self.max_depth = max_depth
        self.delay = delay
        self.data = []  # To store the scraped data

    # Method to scrape a page and extract its data
    def scrape_page(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Example: Extracting article title and content if the URL contains 'news'
            if "news" in url:
                title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No Title"
                content = "\n".join([p.get_text(strip=True) for p in soup.find_all('p')])

                # Store the scraped data
                self.data.append({
                    'url': url,
                    'title': title,
                    'content': content
                })

            # Extract all internal links
            internal_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('/')]
            internal_links = [urljoin(self.base_url, link) for link in internal_links]

            return internal_links

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            return []

    # Recursive function to visit links
    def crawl(self, url, depth=0):
        if url in self.visited_urls or depth > self.max_depth:
            return  # Stop if URL is already visited or depth limit is reached

        print(f"Crawling {url} at depth {depth}")
        self.visited_urls.add(url)

        # Scrape the page and get the links
        links = self.scrape_page(url)

        # Delay to avoid overwhelming the server
        time.sleep(self.delay)

        # Visit each link recursively
        for link in links:
            self.crawl(link, depth + 1)

    # Method to start crawling
    def start_crawling(self):
        self.crawl(self.base_url)

    # Method to save the scraped data to a CSV file
    def save_to_csv(self, filename='news_data.csv'):
        if self.data:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False)
            print(f"Data successfully saved to {filename}")
        else:
            print("No data to save.")


# Instantiate the WebScraper class and start crawling
if __name__ == "__main__":
    scraper = WebScraper(base_url="https://www.thedailystar.net", max_depth=3, delay=1)
    
    # Start crawling the website
    scraper.start_crawling()

    # Save the scraped data to a CSV file
    scraper.save_to_csv('news_data.csv')
