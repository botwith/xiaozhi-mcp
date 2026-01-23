# stock.py
from fastmcp import FastMCP
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, List
import time

# Defer yfinance import to avoid slow startup (lazy import)
_yfinance = None

def get_yfinance():
    """Lazy import yfinance to speed up server initialization."""
    global _yfinance
    if _yfinance is None:
        import yfinance as _yfinance
    return _yfinance

logger = logging.getLogger('Stock')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("Stock")

# Cache for stock data to avoid excessive API calls
stock_cache = {}
CACHE_DURATION = 60  # Cache duration in seconds

def get_cached_stock(symbol: str) -> Optional[Dict]:
    """Get stock data from cache if available and not expired."""
    if symbol in stock_cache:
        cached_data, timestamp = stock_cache[symbol]
        if time.time() - timestamp < CACHE_DURATION:
            logger.info(f"Using cached data for {symbol}")
            return cached_data
    return None

def set_cached_stock(symbol: str, data: Dict):
    """Store stock data in cache."""
    stock_cache[symbol] = (data, time.time())

def get_realtime_stock(symbol: str) -> Optional[Dict]:
    """Get real-time stock price information using yfinance."""
    try:
        symbol = symbol.upper().strip()
        
        # Check cache first
        cached_data = get_cached_stock(symbol)
        if cached_data:
            return cached_data
        
        logger.info(f"Fetching real-time data for {symbol}")

        yf = get_yfinance()
        # Fetch stock data using yfinance
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price and history
        hist = ticker.history(period="1d")
        
        if hist.empty:
            logger.warning(f"No data found for symbol: {symbol}")
            return None
        
        current_price = hist['Close'].iloc[-1]
        previous_close = info.get('previousClose', current_price)
        
        # Calculate change
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close != 0 else 0
        
        # Format market cap
        market_cap = info.get('marketCap', 0)
        market_cap_str = format_market_cap(market_cap)
        
        # Get additional info
        stock_data = {
            "symbol": symbol,
            "name": info.get('longName', info.get('shortName', symbol)),
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "currency": info.get('currency', 'USD'),
            "market_cap": market_cap_str,
            "volume": info.get('volume', 0),
            "day_high": info.get('dayHigh', current_price),
            "day_low": info.get('dayLow', current_price),
            "52_week_high": info.get('fiftyTwoWeekHigh', 0),
            "52_week_low": info.get('fiftyTwoWeekLow', 0),
            "open": info.get('open', current_price),
            "previous_close": previous_close,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the result
        set_cached_stock(symbol, stock_data)
        
        return stock_data
        
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        return None

def format_market_cap(market_cap: float) -> str:
    """Format market cap into human-readable string."""
    if market_cap >= 1e12:
        return f"${market_cap / 1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap / 1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap / 1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

# Add stock query tool
@mcp.tool()
def query_stock(symbol: str) -> dict:
    """查询股票信息。输入股票代码（如 AAPL, GOOGL, MSFT, 0700.HK, 600519.SS 等），返回实时价格、涨跌幅、市值、成交量等信息。
    
    Args:
        symbol: 股票代码，例如 'AAPL', 'GOOGL', 'MSFT' (美股) 或 '0700.HK', '9988.HK' (港股) 或 '600519.SS', '000858.SZ' (A股)
    """
    symbol = symbol.strip()
    
    if not symbol:
        return {
            "success": False,
            "error": "股票代码不能为空",
            "timestamp": datetime.now().isoformat()
        }
    
    stock_info = get_realtime_stock(symbol)
    
    if stock_info:
        logger.info(f"Query stock: {symbol}, price: {stock_info['price']}")
        return {
            "success": True,
            "data": stock_info,
            "timestamp": datetime.now().isoformat()
        }
    else:
        logger.warning(f"Stock not found or error: {symbol}")
        return {
            "success": False,
            "error": f"无法获取股票 '{symbol}' 的数据。请检查股票代码是否正确，或稍后重试。",
            "hint": "支持美股（如 AAPL, GOOGL, MSFT）、港股（如 0700.HK, 9988.HK）和A股（如 600519.SS, 000858.SZ）",
            "timestamp": datetime.now().isoformat()
        }

# Add batch stock query tool
@mcp.tool()
def query_multiple_stocks(symbols: str) -> dict:
    """批量查询多个股票信息。输入多个股票代码，用逗号分隔（如 'AAPL,GOOGL,MSFT,0700.HK,600519.SS'）。
    
    Args:
        symbols: 多个股票代码，用逗号分隔，例如 'AAPL,GOOGL,MSFT' 或 '0700.HK,9988.HK' 或 '600519.SS,000858.SZ'
    """
    if not symbols or not symbols.strip():
        return {
            "success": False,
            "error": "股票代码不能为空",
            "timestamp": datetime.now().isoformat()
        }
    
    symbol_list = [s.strip() for s in symbols.split(",")]
    results = []
    success_count = 0
    
    for symbol in symbol_list:
        stock_info = get_realtime_stock(symbol)
        if stock_info:
            results.append(stock_info)
            success_count += 1
        else:
            results.append({
                "symbol": symbol.upper(),
                "error": "无法获取该股票数据"
            })
    
    logger.info(f"Query multiple stocks: {symbols}, found {success_count}/{len(symbol_list)} stocks")
    
    return {
        "success": True,
        "count": len(results),
        "success_count": success_count,
        "data": results,
        "timestamp": datetime.now().isoformat()
    }

# Popular stocks list for search functionality
POPULAR_STOCKS = [
    # US Stocks
    {"symbol": "AAPL", "name": "Apple Inc.", "market": "US"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "market": "US"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "market": "US"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "market": "US"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "market": "US"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "market": "US"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "market": "US"},
    {"symbol": "BABA", "name": "Alibaba Group", "market": "US"},
    {"symbol": "TSM", "name": "Taiwan Semiconductor", "market": "US"},
    {"symbol": "NFLX", "name": "Netflix, Inc.", "market": "US"},
    {"symbol": "AMD", "name": "Advanced Micro Devices", "market": "US"},
    {"symbol": "INTC", "name": "Intel Corporation", "market": "US"},
    # Hong Kong Stocks
    {"symbol": "0700.HK", "name": "Tencent Holdings", "market": "HK"},
    {"symbol": "9988.HK", "name": "Alibaba Group", "market": "HK"},
    {"symbol": "0941.HK", "name": "China Mobile", "market": "HK"},
    {"symbol": "1299.HK", "name": "AIA Group", "market": "HK"},
    {"symbol": "0960.HK", "name": "Longfor Group", "market": "HK"},
    {"symbol": "0988.HK", "name": "Alibaba Health", "market": "HK"},
    {"symbol": "1024.HK", "name": "Kuaishou Technology", "market": "HK"},
    {"symbol": "1810.HK", "name": "Xiaomi Corporation", "market": "HK"},
    {"symbol": "2318.HK", "name": "Ping An Insurance", "market": "HK"},
    {"symbol": "0968.HK", "name": "Xinyi Solar", "market": "HK"},
    # A-Shares (Shanghai Stock Exchange - .SS)
    {"symbol": "600519.SS", "name": "Kweichow Moutai", "market": "A-Share"},
    {"symbol": "601318.SS", "name": "Ping An Insurance", "market": "A-Share"},
    {"symbol": "600036.SS", "name": "China Merchants Bank", "market": "A-Share"},
    {"symbol": "601888.SS", "name": "China Tourism Group Duty Free", "market": "A-Share"},
    {"symbol": "600276.SS", "name": "Hengrui Medicine", "market": "A-Share"},
    {"symbol": "601012.SS", "name": "Longji Green Energy", "market": "A-Share"},
    {"symbol": "601390.SS", "name": "China State Construction", "market": "A-Share"},
    {"symbol": "600887.SS", "name": "Inner Mongolia Yili", "market": "A-Share"},
    {"symbol": "601668.SS", "name": "China Architecture", "market": "A-Share"},
    {"symbol": "600030.SS", "name": "CITIC Securities", "market": "A-Share"},
    # A-Shares (Shenzhen Stock Exchange - .SZ)
    {"symbol": "000858.SZ", "name": "Wuliangye Yibin", "market": "A-Share"},
    {"symbol": "002594.SZ", "name": "BYD Company", "market": "A-Share"},
    {"symbol": "300750.SZ", "name": "Contemporary Amperex Technology", "market": "A-Share"},
    {"symbol": "000333.SZ", "name": "Midea Group", "market": "A-Share"},
    {"symbol": "002415.SZ", "name": "Hikvision Digital Technology", "market": "A-Share"},
    {"symbol": "300059.SZ", "name": "East Money Information", "market": "A-Share"},
    {"symbol": "000651.SZ", "name": "Gree Electric", "market": "A-Share"},
    {"symbol": "002475.SZ", "name": "Luxshare Precision", "market": "A-Share"},
    {"symbol": "300274.SZ", "name": "Sunshine Laser", "market": "A-Share"},
    {"symbol": "002371.SZ", "name": "North Creation", "market": "A-Share"},
]

# Add stock list tool with popular stocks
@mcp.tool()
def list_popular_stocks() -> dict:
    """列出热门股票代码列表，包括美股、港股和A股。"""
    logger.info(f"List popular stocks: {len(POPULAR_STOCKS)} stocks")
    
    return {
        "success": True,
        "count": len(POPULAR_STOCKS),
        "stocks": POPULAR_STOCKS,
        "timestamp": datetime.now().isoformat()
    }

# Add stock search tool
@mcp.tool()
def search_stock(keyword: str) -> dict:
    """根据关键词搜索股票。支持股票代码或公司名称搜索。
    
    Args:
        keyword: 搜索关键词，可以是股票代码或公司名称，例如 'Apple', '腾讯', 'Tencent', '茅台'
    """
    keyword = keyword.strip().lower()
    
    if not keyword:
        return {
            "success": False,
            "error": "搜索关键词不能为空",
            "timestamp": datetime.now().isoformat()
        }
    
    # Try to get stock data directly if it looks like a symbol
    if len(keyword) <= 6 and not ' ' in keyword:
        stock_info = get_realtime_stock(keyword)
        if stock_info:
            logger.info(f"Direct stock match: {keyword}")
            return {
                "success": True,
                "count": 1,
                "data": [stock_info],
                "timestamp": datetime.now().isoformat()
            }
    
    # Search in popular stocks list
    results = []
    
    for stock in POPULAR_STOCKS:
        if keyword in stock["symbol"].lower() or keyword in stock["name"].lower():
            stock_info = get_realtime_stock(stock["symbol"])
            if stock_info:
                results.append(stock_info)
    
    logger.info(f"Search stock: {keyword}, found {len(results)} results")
    
    if results:
        return {
            "success": True,
            "count": len(results),
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "success": False,
            "error": f"未找到与 '{keyword}' 相关的股票",
            "hint": "请尝试使用股票代码（如 AAPL, 0700.HK, 600519.SS）或完整公司名称",
            "timestamp": datetime.now().isoformat()
        }

# Add stock history tool
@mcp.tool()
def get_stock_history(symbol: str, period: str = "1mo") -> dict:
    """获取股票历史数据。支持不同时间周期。
    
    Args:
        symbol: 股票代码，例如 'AAPL', '0700.HK', '600519.SS', '000858.SZ'
        period: 时间周期，可选值: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'，默认 '1mo'
    """
    symbol = symbol.strip()
    
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
    if period not in valid_periods:
        return {
            "success": False,
            "error": f"无效的时间周期 '{period}'，可选值: {', '.join(valid_periods)}",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        logger.info(f"Fetching stock history for {symbol}, period: {period}")
        yf = get_yfinance()
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {
                "success": False,
                "error": f"无法获取股票 '{symbol}' 的历史数据",
                "timestamp": datetime.now().isoformat()
            }
        
        # Format history data
        history_data = []
        for index, row in hist.iterrows():
            history_data.append({
                "date": index.strftime("%Y-%m-%d"),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        # Calculate statistics
        latest = history_data[-1]
        earliest = history_data[0]
        total_change = ((latest['close'] - earliest['close']) / earliest['close'] * 100) if earliest['close'] != 0 else 0
        
        logger.info(f"Stock history retrieved: {symbol}, {len(history_data)} data points")
        
        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "data_points": len(history_data),
            "total_change_percent": round(total_change, 2),
            "data": history_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching stock history for {symbol}: {str(e)}")
        return {
            "success": False,
            "error": f"获取历史数据时出错: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
