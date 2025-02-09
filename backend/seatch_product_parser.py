import requests
from bs4 import BeautifulSoup

search_query = "egg"

URL = f"https://www.trolley.co.uk/search/?from=search&q={search_query}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def scrape_trolley():
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    products = []
    
    for product in soup.select(".product-item"):
        product_id = product.get("data-id", "N/A")
        image_tag = product.select_one(".product-item img")
        image_url = "https://www.trolley.co.uk" + image_tag["src"] if image_tag else "N/A"
        price_tag = product.select_one("._price")
        price = price_tag.text.strip() if price_tag else "N/A"
        
        products.append({
            "id": product_id,
            "image": image_url,
            "price": price
        })
    
    return products

if __name__ == "__main__":
    data = scrape_trolley()
    for item in data:
        print(item)
