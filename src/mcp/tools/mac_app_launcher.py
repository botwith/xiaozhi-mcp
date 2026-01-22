# mac_app_launcher.py
from fastmcp import FastMCP
import sys
import logging
import subprocess
import platform
import re
import urllib.parse
from typing import Optional

logger = logging.getLogger('MacAppLauncher')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Check if running on macOS
if platform.system() != 'Darwin':
    logger.warning("This tool is designed for macOS. Some features may not work on other platforms.")

# Create an MCP server
mcp = FastMCP("MacAppLauncher")

# Application mappings (English name -> Chinese name)
# Also includes alternative names that might be used
APP_MAPPINGS = {
    "Google Chrome": "浏览器",
    "Chrome": "浏览器",
    "WeChat": "微信",
    "微信": "微信",
    "Calculator": "计算器",
    "计算器": "计算器",
    "Stock": "同花顺",
    "同花顺": "同花顺",
    "Phone": "电话",
    "电话": "电话",
    "FaceTime": "视频通话",
    "视频通话": "视频通话",
    "Photos": "照片",
    "照片": "照片",
    "相册": "照片"
}

# Alternative app names mapping (for apps that might have different bundle names)
APP_ALTERNATIVES = {
    "浏览器": ["Google Chrome", "Chrome"],
    "微信": ["WeChat", "微信"],
    "计算器": ["Calculator"],
    "同花顺": ["Stock", "同花顺", "10jqka"],
    "电话": ["Phone"],
    "视频通话": ["FaceTime"],
    "照片": ["Photos"],
    "相册": ["Photos"]
}

# Site mappings for Chrome
SITE_MAPPINGS = {
    "Google": "https://www.google.com",
    "GitHub": "https://github.com",
    "OpenAI": "https://chat.openai.com",
    "YouTube": "https://www.youtube.com",
    "百度": "https://www.baidu.com",
    "Baidu": "https://www.baidu.com",
    "知乎": "https://www.zhihu.com",
    "Zhihu": "https://www.zhihu.com",
    "微博": "https://weibo.com",
    "Weibo": "https://weibo.com",
    "淘宝": "https://www.taobao.com",
    "Taobao": "https://www.taobao.com",
    "京东": "https://www.jd.com",
    "JD": "https://www.jd.com",
    "微信": "https://wx.qq.com",
    "WeChat": "https://wx.qq.com",
    "Gmail": "https://mail.google.com",
    "Outlook": "https://outlook.live.com",
    "Twitter": "https://twitter.com",
    "X": "https://x.com",
    "Facebook": "https://www.facebook.com",
    "LinkedIn": "https://www.linkedin.com",
    "Reddit": "https://www.reddit.com",
    "Stack Overflow": "https://stackoverflow.com",
    "Medium": "https://medium.com",
    "Netflix": "https://www.netflix.com",
    "Spotify": "https://open.spotify.com",
    "Apple": "https://www.apple.com",
    "Microsoft": "https://www.microsoft.com",
    "Amazon": "https://www.amazon.com",
    "Wikipedia": "https://www.wikipedia.org",
    "维基百科": "https://www.wikipedia.org",
}

def open_app(app_name: str) -> dict:
    """Open a Mac application by name."""
    if platform.system() != 'Darwin':
        return {
            "success": False,
            "message": "此工具仅在 macOS 系统上可用",
            "error": "Not running on macOS"
        }
    
    # Try to find the correct app name
    app_names_to_try = [app_name]
    
    # If it's a Chinese name, try alternatives
    if app_name in APP_ALTERNATIVES:
        app_names_to_try.extend(APP_ALTERNATIVES[app_name])
    
    # Remove duplicates while preserving order
    app_names_to_try = list(dict.fromkeys(app_names_to_try))
    
    last_error = None
    for name_to_try in app_names_to_try:
        try:
            # Use 'open -a' command to launch the application
            result = subprocess.run(
                ["open", "-a", name_to_try],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully opened application: {name_to_try}")
                display_name = APP_MAPPINGS.get(app_name, app_name)
                if display_name == app_name:
                    display_name = APP_MAPPINGS.get(name_to_try, name_to_try)
                return {
                    "success": True,
                    "message": f"已成功打开 {display_name}",
                    "app_name": name_to_try,
                    "app_name_cn": display_name
                }
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                last_error = error_msg
                logger.debug(f"Failed to open {name_to_try}: {error_msg}, trying next alternative...")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while opening application: {name_to_try}")
            return {
                "success": False,
                "message": f"打开 {APP_MAPPINGS.get(app_name, app_name)} 超时",
                "error": "Timeout"
            }
        except Exception as e:
            last_error = str(e)
            logger.debug(f"Error opening {name_to_try}: {e}, trying next alternative...")
    
    # If all attempts failed
    logger.error(f"Failed to open application {app_name} after trying: {app_names_to_try}")
    return {
        "success": False,
        "message": f"打开 {APP_MAPPINGS.get(app_name, app_name)} 失败: {last_error or '应用程序未找到'}",
        "error": last_error or "Application not found",
        "tried_names": app_names_to_try
    }

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number by removing spaces, dashes, parentheses, and other non-digit characters.
    Keeps + sign for international numbers.
    """
    # Remove common separators but keep + for international numbers
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    return phone

def send_email(to: str, subject: Optional[str] = None, body: Optional[str] = None) -> dict:
    """Open default email client with pre-filled recipient, subject, and body.
    Note: This does NOT actually send the email, it only opens the email client for the user to review and send manually.
    For actually sending emails via SMTP, use the send_email tool from email_tool.py instead.
    """
    if platform.system() != 'Darwin':
        return {
            "success": False,
            "message": "此工具仅在 macOS 系统上可用",
            "error": "Not running on macOS"
        }
    
    try:
        # Extract email address if format is "Display Name <email@example.com>"
        # Otherwise use the input as-is
        email_address = to
        if '<' in to and '>' in to:
            # Extract email from "Display Name <email@example.com>" format
            match = re.search(r'<([^>]+)>', to)
            if match:
                email_address = match.group(1)
        
        # Validate email format (basic check)
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email_address):
            return {
                "success": False,
                "message": f"无效的邮箱地址格式: {to}",
                "error": "Invalid email address format"
            }
        
        # Build mailto URL
        mailto_params = {}
        if subject:
            mailto_params['subject'] = subject
        if body:
            mailto_params['body'] = body
        
        # URL encode the email address and parameters
        encoded_email = urllib.parse.quote(email_address, safe='')
        
        # Construct mailto URL
        if mailto_params:
            query_string = urllib.parse.urlencode(mailto_params, quote_via=urllib.parse.quote)
            mailto_url = f"mailto:{encoded_email}?{query_string}"
        else:
            mailto_url = f"mailto:{encoded_email}"
        
        # Open mailto URL using 'open' command
        result = subprocess.run(
            ["open", mailto_url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully opened email client for: {email_address}")
            return {
                "success": True,
                "message": f"正在打开邮件客户端，收件人: {to}" + (f"，主题: {subject}" if subject else ""),
                "to": to,
                "email_address": email_address,
                "subject": subject,
                "body": body
            }
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            logger.error(f"Failed to open email client for {email_address}: {error_msg}")
            return {
                "success": False,
                "message": f"打开邮件客户端失败: {error_msg}",
                "error": error_msg
            }
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout while opening email client for: {to}")
        return {
            "success": False,
            "message": f"打开邮件客户端超时",
            "error": "Timeout"
        }
    except Exception as e:
        logger.error(f"Error opening email client for {to}: {e}")
        return {
            "success": False,
            "message": f"打开邮件客户端时发生错误: {str(e)}",
            "error": str(e)
        }

def call_phone(phone_number: str) -> dict:
    """Make a phone call to the specified number."""
    if platform.system() != 'Darwin':
        return {
            "success": False,
            "message": "此工具仅在 macOS 系统上可用",
            "error": "Not running on macOS"
        }
    
    try:
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)
        
        # Validate phone number (should contain digits and optionally +)
        if not re.match(r'^\+?[\d]+$', normalized_phone):
            return {
                "success": False,
                "message": f"无效的电话号码格式: {phone_number}",
                "error": "Invalid phone number format"
            }
        
        # Use tel: protocol to make the call
        tel_url = f"tel:{normalized_phone}"
        result = subprocess.run(
            ["open", tel_url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully initiated call to: {normalized_phone}")
            return {
                "success": True,
                "message": f"正在拨打 {phone_number}",
                "phone_number": phone_number,
                "normalized_phone": normalized_phone
            }
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            logger.error(f"Failed to call {normalized_phone}: {error_msg}")
            return {
                "success": False,
                "message": f"拨打 {phone_number} 失败: {error_msg}",
                "error": error_msg
            }
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout while calling: {phone_number}")
        return {
            "success": False,
            "message": f"拨打 {phone_number} 超时",
            "error": "Timeout"
        }
    except Exception as e:
        logger.error(f"Error calling {phone_number}: {e}")
        return {
            "success": False,
            "message": f"拨打 {phone_number} 时发生错误: {str(e)}",
            "error": str(e)
        }

def open_chrome_with_site(site: str) -> dict:
    """Open Google Chrome with a specific site."""
    try:
        # Check if site is a URL or a site name
        url = SITE_MAPPINGS.get(site, site)
        
        # If it's not a URL (doesn't start with http:// or https://), treat it as a site name
        if not url.startswith(("http://", "https://")):
            # If it's not in mappings, try to construct a URL
            if "." in site:
                url = f"https://{site}"
            else:
                return {
                    "success": False,
                    "message": f"未知的网站名称: {site}",
                    "error": f"Unknown site name: {site}",
                    "available_sites": list(SITE_MAPPINGS.keys())
                }
        
        # Open Chrome with the URL
        result = subprocess.run(
            ["open", "-a", "Google Chrome", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully opened Chrome with site: {url}")
            return {
                "success": True,
                "message": f"已成功在浏览器中打开 {site}",
                "site": site,
                "url": url
            }
        else:
            error_msg = result.stderr.strip() or "Unknown error"
            logger.error(f"Failed to open Chrome with site {url}: {error_msg}")
            return {
                "success": False,
                "message": f"在浏览器中打开 {site} 失败: {error_msg}",
                "error": error_msg,
                "url": url
            }
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout while opening Chrome with site: {site}")
        return {
            "success": False,
            "message": f"在浏览器中打开 {site} 超时",
            "error": "Timeout"
        }
    except Exception as e:
        logger.error(f"Error opening Chrome with site {site}: {e}")
        return {
            "success": False,
            "message": f"在浏览器中打开 {site} 时发生错误: {str(e)}",
            "error": str(e)
        }

@mcp.tool()
def open_application(app_name: str) -> dict:
    """Open a Mac application. Supported apps: Google Chrome/Chrome (浏览器), WeChat (微信), Calculator (计算器), Stock (同花顺), Phone (电话), FaceTime (视频通话), Photos (照片/相册).
    
    Args:
        app_name: The name of the application to open. Can be English name (e.g., "Google Chrome", "WeChat", "Calculator", "Photos") or Chinese name (e.g., "浏览器", "微信", "计算器", "照片", "相册").
    
    Returns:
        dict: Result with success status and message.
    """
    return open_app(app_name)

@mcp.tool()
def call_phone_number(phone_number: str) -> dict:
    """Make a phone call to the specified number. The phone number can include spaces, dashes, parentheses, or other common separators.
    
    Examples:
    - "13800138000" (Chinese mobile number)
    - "+86 138 0013 8000" (International format)
    - "(010) 1234-5678" (Landline with area code)
    - "400-123-4567" (Service number)
    
    Args:
        phone_number: The phone number to call. Can include spaces, dashes, parentheses, or other separators.
    
    Returns:
        dict: Result with success status and message.
    """
    return call_phone(phone_number)

@mcp.tool()
def open_email_client(to: str, subject: Optional[str] = None, body: Optional[str] = None) -> dict:
    """打开默认邮件客户端撰写邮件（不直接发送，需要用户手动发送）。与 send_email 工具的区别：此工具只是打开邮件客户端并预填信息，不会实际发送邮件；send_email 工具会通过 SMTP 直接发送邮件。
    
    使用场景：
    - 需要用户确认后再发送
    - 需要添加附件
    - 需要修改邮件内容
    - 使用系统默认邮件客户端
    
    Examples:
    - open_email_client("user@example.com")
    - open_email_client("user@example.com", subject="Hello")
    - open_email_client("user@example.com", subject="Hello", body="This is the email body")
    - open_email_client("张三 <zhangsan@example.com>", subject="会议通知", body="明天下午3点开会")
    
    Args:
        to: 收件人邮箱地址。可以是简单格式（如 "user@example.com"）或带显示名称（如 "张三 <zhangsan@example.com>"）。
        subject: 可选。邮件主题。
        body: 可选。邮件正文内容。
    
    Returns:
        dict: 包含成功状态和消息的结果。
    """
    return send_email(to, subject, body)

@mcp.tool()
def open_chrome(site: Optional[str] = None) -> dict:
    """Open Google Chrome browser. If a site is specified, opens that site in Chrome.
    
    Supported sites: Google, GitHub, OpenAI, YouTube, 百度 (Baidu), 知乎 (Zhihu), 微博 (Weibo), 
    淘宝 (Taobao), 京东 (JD), 微信 (WeChat), Gmail, Outlook, Twitter, X, Facebook, LinkedIn, 
    Reddit, Stack Overflow, Medium, Netflix, Spotify, Apple, Microsoft, Amazon, Wikipedia (维基百科).
    
    You can also provide a custom URL directly (must start with http:// or https://).
    
    Args:
        site: Optional. The site name (e.g., "Google", "GitHub", "OpenAI", "YouTube") or a custom URL.
             If not provided, just opens Chrome without navigating to any site.
    
    Returns:
        dict: Result with success status and message.
    """
    if site:
        return open_chrome_with_site(site)
    else:
        return open_app("Google Chrome")

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
