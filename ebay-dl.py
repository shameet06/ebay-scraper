import argparse
import json
import time
import requests
from bs4 import BeautifulSoup

def get_text(item, selector):
    tags = item.select(selector)

    if len(tags) == 0:
        return None

    return tags[0].text.strip()

def price_in_cents(text):
    if text is None:
        return None
    number = ""

    for character in text:
        if character in "0123456789.":
            number += character
        elif character == ",":
            continue
        elif number != "":
            break

    if number == "":
        return None

    parts = number.split(".")
    dollars = int(parts[0])
    cents = 0

    if len(parts) > 1:
        decimal = parts[1] + "00"
        cents = int(decimal[:2])

    return dollars * 100 + cents

def extract_items(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for item in soup.select(".s-item"):
        name = get_text(item, ".s-item__title")

        if name == "Shop on eBay":
            continue
        price_text = get_text(item, ".s-item__price")
        price = price_in_cents(price_text)

        status = get_text(item, ".SECONDARY_INFO")
        shipping_text = get_text(item, ".s-item__shipping")
        shipping = None

        if shipping_text is not None:
            if "free" in shipping_text.lower():
                shipping = 0
            else:
                shipping = price_in_cents(shipping_text)
        returns_text = get_text(item, ".s-item__free-returns")
        free_returns = None

        if returns_text is not None:
            free_returns = "free returns" in returns_text.lower()
        sold_text = get_text(item, ".s-item__hotness")
        items_sold = None

        if sold_text is not None:
            if "sold" in sold_text.lower():
                number = ""

                for character in sold_text:
                    if character in "0123456789":
                        number += character
                    elif character == ",":
                        continue
                    elif number != "":
                        break

                if number != "":
                    items_sold = int(number)

        items.append({
            "name": name,
            "price": price,
            "status": status,
            "shipping": shipping,
            "free_returns": free_returns,
            "items_sold": items_sold,
        })
    return items

def json_writer():
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", required=True)
    parser.add_argument("--pages-dir")
    args = parser.parse_args()

    all_items_list = []

    for page in range(1, 11):
        if args.pages_dir is not None:
            filename = args.pages_dir + "/page-" + str(page) + ".html"

            with open(filename, encoding="utf-8") as f:
                html = f.read()

        else:
            try:
                response = requests.get(
                    "https://www.ebay.com/sch/i.html",
                    params={"_nkw": args.search, "_pgn": page},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=10,
                )

                print("Page", page, "HTTP status:", response.status_code)
                response.raise_for_status()

            except requests.exceptions.RequestException:
                print("Download failed. Run with --pages-dir practice-pages.")
                return

            html = response.text

            if (
                "robot check" in html.lower()
                or "pardon our interruption" in html.lower()
                or "verify you are human" in html.lower()
            ):
                print("Robot check. Run with --pages-dir practice-pages.")
                return

        items = extract_items(html)

        if len(items) == 0:
            print("No listings found on page", page)
            print("Check the HTML or use --pages-dir practice-pages.")
            return

        for item in items:
            all_items_list.append(item)
        print("Page", page, "listings:", len(items))

        if args.pages_dir is None and page < 10:
            time.sleep(1)

    filename = args.search + ".json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_items_list, f, indent=2)
    print("Saved", len(all_items_list), "listings to", filename)


json_writer()