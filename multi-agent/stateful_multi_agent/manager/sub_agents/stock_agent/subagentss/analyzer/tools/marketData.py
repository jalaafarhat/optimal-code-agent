import yfinance as yf
import time
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import random

class RealPriceFetcher:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        ]
        self.cache = {}
        self.cache_duration = 60
        self.rate_limit_delay = 1.5
        
    def _get_random_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
    
    def _rate_limit(self):
        time.sleep(self.rate_limit_delay)
    
    def _get_cached_price(self, ticker):
        if ticker in self.cache:
            cached_time, price = self.cache[ticker]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_duration):
                return price
        return None
    
    def _cache_price(self, ticker, price):
        self.cache[ticker] = (datetime.now(), price)
    
    def get_current_price(self, ticker):
        """Get real current price for a stock ticker"""
        self._rate_limit()
        
        # Check cache first
        cached_price = self._get_cached_price(ticker)
        if cached_price is not None:
            return cached_price
        
        # Define all price fetching methods
        methods = [
            self._get_from_finance_yahoo_api,
            self._get_from_marketwatch,
            self._get_from_google_finance,
            self._get_from_yahoo_finance_web,
            self._get_from_investing_com,
        ]
        
        all_errors = []
        
        for method in methods:
            try:
                price = method(ticker)
                if price and price > 0:
                    self._cache_price(ticker, price)
                    return price
            except Exception as e:
                error_msg = f"{method.__name__}: {str(e)}"
                all_errors.append(error_msg)
                continue
        
        emergency_price = self._emergency_fetch(ticker)
        if emergency_price:
            self._cache_price(ticker, emergency_price)
            return emergency_price
        
        error_summary = "\n".join(all_errors)
        raise Exception(f"Failed to fetch real price for {ticker}. All methods exhausted:\n{error_summary}")
    
    def _get_from_finance_yahoo_api(self, ticker):
        for attempt in range(3):
            try:
                time.sleep(attempt * 0.5)
                stock = yf.Ticker(ticker)
                
                try:
                    price = stock.fast_info['lastPrice']
                    if price:
                        return float(price)
                except:
                    pass
                
                history = stock.history(period="1d", interval="1m")
                if not history.empty:
                    return float(history['Close'].iloc[-1])
                
                history = stock.history(period="1d")
                if not history.empty:
                    return float(history['Close'].iloc[-1])
                    
            except Exception as e:
                if attempt == 2:
                    raise Exception(f"Yahoo Finance API failed after 3 attempts: {str(e)}")
                continue
        
        raise Exception("Yahoo Finance API: All retries failed")
    
    def _get_from_marketwatch(self, ticker):
        try:
            url = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
            response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            selectors = [
                "bg-quote[field='lastPrice']",
                "h2.intraday__price",
                "span.value",
                "div.region--intraday",
                "td.table__cell.u-semi"
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.text.strip()
                    price_text = price_text.replace('$', '').replace(',', '').replace('€', '').replace('£', '').replace(' ', '')
                    
                    if any(char.isdigit() for char in price_text):
                        import re
                        match = re.search(r'[\d,]+\.?\d*', price_text)
                        if match:
                            return float(match.group().replace(',', ''))
            
            raise Exception("Could not find price element")
            
        except Exception as e:
            raise Exception(f"MarketWatch failed: {str(e)}")
    
    def _get_from_google_finance(self, ticker):
        try:
            exchanges = ['NASDAQ', 'NYSE', 'NSE', 'BSE', 'HKG']
            
            for exchange in exchanges:
                try:
                    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
                    response = requests.get(url, headers=self._get_random_headers(), timeout=8)
                    
                    if "Couldn't find" in response.text:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    price_div = soup.find("div", class_="YMlKec fxKbKc")
                    if not price_div:
                        price_div = soup.find("div", class_="YMlKec")
                    
                    if price_div:
                        price_text = price_div.text.strip()
                        price_text = price_text.replace('$', '').replace(',', '').replace('₹', '').replace('€', '').replace('£', '').replace('HK$', '')
                        
                        if price_text:
                            return float(price_text)
                    
                except:
                    continue
            
            raise Exception("Not found on any exchange")
            
        except Exception as e:
            raise Exception(f"Google Finance failed: {str(e)}")
    
    def _get_from_yahoo_finance_web(self, ticker):
        try:
            url = f"https://finance.yahoo.com/quote/{ticker}"
            response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            price_elements = soup.find_all("fin-streamer", {"data-field": "regularMarketPrice"})
            
            for element in price_elements:
                if 'value' in element.attrs:
                    return float(element['value'])
            
            price_span = soup.find("span", class_="Trsdu(0.3s)")
            if price_span:
                price_text = price_span.text.strip()
                price_text = price_text.replace('$', '').replace(',', '')
                return float(price_text)
            
            raise Exception("Price element not found")
            
        except Exception as e:
            raise Exception(f"Yahoo Finance Web failed: {str(e)}")
    
    def _get_from_investing_com(self, ticker):
        try:
            url = f"https://www.investing.com/equities/{ticker.lower()}-historical-data"
            response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            
            if response.status_code == 404:
                url = f"https://www.investing.com/equities/{ticker}"
                response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            price_span = soup.find("span", {"data-test": "instrument-price-last"})
            if not price_span:
                price_span = soup.find("div", class_="text-5xl")
            
            if price_span:
                price_text = price_span.text.strip()
                price_text = price_text.replace('$', '').replace(',', '')
                return float(price_text)
            
            raise Exception("Price not found")
            
        except Exception as e:
            raise Exception(f"Investing.com failed: {str(e)}")
    
    def _emergency_fetch(self, ticker):
        try:
            url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey=demo"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    return float(data['price'])
        except:
            pass
        
        return None
    
    def get_price_history(self, ticker, period="3y"):
        self._rate_limit()
        
        retries = 3
        for attempt in range(retries):
            try:
                time.sleep(attempt * 1)
                stock = yf.Ticker(ticker)
                history = stock.history(period=period)
                
                if history.empty:
                    raise Exception(f"No historical data found for {ticker}")
                
                result = {
                    "dates": history.index.strftime('%Y-%m-%d').tolist(),
                    "open": history["Open"].tolist(),
                    "high": history["High"].tolist(),
                    "low": history["Low"].tolist(),
                    "close": history["Close"].tolist(),
                    "volume": history["Volume"].tolist()
                }
                return result
                
            except Exception as e:
                if attempt == retries - 1:
                    raise Exception(f"Failed to get price history after {retries} attempts: {str(e)}")
                continue

# Create a singleton instance
_price_fetcher = RealPriceFetcher()

# Standalone functions with simple signatures for automatic function calling
def get_current_price(ticker: str) -> float:
    """
    Get current stock price for a given ticker symbol
    
    Parameters:
    ticker (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA', 'TCEHY')
    
    Returns:
    float: Current price of the stock
    """
    return _price_fetcher.get_current_price(ticker)

def get_price_history(ticker: str, period: str = "3y") -> dict:
    """
    Get historical price data for a stock
    
    Parameters:
    ticker (str): The stock ticker symbol
    period (str): Time period for history (e.g., '1d', '1mo', '1y', '3y')
    
    Returns:
    dict: Dictionary with price history data
    """
    return _price_fetcher.get_price_history(ticker, period)

def get_multiple_prices(tickers: list) -> dict:
    """
    Get current prices for multiple tickers
    
    Parameters:
    tickers (list): List of stock ticker symbols
    
    Returns:
    dict: Dictionary with ticker: price pairs
    """
    results = {}
    for ticker in tickers:
        try:
            price = get_current_price(ticker)
            results[ticker] = price
        except Exception as e:
            results[ticker] = f"Error: {str(e)}"
    return results

# Test function
def test_price_fetch(ticker: str = "AAPL") -> bool:
    """Test the price fetcher with a given ticker"""
    try:
        price = get_current_price(ticker)
        print(f"Success! {ticker} current price: ${price:.2f}")
        return True
    except Exception as e:
        print(f"Test failed for {ticker}: {e}")
        return False

if __name__ == "__main__":
    print("Testing price fetcher...")
    test_price_fetch("AAPL")