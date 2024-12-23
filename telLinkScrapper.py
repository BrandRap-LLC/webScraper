import requests
from bs4 import BeautifulSoup
import csv
import os

def fetch_sitemap_urls(sitemap_url):
    """
    Fetch all URLs from the sitemap or sitemap index.
    """
    response = requests.get(sitemap_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "xml")
    
    # Check if it's a sitemap index
    sitemap_tags = soup.find_all("sitemap")
    if sitemap_tags:
        # Recursively fetch URLs from each sitemap in the index
        urls = []
        for sitemap in sitemap_tags:
            loc = sitemap.find("loc").text
            urls.extend(fetch_sitemap_urls(loc))
        return urls
    else:
        # Extract URLs directly from the sitemap
        return [loc.text for loc in soup.find_all("loc")]

def fetch_html_content(url):
    """
    Fetch HTML content for a given URL.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_tel_links(html_content, page_url):
    """
    Extract all 'tel:' links from the HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    tel_links = []
    for a_tag in soup.find_all("a", href=True):
        if a_tag["href"].startswith("tel:"):
            tel_links.append({"tel": a_tag["href"], "page_url": page_url})
    return tel_links

def scrape_tel_links(sitemap_url, output_csv):
    """
    Scrape all 'tel:' links from pages listed in the sitemap and save to a CSV.
    """
    urls = fetch_sitemap_urls(sitemap_url)
    tel_links = []

    for i, url in enumerate(urls, start=1):
        print(f"Fetching {url} ({i}/{len(urls)})...")
        try:
            html_content = fetch_html_content(url)
            tel_links.extend(extract_tel_links(html_content, url))
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    # Save results to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["tel", "page_url"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tel_links)

    print(f"All 'tel:' links saved to {output_csv}.")

if __name__ == "__main__":
    sitemap_url = input("Enter the sitemap URL: ").strip()
    output_csv = input("Enter the output CSV filename (e.g., output.csv): ").strip()
    scrape_tel_links(sitemap_url, output_csv)
