
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from loguru import logger
import re
# import koreanize_matplotlib # Commented out due to ModuleNotFoundError

# Logger setup
logger.add("yes24/log/file_{time}.log", rotation="500 MB", level="INFO")

BASE_URL = "https://www.yes24.com/product/category/CategoryProductContents"
CATEGORY_ID = "001001003032" # Example category ID for "IT/모바일" -> "프로그래밍" -> "웹 프로그래밍"

HEADERS = {
    "host": "www.yes24.com",
    "referer": f"https://www.yes24.com/product/category/display/{CATEGORY_ID}",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
}

def parse_book_info(item_unit):
    """Parses a single book item HTML unit and extracts relevant information."""
    book = {}

    # Book URL and Title
    title_link = item_unit.select_one(".info_name .gd_name")
    if title_link:
        book["title"] = title_link.get_text(strip=True)
        book["url"] = "https://www.yes24.com" + title_link["href"]
    else:
        book["title"] = None
        book["url"] = None

    # English Title/Subtitle
    english_title_span = item_unit.select_one(".info_name .gd_nameE")
    book["english_title"] = english_title_span.get_text(strip=True) if english_title_span else None

    # Author
    author_span = item_unit.select_one(".info_pubGrp .info_auth a")
    book["author"] = author_span.get_text(strip=True) if author_span else None

    # Publisher
    publisher_span = item_unit.select_one(".info_pubGrp .info_pub a")
    book["publisher"] = publisher_span.get_text(strip=True) if publisher_span else None

    # Publication Date
    pub_date_span = item_unit.select_one(".info_pubGrp .info_date")
    book["publication_date"] = pub_date_span.get_text(strip=True) if pub_date_span else None

    # Prices
    selling_price_strong = item_unit.select_one(".info_price .txt_num .yes_b")
    book["selling_price"] = int(re.sub(r"[^\d]", "", selling_price_strong.get_text(strip=True))) if selling_price_strong else None

    original_price_span = item_unit.select_one(".info_price .txt_num.dash .yes_m")
    book["original_price"] = int(re.sub(r"[^\d]", "", original_price_span.get_text(strip=True))) if original_price_span else None

    discount_rate_span = item_unit.select_one(".info_price .txt_sale .num")
    book["discount_rate"] = int(discount_rate_span.get_text(strip=True)) if discount_rate_span else None

    # Sales Index
    sales_index_span = item_unit.select_one(".info_rating .saleNum")
    book["sales_index"] = int(re.sub(r"[^\d]", "", sales_index_span.get_text(strip=True))) if sales_index_span else None
    
    # Review Count and Rating
    review_count_a = item_unit.select_one(".info_rating .rating_rvCount a .txC_blue")
    book["review_count"] = int(re.sub(r"[^\d]", "", review_count_a.get_text(strip=True))) if review_count_a else 0

    rating_span = item_unit.select_one(".info_rating .rating_grade .yes_b")
    book["rating"] = float(rating_span.get_text(strip=True)) if rating_span else None

    # Tags
    tags = [tag.get_text(strip=True) for tag in item_unit.select(".info_tag .tag a")]
    book["tags"] = ", ".join(tags) if tags else None

    # Description (Read)
    description_div = item_unit.select_one(".info_read")
    book["description"] = description_div.get_text(strip=True) if description_div else None

    return book

def scrape_category_page(page_num, page_size=24):
    """Scrapes a single page of a category and returns a list of book dictionaries."""
    params = {
        "dispNo": CATEGORY_ID,
        "order": "SINDEX_ONLY",
        "addOptionTp": "0",
        "page": page_num,
        "size": page_size,
        "statGbYn": "N",
        "viewMode": "",
        "_options": "",
        "directDelvYn": "",
        "usedTp": "0",
        "elemNo": "0",
        "elemSeq": "0",
        "seriesNumber": "0",
    }

    try:
        logger.info(f"Scraping page {page_num}...")
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        soup = BeautifulSoup(response.text, "html.parser")
        item_units = soup.select(".itemUnit")

        if not item_units:
            logger.info(f"No item units found on page {page_num}. End of category or parsing error.")
            return []

        books_on_page = [parse_book_info(unit) for unit in item_units]
        logger.info(f"Successfully scraped {len(books_on_page)} books from page {page_num}.")
        return books_on_page

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for page {page_num}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing page {page_num}: {e}")
        return []

def main():
    all_books = []
    max_pages = 5 # Define how many pages to scrape. Adjust as needed.
    page_size = 24

    for page in range(1, max_pages + 1):
        books = scrape_category_page(page, page_size)
        if not books:
            break # Stop if no books are found on a page (e.g., reached end of category)
        all_books.extend(books)
        time.sleep(1) # Be polite and avoid overwhelming the server

    if all_books:
        df = pd.DataFrame(all_books)
        output_path = "yes24/data/yes24_ai.csv" # Updated output path
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"Successfully scraped {len(all_books)} books and saved to {output_path}")
    else:
        logger.warning("No books were scraped.")

if __name__ == "__main__":
    main()
