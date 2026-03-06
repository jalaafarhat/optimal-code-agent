import os
import json
import re
from dotenv import load_dotenv
from serpapi import GoogleSearch

from google.adk.agents import Agent

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# Load Instructions (prompt.md)
# ==========================================
def load_instructions(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

instructions = load_instructions(os.path.join(BASE_DIR, "prompt.md"))

# ==========================================
# MACHINE DATABASE
# ==========================================
MACHINE_FILE = os.path.join(BASE_DIR, "machines.json")

def load_machine_db():
    if not os.path.exists(MACHINE_FILE):
        with open(MACHINE_FILE, "w") as f:
            json.dump({}, f)
    with open(MACHINE_FILE, "r") as f:
        return json.load(f)

def save_machine_db(data):
    with open(MACHINE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==========================================
# HELPER: Google Search via SerpAPI
# ==========================================
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY not found in .env file")

def google_search_api(query: str, num_results: int = 5) -> list:
    """Fetch Google search results using SerpAPI."""
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num_results,
        "engine": "google"
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get("organic_results", [])
        return [{"title": item.get("title", ""), "snippet": item.get("snippet", "")} for item in organic]
    except Exception as e:
        print(f"SerpAPI error: {e}")
        return []

# ==========================================
# HELPER EXTRACTORS
# ==========================================
def extract_price(text):
    """Extract a price in USD (e.g., $5,000 or 5000 USD)."""
    match = re.search(r'\$\s?(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
    if match:
        return float(match.group(1).replace(',', ''))
    match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD', text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

def extract_shipping(text):
    """Extract shipping cost mentions."""
    match = re.search(r'shipping[:\s]*\$?\s?(\d+(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

def extract_voltage(text):
    """Find voltage like 110V, 220V."""
    match = re.search(r'(\d{3})\s*V', text)
    return match.group(1) + 'V' if match else None

def extract_region(text):
    """Look for common supplier countries."""
    common_regions = ['China', 'USA', 'Germany', 'Japan', 'Italy', 'Taiwan', 'India', 'Vietnam']
    for region in common_regions:
        if region.lower() in text.lower():
            return region
    return None

# ==========================================
# TOOL: MACHINE SEARCH (with real API)
# ==========================================
def search_business_machines(keyword: str) -> dict:
    """
    Searches machine database. If machine not found → use SerpAPI to get real data,
    extract information, and add it to the database.
    """
    print("--- Tool: search_business_machines called ---")

    machines = load_machine_db()
    key = keyword.lower()

    if key in machines:
        return {
            "status": "found",
            "machine": key,
            "data": machines[key]
        }

    print(f"   -> Machine '{keyword}' not in DB. Searching with SerpAPI...")

    # Construct focused queries
    price_query = f"{keyword} price USD business"
    shipping_query = f"{keyword} shipping cost from China"
    power_query = f"{keyword} power voltage requirements"
    region_query = f"{keyword} manufacturer country"

    # Fetch results
    price_results = google_search_api(price_query)
    shipping_results = google_search_api(shipping_query)
    power_results = google_search_api(power_query)
    region_results = google_search_api(region_query)

    # Combine all snippets
    all_text = ""
    for res_list in [price_results, shipping_results, power_results, region_results]:
        for item in res_list:
            all_text += (item.get('title', '') + ' ' + item.get('snippet', '') + ' ')

    # Extract values
    price = extract_price(all_text)
    shipping = extract_shipping(all_text)
    voltage = extract_voltage(all_text)
    region = extract_region(all_text)

    # Build machine record with fallbacks
    new_machine = {
        "price_usd": price if price else 5000,
        "shipping_estimate": shipping if shipping else 1000,
        "power": voltage if voltage else "220V",
        "supplier_region": region if region else "China",
        "status": "auto_added_needs_verification" if (price and shipping) else "partial_needs_verification"
    }

    # Save to DB
    machines[key] = new_machine
    save_machine_db(machines)

    print(f"   -> Added machine '{key}' with data: {new_machine}")

    return {
        "status": "created",
        "machine": key,
        "data": new_machine
    }

# ==========================================
# OTHER TOOLS (unchanged)
# ==========================================
def estimate_import_cost(
    machine_price: float,
    shipping_cost: float,
    country: str,
    duty_percent: float
) -> dict:
    print("--- Tool: estimate_import_cost called ---")
    duty = machine_price * duty_percent
    landed_cost = machine_price + shipping_cost + duty
    return {
        "machine_price": machine_price,
        "shipping_cost": shipping_cost,
        "import_duty": duty,
        "landed_cost": landed_cost,
        "destination_country": country
    }

def validate_population_feasibility(
    location_population: int,
    required_daily_customers: int,
    conversion_rate: float
) -> dict:
    print("--- Tool: validate_population_feasibility called ---")
    potential_customers = location_population * conversion_rate
    feasible = potential_customers >= required_daily_customers
    return {
        "population": location_population,
        "potential_customers": potential_customers,
        "required_daily_customers": required_daily_customers,
        "feasible": feasible
    }

def check_voltage_compatibility(
    machine_voltage: str,
    country_voltage: str
) -> dict:
    print("--- Tool: check_voltage_compatibility called ---")
    compatible = machine_voltage == country_voltage
    return {
        "machine_voltage": machine_voltage,
        "country_voltage": country_voltage,
        "compatible": compatible
    }

def estimate_machine_maintenance(machine_price: float) -> dict:
    print("--- Tool: estimate_machine_maintenance called ---")
    yearly = machine_price * 0.08
    monthly = yearly / 12
    return {
        "yearly_maintenance": yearly,
        "monthly_maintenance": monthly
    }

def estimate_shipping_time(
    origin_country: str,
    destination_country: str
) -> dict:
    print("--- Tool: estimate_shipping_time called ---")
    shipping_days = 35
    return {
        "origin": origin_country,
        "destination": destination_country,
        "shipping_days": shipping_days
    }

def check_business_legality(
    business_type: str,
    country: str
) -> dict:
    print("--- Tool: check_business_legality called ---")
    banned = ["plastic bag manufacturing"]
    if business_type.lower() in banned:
        return {"legal": False, "reason": "Environmental regulation ban"}
    return {"legal": True}

def estimate_small_business_roi(
    initial_capital: float,
    monthly_cost: float,
    expected_monthly_revenue: float
) -> dict:
    print("--- Tool: estimate_small_business_roi called ---")
    monthly_profit = expected_monthly_revenue - monthly_cost
    if monthly_profit <= 0:
        break_even_months = None
    else:
        break_even_months = initial_capital / monthly_profit
    return {
        "status": "success",
        "initial_capital": initial_capital,
        "monthly_cost": monthly_cost,
        "expected_monthly_revenue": expected_monthly_revenue,
        "monthly_profit": monthly_profit,
        "break_even_months": break_even_months
    }

# ==========================================
# CREATE BUSINESS AGENT
# ==========================================
business_agent = Agent(
    name="business_agent",
    model="gemini-2.0-flash",
    description="An agent that finds profitable real-world businesses based on user budget, location and constraints.",
    instruction=instructions,
    tools=[
        search_business_machines,
        estimate_import_cost,
        validate_population_feasibility,
        check_voltage_compatibility,
        estimate_machine_maintenance,
        estimate_shipping_time,
        check_business_legality,
        estimate_small_business_roi
    ]
)