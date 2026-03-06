import os
import json
import re
from typing import Optional
from dotenv import load_dotenv
from serpapi import GoogleSearch

from google.adk.agents import Agent

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(os.path.join(BASE_DIR, "prompt.md"))

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY not found in .env file")

# ==========================================
# Helper: extract price from text
# ==========================================
def extract_price_from_text(text: str) -> Optional[float]:
    """
    Extract a price from a string. Handles:
    - $1,234.56
    - 1234.56 USD
    - Price ranges: $1,000 - $2,000 (returns lower bound)
    """
    # Try to find a price range first, take the lower bound
    range_match = re.search(r'\$\s?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$\s?\d+', text)
    if range_match:
        return float(range_match.group(1).replace(',', ''))

    # Single price with $
    match = re.search(r'\$\s?(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
    if match:
        return float(match.group(1).replace(',', ''))

    # Single price with USD
    match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD', text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(',', ''))

    return None

# ==========================================
# TOOL: Search Marketplace Deals
# ==========================================
def search_marketplace_deals(
    query: str,
    marketplace: str = "ebay",
    max_price: Optional[float] = None,
    condition: Optional[str] = None
) -> dict:
    """
    Search eBay or Alibaba for items matching the query and return those priced below max_price.
    For eBay, you can filter by condition ("new", "used").
    Returns a dictionary with a list of deals (title, price, condition, link).
    """
    print("--- Tool: search_marketplace_deals called ---")
    print(f"   Marketplace: {marketplace}, Query: {query}, max_price: {max_price}, condition: {condition}")

    # Determine engine and parameters
    if marketplace.lower() == "ebay":
        params = {
            "_nkw": query,
            "api_key": SERPAPI_API_KEY,
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "num": 20
        }
    elif marketplace.lower() == "alibaba":
        # Use Google Search to find Alibaba pages
        params = {
            "q": f"site:alibaba.com {query}",
            "api_key": SERPAPI_API_KEY,
            "engine": "google",
            "num": 20,
            "gl": "us",
            "hl": "en"
        }
        # Condition not applicable for Alibaba via this method
        condition = None
    else:
        return {
            "status": "error",
            "error": f"Unsupported marketplace: {marketplace}. Use 'ebay' or 'alibaba'.",
            "deals": []
        }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        # Debug: print raw response (first 2000 chars)
        print("===== SerpAPI Raw Response =====")
        print(json.dumps(results, indent=2)[:2000])
        print("=================================")

        # For eBay, use organic_results; for Alibaba (via Google), also use organic_results
        organic = results.get("organic_results", [])
        if not organic:
            print("⚠️ No organic results returned")
            return {
                "status": "success",
                "marketplace": marketplace,
                "query": query,
                "max_price": max_price,
                "condition": condition,
                "deals": [],
                "count": 0,
                "debug": "No organic results"
            }

        deals = []
        for idx, item in enumerate(organic):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")

            # For eBay, we have structured price and condition; for Alibaba we need to extract from text
            if marketplace.lower() == "ebay":
                price_data = item.get("price")
                item_condition = item.get("condition", "").lower()
                price = None
                if isinstance(price_data, (int, float)):
                    price = float(price_data)
                elif isinstance(price_data, str):
                    price_clean = re.sub(r'[^\d.]', '', price_data.replace(',', ''))
                    if price_clean:
                        try:
                            price = float(price_clean)
                        except ValueError:
                            pass
                elif isinstance(price_data, dict):
                    if "extracted" in price_data and isinstance(price_data["extracted"], (int, float)):
                        price = float(price_data["extracted"])
                    else:
                        price_str = price_data.get("raw") or price_data.get("display") or price_data.get("value")
                        if price_str:
                            price_clean = re.sub(r'[^\d.]', '', str(price_str).replace(',', ''))
                            if price_clean:
                                try:
                                    price = float(price_clean)
                                except ValueError:
                                    pass
            else:  # Alibaba
                # Extract price from title and snippet
                combined_text = title + " " + snippet
                price = extract_price_from_text(combined_text)
                item_condition = ""  # not available

            print(f"\n--- Item {idx+1} ---")
            print(f"Title: {title}")
            print(f"Snippet: {snippet}")
            print(f"Extracted price: {price}")
            print(f"Condition: {item_condition}")

            if price is None:
                print("   ⏭️ Skipped: could not extract price")
                continue

            # Apply filters
            if max_price is not None and price > max_price:
                print(f"   ⏭️ Skipped: price {price} > max_price {max_price}")
                continue
            if condition and condition.lower() not in item_condition:
                print(f"   ⏭️ Skipped: condition '{item_condition}' does not match '{condition}'")
                continue

            deals.append({
                "title": title,
                "price": price,
                "condition": item_condition if item_condition else None,
                "link": link,
                "marketplace": marketplace
            })
            print(f"   ✅ Added to deals")

        deals.sort(key=lambda x: x["price"])
        print(f"\n✅ Total deals found: {len(deals)}")

        return {
            "status": "success",
            "marketplace": marketplace,
            "query": query,
            "max_price": max_price,
            "condition": condition,
            "deals": deals,
            "count": len(deals)
        }

    except Exception as e:
        print(f"❌ SerpAPI error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "deals": []
        }

# ==========================================
# CREATE ITEM FINDER AGENT
# ==========================================
item_finder_agent = Agent(
    name="item_finder",
    model="gemini-2.0-flash",
    description="An agent that finds great deals on eBay or Alibaba by comparing prices to user-defined budgets.",
    instruction=instructions,
    tools=[search_marketplace_deals]
)

root_agent = item_finder_agent