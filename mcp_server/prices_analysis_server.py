from mcp.server.fastmcp import FastMCP
import logfire
import yfinance as yf

from config import settings

if settings.logfire_token:
    logfire.configure(token=settings.logfire_token, service_name='server')
    logfire.instrument_mcp()

mcp = FastMCP("Financial Research Server")

@mcp.prompt()
def price_analyst_prompt():
    return (
        "You are a stock price analyst. When given a company name, you should:\n"
        "1. Determine the stock ticker symbol (e.g., 'Nvidia' -> 'NVDA')\n"
        "2. Use get_current_stock_price to fetch the current price\n"
        "3. Use get_historical_stock_prices to analyze recent trends (default 1mo)\n"
        "4. Provide a concise analysis including:\n"
        "   - Current price\n"
        "   - Recent trend (up/down, percentage change)\n"
        "   - Key observations\n"
        "Keep your analysis under 3 paragraphs."
    )

@mcp.tool()
async def get_current_stock_price(symbol: str) -> str:
    """
    Use this function to get the current stock price for a given symbol.

    Args:
        symbol (str): The stock symbol.

    Returns:
        str: The current stock price or error message.
    """
    try:
        stock = yf.Ticker(symbol)
        current_price = stock.info.get("regularMarketPrice", stock.info.get("currentPrice"))
        return f"{current_price:.4f}" if current_price else f"Could not fetch current price for {symbol}"
    except Exception as e:
        return f"Error fetching current price for {symbol}: {e}"

@mcp.tool()
async def get_historical_stock_prices(symbol: str, period: str = "1mo", interval: str = "1d") -> str:
    """
    Use this function to get the historical stock price for a given symbol.

    Args:
        symbol (str): The stock symbol.
        period (str): The period for which to retrieve historical prices. Defaults to "1mo".
                      Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        interval (str): The interval between data points. Defaults to "1d".
                        Valid intervals: 1d,5d,1wk,1mo,3mo

    Returns:
        str: The historical stock price or error message.
    """
    try:
        stock = yf.Ticker(symbol)
        historical_price = stock.history(period=period, interval=interval)
        return historical_price.to_json(orient="index")
    except Exception as e:
        return f"Error fetching historical prices for {symbol}: {e}"

@mcp.tool()
async def get_analyst_recommendations(symbol: str) -> str:
    """
    Use this function to get analyst recommendations for a given stock symbol.

    Args:
        symbol (str): The stock symbol.

    Returns:
        str: JSON containing analyst recommendations or error message.
    """
    try:
        stock = yf.Ticker(symbol)
        recommendations = stock.recommendations
        return recommendations.to_json(orient="index")
    except Exception as e:
        return f"Error fetching analyst recommendations for {symbol}: {e}"
