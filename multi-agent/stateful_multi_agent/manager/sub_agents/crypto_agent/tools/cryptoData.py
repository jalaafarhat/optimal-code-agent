import yfinance as yf


def get_crypto_price(symbol: str) -> dict:
    """
    Get current price for a cryptocurrency.

    Parameters:
    symbol (str): Crypto symbol (e.g., 'BTC', 'ETH', 'SOL') or pair like 'BTC-USD'

    Returns:
    dict: Current price and 24h change
    """
    ticker = symbol.upper()
    if "-" not in ticker:
        ticker = f"{ticker}-USD"

    try:
        crypto = yf.Ticker(ticker)
        info = crypto.info
        history = crypto.history(period="2d")
        current = float(history["Close"].iloc[-1]) if not history.empty else info.get("regularMarketPrice")
        prev = float(history["Close"].iloc[-2]) if len(history) > 1 else current
        change_pct = round(((current - prev) / prev) * 100, 2) if prev else 0

        return {
            "symbol": ticker,
            "name": info.get("shortName") or info.get("longName"),
            "price_usd": round(float(current), 2),
            "change_24h_pct": change_pct,
            "market_cap": info.get("marketCap"),
            "volume_24h": info.get("volume24Hr") or info.get("regularMarketVolume"),
        }
    except Exception as e:
        return {"symbol": ticker, "error": str(e)}


def get_crypto_history(symbol: str, period: str = "1y") -> dict:
    """
    Get historical price data for a cryptocurrency.

    Parameters:
    symbol (str): Crypto symbol (e.g., 'BTC', 'ETH')
    period (str): Time period ('1mo', '3mo', '6mo', '1y', '2y')

    Returns:
    dict: Price history with dates and closes
    """
    ticker = symbol.upper()
    if "-" not in ticker:
        ticker = f"{ticker}-USD"

    try:
        crypto = yf.Ticker(ticker)
        history = crypto.history(period=period)
        if history.empty:
            return {"symbol": ticker, "error": "No data found"}

        close = history["Close"]
        start = float(close.iloc[0])
        end = float(close.iloc[-1])
        return {
            "symbol": ticker,
            "period": period,
            "start_price": round(start, 2),
            "end_price": round(end, 2),
            "return_pct": round(((end - start) / start) * 100, 2),
            "high": round(float(close.max()), 2),
            "low": round(float(close.min()), 2),
            "dates": history.index.strftime("%Y-%m-%d").tolist()[-30:],
            "closes": [round(v, 2) for v in close.tolist()[-30:]],
        }
    except Exception as e:
        return {"symbol": ticker, "error": str(e)}


def compare_cryptos(symbols: list) -> dict:
    """
    Compare performance of multiple cryptocurrencies.

    Parameters:
    symbols (list): List of crypto symbols (e.g., ['BTC', 'ETH', 'SOL'])

    Returns:
    dict: Comparison of prices and 1-year returns
    """
    results = {}
    for sym in symbols:
        price_data = get_crypto_price(sym)
        hist_data = get_crypto_history(sym, "1y")
        results[sym.upper()] = {
            "price_usd": price_data.get("price_usd"),
            "change_24h_pct": price_data.get("change_24h_pct"),
            "return_1y_pct": hist_data.get("return_pct"),
            "error": price_data.get("error") or hist_data.get("error"),
        }
    return results
