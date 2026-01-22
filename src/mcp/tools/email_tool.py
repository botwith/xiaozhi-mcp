# email_tool.py
from fastmcp import FastMCP
import sys
import logging
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import yaml
import json

logger = logging.getLogger('Email')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("Email")

def get_config_value(cfg, *keys, default=None):
    """Get nested config value by keys path. Returns default if not found."""
    value = cfg
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value

def load_config_file(file_path):
    """Load config file (YAML or JSON format). Returns dict or None."""
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f) or {}
            else:
                # Backward compatibility: support JSON files
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config {file_path}: {e}")
        return None

def load_smtp_config():
    """Load SMTP configuration.
    
    Priority:
    1. Environment variables (set by app.py from server config)
    2. mcp_config.yaml -> mcp.servers.local-stdio-email.smtp
    3. Environment variables (direct, backward compatibility)
    
    Returns dict with SMTP configuration.
    """
    # Priority 1: Check environment variables first (set by app.py)
    if os.getenv("SMTP_HOST"):
        return {
            "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "user": os.getenv("SMTP_USER", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USER", "")),
            "from_name": os.getenv("SMTP_FROM_NAME", "MCP Email Tool"),
        }
    
    # Priority 2: Load from config file
    base_dir = os.getcwd()
    default_config_path = os.path.join(base_dir, "mcp_config.yaml")
    cfg = load_config_file(default_config_path) or {}
    
    # Extract SMTP config from server config
    servers = get_config_value(cfg, "mcp", "servers") or {}
    email_server = servers.get("local-stdio-email", {})
    smtp_config = email_server.get("smtp") or {}
    
    # Fallback to old mcp.mail.smtp format (backward compatibility)
    if not smtp_config:
        smtp_config = get_config_value(cfg, "mcp", "mail", "smtp") or {}
    
    # Return with environment variable fallback
    return {
        "host": smtp_config.get("host") or os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(smtp_config.get("port") or os.getenv("SMTP_PORT", "587")),
        "user": smtp_config.get("user") or os.getenv("SMTP_USER", ""),
        "password": smtp_config.get("password") or os.getenv("SMTP_PASSWORD", ""),
        "from_email": smtp_config.get("from_email") or os.getenv("SMTP_FROM_EMAIL", smtp_config.get("user") or os.getenv("SMTP_USER", "")),
        "from_name": smtp_config.get("from_name") or os.getenv("SMTP_FROM_NAME", "MCP Email Tool"),
    }

# Load SMTP configuration
_smtp_config = load_smtp_config()
SMTP_HOST = _smtp_config["host"]
SMTP_PORT = _smtp_config["port"]
SMTP_USER = _smtp_config["user"]
SMTP_PASSWORD = _smtp_config["password"]
SMTP_FROM_EMAIL = _smtp_config["from_email"]
SMTP_FROM_NAME = _smtp_config["from_name"]

def send_email_smtp(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False
) -> dict:
    """Send email using SMTP."""
    try:
        # Check credentials
        if not SMTP_USER or not SMTP_PASSWORD:
            return {
                "success": False,
                "error": "SMTP credentials not configured. Please configure mcp.mail.smtp.user and mcp.mail.smtp.password in mcp_config.yaml or set SMTP_USER and SMTP_PASSWORD environment variables."
            }
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((SMTP_FROM_NAME, SMTP_FROM_EMAIL))
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        if is_html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Connect to SMTP server with timeout
        logger.info(f"Connecting to SMTP server {SMTP_HOST}:{SMTP_PORT}")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        
        try:
            # Enable debug output (level 1 for minimal output)
            server.set_debuglevel(0)
            
            # Start TLS if using port 587
            if SMTP_PORT == 587:
                logger.info("Starting TLS connection")
                server.starttls()
            
            # Login
            logger.info(f"Logging in as {SMTP_USER}")
            server.login(SMTP_USER, SMTP_PASSWORD)
            
            # Send message
            logger.info(f"Sending email to {to_email}")
            server.send_message(msg)
            
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}"
            }
        finally:
            # Always close the connection
            try:
                server.quit()
            except:
                server.close()
        
    except smtplib.SMTPConnectError as e:
        logger.error(f"SMTP connection error: {e}")
        return {
            "success": False,
            "error": f"Failed to connect to SMTP server {SMTP_HOST}:{SMTP_PORT}. Check your SMTP_HOST and SMTP_PORT settings."
        }
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"SMTP server disconnected: {e}")
        return {
            "success": False,
            "error": f"SMTP server connection was closed unexpectedly. This may be due to authentication failure or server timeout. Check your SMTP_USER and SMTP_PASSWORD."
        }
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication error: {e}")
        return {
            "success": False,
            "error": f"SMTP authentication failed. Please check your SMTP_USER and SMTP_PASSWORD. For Gmail, you may need to use an App Password instead of your regular password."
        }
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"SMTP recipient refused: {e}")
        return {
            "success": False,
            "error": f"Recipient email address '{to_email}' was refused by the server: {str(e)}"
        }
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return {
            "success": False,
            "error": f"SMTP error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to send email: {str(e)}"
        }

# Add send email tool
@mcp.tool()
def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False
) -> dict:
    """给单一收件人发送邮件。
    
    Args:
        to_email: 收件人的邮箱地址
        subject: 邮件主题
        body: 邮件正文内容
        is_html: 是否为 HTML 格式邮件（默认 False，即纯文本）
    """
    to_email = to_email.strip()
    
    if not to_email:
        return {
            "success": False,
            "error": "收件人邮箱地址不能为空",
            "timestamp": datetime.now().isoformat()
        }
    
    if not subject:
        return {
            "success": False,
            "error": "邮件主题不能为空",
            "timestamp": datetime.now().isoformat()
        }
    
    if not body:
        return {
            "success": False,
            "error": "邮件正文不能为空",
            "timestamp": datetime.now().isoformat()
        }
    
    logger.info(f"Sending email to {to_email}, subject: {subject}")
    
    # Send email
    result = send_email_smtp(to_email, subject, body, is_html)
    
    if result.get("success"):
        response = {
            "success": True,
            "to": to_email,
            "subject": subject,
            "timestamp": datetime.now().isoformat()
        }
        response.update(result)
        return response
    else:
        return {
            "success": False,
            "to": to_email,
            "error": result.get("error", "Unknown error"),
            "timestamp": datetime.now().isoformat()
        }

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
