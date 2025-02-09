import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

SEARCH_QUERY = "Tikka Chicken Slices"
BASE_URL = "https://www.trolley.co.uk"

def scrape_trolley():
    search_url = f"{BASE_URL}/search/?from=search&q={SEARCH_QUERY}"
    response = requests.get(search_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to retrieve search results: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    products = []
    
    for index, product in enumerate(soup.select(".product-item")):
        if index >= 5:  # Limit to top 5 products
            break

        product_id = product.get("data-id", "N/A")
        image_tag = product.select_one("._img img")
        image_url = BASE_URL + image_tag["src"] if image_tag else "N/A"
        price_tag = product.select_one("._price")
        price = price_tag.text.strip().split()[0] if price_tag else "N/A"  # Only get the first part of the price
        brand_tag = product.select_one("._brand")
        brand = brand_tag.text.strip() if brand_tag else "N/A"
        desc_tag = product.select_one("._desc")
        product_name = desc_tag.text.strip() if desc_tag else "N/A"
        link_tag = product.select_one("a")
        product_link = BASE_URL + link_tag["href"] if link_tag else "N/A"

        # Fetch supermarket data from product page
        supermarkets = scrape_supermarkets(product_link)

        products.append({
            "id": product_id,
            "brand": brand,
            "name": product_name,
            "image": image_url,
            "price": price,
            "link": product_link,
            "supermarkets": supermarkets
        })
    
    return products

def scrape_supermarkets(product_url):
    """Visits a product page and extracts supermarket names and prices (without links)."""
    response = requests.get(product_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to retrieve product page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    supermarkets = []

    for store in soup.select("._item"):
        store_name_tag = store.select_one(".store-logo")
        store_name = store_name_tag["title"] if store_name_tag else "N/A"
        price_tag = store.select_one("._price b")
        price = price_tag.text.strip().split()[0] if price_tag else "N/A"  # Only get the first part of the price

        if store_name != "N/A" and price != "N/A":  # Skip adding N/A values
            supermarkets.append({
                "store": store_name,
                "price": price
            })

    return supermarkets

if __name__ == "__main__":
    data = scrape_trolley()
    
    import json
    print(json.dumps(data, indent=4, ensure_ascii=False))