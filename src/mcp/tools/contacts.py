# contacts.py
from fastmcp import FastMCP
import sys
import logging
import json  # Still needed for extra_fields JSON serialization
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import uuid

logger = logging.getLogger('Contacts')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("Contacts")

# Data file paths
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DB_FILE = DATA_DIR / "contacts.db"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_db_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    """Initialize SQLite database with required tables."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Main contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                github_id TEXT,
                x_id TEXT,
                birthday TEXT,
                notes TEXT,
                extra_fields TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Contact phones table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_phones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id TEXT NOT NULL,
                value TEXT NOT NULL,
                label TEXT DEFAULT '个人',
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)
        
        # Contact emails table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id TEXT NOT NULL,
                value TEXT NOT NULL,
                label TEXT DEFAULT '个人',
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)
        
        # Contact wechat IDs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_wechat_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id TEXT NOT NULL,
                value TEXT NOT NULL,
                label TEXT DEFAULT '个人',
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_birthday ON contacts(birthday)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phones_contact ON contact_phones(contact_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_contact ON contact_emails(contact_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_value ON contact_emails(value)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wechat_contact ON contact_wechat_ids(contact_id)")
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def contact_row_to_dict(row: sqlite3.Row, conn: sqlite3.Connection) -> Dict[str, Any]:
    """Convert a database row to a contact dictionary."""
    try:
        contact_id = row["id"]
        cursor = conn.cursor()
        
        # Get phones
        phones = []
        try:
            cursor.execute("SELECT value, label FROM contact_phones WHERE contact_id = ?", (contact_id,))
            for r in cursor.fetchall():
                phones.append({"value": r["value"], "label": r["label"]})
        except Exception as e:
            logger.warning(f"Error fetching phones for contact {contact_id}: {e}")
        
        # Get emails
        emails = []
        try:
            cursor.execute("SELECT value, label FROM contact_emails WHERE contact_id = ?", (contact_id,))
            for r in cursor.fetchall():
                emails.append({"value": r["value"], "label": r["label"]})
        except Exception as e:
            logger.warning(f"Error fetching emails for contact {contact_id}: {e}")
        
        # Get wechat IDs
        wechat_ids = []
        try:
            cursor.execute("SELECT value, label FROM contact_wechat_ids WHERE contact_id = ?", (contact_id,))
            for r in cursor.fetchall():
                wechat_ids.append({"value": r["value"], "label": r["label"]})
        except Exception as e:
            logger.warning(f"Error fetching wechat_ids for contact {contact_id}: {e}")
        
        # Parse extra_fields JSON
        extra_fields = {}
        extra_fields_str = row["extra_fields"]
        if extra_fields_str:
            try:
                extra_fields = json.loads(extra_fields_str)
            except Exception as e:
                logger.warning(f"Error parsing extra_fields for contact {contact_id}: {e}")
                extra_fields = {}
        
        return {
            "id": contact_id,
            "name": row["name"],
            "phones": phones,
            "emails": emails,
            "wechat_ids": wechat_ids,
            "github_id": row["github_id"],
            "x_id": row["x_id"],
            "birthday": row["birthday"],
            "notes": row["notes"],
            "extra_fields": extra_fields,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    except Exception as e:
        logger.error(f"Error converting contact row to dict: {e}")
        raise

def normalize_contact_data(contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and validate contact data."""
    normalized = {}
    
    # ID (generate if not provided)
    normalized["id"] = contact_data.get("id") or str(uuid.uuid4())
    
    # Name (required)
    name = contact_data.get("name")
    if not name:
        raise ValueError("姓名不能为空")
    name = str(name).strip()
    if not name:
        raise ValueError("姓名不能为空")
    normalized["name"] = name
    
    # Phones (list of {value, label})
    phones = contact_data.get("phones", [])
    if isinstance(phones, list):
        normalized["phones"] = []
        for p in phones:
            if p and isinstance(p, dict):
                value = p.get("value")
                if value:
                    value_str = str(value).strip()
                    if value_str:
                        label = p.get("label") or "个人"
                        normalized["phones"].append({
                            "value": value_str,
                            "label": str(label).strip() if label else "个人"
                        })
    else:
        normalized["phones"] = []
    
    # Emails (list of {value, label})
    emails = contact_data.get("emails", [])
    if isinstance(emails, list):
        normalized["emails"] = []
        for e in emails:
            if e and isinstance(e, dict):
                value = e.get("value")
                if value:
                    value_str = str(value).strip()
                    if value_str:
                        label = e.get("label") or "个人"
                        normalized["emails"].append({
                            "value": value_str,
                            "label": str(label).strip() if label else "个人"
                        })
    else:
        normalized["emails"] = []
    
    # Wechat IDs (list of {value, label})
    wechat_ids = contact_data.get("wechat_ids", [])
    if isinstance(wechat_ids, list):
        normalized["wechat_ids"] = []
        for w in wechat_ids:
            if w and isinstance(w, dict):
                value = w.get("value")
                if value:
                    value_str = str(value).strip()
                    if value_str:
                        label = w.get("label") or "个人"
                        normalized["wechat_ids"].append({
                            "value": value_str,
                            "label": str(label).strip() if label else "个人"
                        })
    else:
        normalized["wechat_ids"] = []
    
    # GitHub ID (optional)
    github_id = contact_data.get("github_id")
    normalized["github_id"] = str(github_id).strip() if github_id else None
    
    # X ID (optional)
    x_id = contact_data.get("x_id")
    normalized["x_id"] = str(x_id).strip() if x_id else None
    
    # Birthday (optional, format: YYYY-MM-DD)
    birthday = contact_data.get("birthday")
    normalized["birthday"] = str(birthday).strip() if birthday else None
    
    # Notes (optional)
    notes = contact_data.get("notes")
    normalized["notes"] = str(notes).strip() if notes else None
    
    # Extra fields (for extensibility)
    extra_fields = contact_data.get("extra_fields", {})
    if isinstance(extra_fields, dict):
        normalized["extra_fields"] = {k: v for k, v in extra_fields.items() if v}
    else:
        normalized["extra_fields"] = {}
    
    # Created and updated timestamps
    normalized["created_at"] = contact_data.get("created_at") or datetime.now().isoformat()
    normalized["updated_at"] = datetime.now().isoformat()
    
    return normalized

def save_contact_to_db(contact: Dict[str, Any]) -> bool:
    """Save a contact to SQLite database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Insert or update main contact record
        cursor.execute("""
            INSERT OR REPLACE INTO contacts (id, name, github_id, x_id, birthday, notes, extra_fields, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contact["id"],
            contact["name"],
            contact["github_id"],
            contact["x_id"],
            contact["birthday"],
            contact["notes"],
            json.dumps(contact["extra_fields"], ensure_ascii=False) if contact["extra_fields"] else None,
            contact["created_at"],
            contact["updated_at"]
        ))
        
        contact_id = contact["id"]
        
        # Delete existing related records
        cursor.execute("DELETE FROM contact_phones WHERE contact_id = ?", (contact_id,))
        cursor.execute("DELETE FROM contact_emails WHERE contact_id = ?", (contact_id,))
        cursor.execute("DELETE FROM contact_wechat_ids WHERE contact_id = ?", (contact_id,))
        
        # Insert phones
        for phone in contact.get("phones", []):
            cursor.execute("""
                INSERT INTO contact_phones (contact_id, value, label)
                VALUES (?, ?, ?)
            """, (contact_id, phone["value"], phone["label"]))
        
        # Insert emails
        for email in contact.get("emails", []):
            cursor.execute("""
                INSERT INTO contact_emails (contact_id, value, label)
                VALUES (?, ?, ?)
            """, (contact_id, email["value"], email["label"]))
        
        # Insert wechat IDs
        for wechat_id in contact.get("wechat_ids", []):
            cursor.execute("""
                INSERT INTO contact_wechat_ids (contact_id, value, label)
                VALUES (?, ?, ?)
            """, (contact_id, wechat_id["value"], wechat_id["label"]))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving contact to database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_contacts_from_db() -> List[Dict[str, Any]]:
    """Get all contacts from database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts ORDER BY name")
        rows = cursor.fetchall()
        
        contacts = []
        for row in rows:
            try:
                contacts.append(contact_row_to_dict(row, conn))
            except Exception as e:
                logger.error(f"Error processing contact row: {e}")
                continue
        
        return contacts
    except Exception as e:
        logger.error(f"Error getting all contacts from database: {e}")
        raise
    finally:
        conn.close()

def get_contact_by_id_from_db(contact_id: str) -> Optional[Dict[str, Any]]:
    """Get a contact by ID from database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        
        if row:
            return contact_row_to_dict(row, conn)
        return None
    except Exception as e:
        logger.error(f"Error getting contact by ID {contact_id}: {e}")
        raise
    finally:
        conn.close()

def get_contact_by_name_from_db(name: str) -> Optional[Dict[str, Any]]:
    """Get a contact by name from database (case-insensitive)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE LOWER(name) = LOWER(?)", (name.strip(),))
        row = cursor.fetchone()
        
        if row:
            return contact_row_to_dict(row, conn)
        return None
    except Exception as e:
        logger.error(f"Error getting contact by name {name}: {e}")
        raise
    finally:
        conn.close()

def delete_contact_from_db(contact_id: str) -> bool:
    """Delete a contact from database (CASCADE will delete related records)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting contact from database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Initialize database on module load
init_database()

@mcp.tool()
def get_all_contacts() -> dict:
    """获取所有联系人列表。
    
    Returns:
        dict: 包含所有联系人的列表，每个联系人包含以下字段：
            - id: 联系人唯一标识
            - name: 姓名（必填）
            - phones: 电话列表，每个包含 value 和 label（场景备注，如"个人"、"办公"）
            - emails: 邮箱列表，每个包含 value 和 label（场景备注，如"个人"、"办公"）
            - wechat_ids: 微信ID列表，每个包含 value 和 label（场景备注，如"个人"、"办公"）
            - github_id: GitHub用户名（可选）
            - x_id: X（Twitter）用户名（可选）
            - birthday: 生日，格式 YYYY-MM-DD（可选）
            - notes: 备注（可选）
            - extra_fields: 扩展字段（可选）
    """
    try:
        contacts = get_all_contacts_from_db()
        logger.info(f"Retrieved {len(contacts)} contacts")
        return {
            "success": True,
            "count": len(contacts),
            "contacts": contacts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def get_contact_by_id(contact_id: str) -> dict:
    """根据联系人ID获取联系人信息。
    
    Args:
        contact_id: 联系人的唯一标识ID
    
    Returns:
        dict: 联系人信息，如果未找到则返回错误信息
    """
    try:
        contact = get_contact_by_id_from_db(contact_id)
        
        if contact:
            logger.info(f"Found contact: {contact.get('name')} (ID: {contact_id})")
            return {
                "success": True,
                "contact": contact,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.warning(f"Contact not found: {contact_id}")
            return {
                "success": False,
                "error": f"未找到ID为 {contact_id} 的联系人",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting contact: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def get_contact_by_name(name: str) -> dict:
    """根据姓名获取联系人信息。
    
    Args:
        name: 联系人的姓名
    
    Returns:
        dict: 联系人信息，如果未找到则返回错误信息
    """
    try:
        contact = get_contact_by_name_from_db(name)
        
        if contact:
            logger.info(f"Found contact: {name}")
            return {
                "success": True,
                "contact": contact,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.warning(f"Contact not found: {name}")
            return {
                "success": False,
                "error": f"未找到姓名为 {name} 的联系人",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting contact: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def edit_contact(
    name: str,
    contact_id: Optional[str] = None,
    phones: Optional[List[Dict[str, str]]] = None,
    emails: Optional[List[Dict[str, str]]] = None,
    wechat_ids: Optional[List[Dict[str, str]]] = None,
    github_id: Optional[str] = None,
    x_id: Optional[str] = None,
    birthday: Optional[str] = None,
    notes: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> dict:
    """创建或编辑联系人。如果提供了 contact_id 且该联系人存在，则更新；否则创建新联系人。
    
    Args:
        name: 姓名（必填）
        contact_id: 联系人ID（可选，如果提供且存在则更新，否则创建新联系人）
        phones: 电话列表，格式：[{"value": "13800138000", "label": "个人"}, ...]（可选）
        emails: 邮箱列表，格式：[{"value": "user@example.com", "label": "办公"}, ...]（可选）
        wechat_ids: 微信ID列表，格式：[{"value": "wechat123", "label": "个人"}, ...]（可选）
        github_id: GitHub用户名（可选）
        x_id: X（Twitter）用户名（可选）
        birthday: 生日，格式 YYYY-MM-DD（可选）
        notes: 备注（可选）
        extra_fields: 扩展字段字典（可选）
    
    Returns:
        dict: 操作结果，包含成功状态和联系人信息
    """
    try:
        # If contact_id is provided, try to find existing contact
        existing_contact = None
        is_update = False
        if contact_id:
            existing_contact = get_contact_by_id_from_db(contact_id)
            if existing_contact:
                is_update = True
                logger.info(f"Updating contact: {name} (ID: {contact_id})")
            else:
                # Contact ID provided but not found, create new with this ID
                logger.info(f"Contact ID {contact_id} not found, creating new contact: {name}")
        
        # Prepare contact data
        # For updates: if field is None, keep original value; if provided (even empty list), use new value
        # For creates: if field is None, use default value
        if is_update and existing_contact:
            contact_data = {
                "id": contact_id,
                "name": name,  # name is always required and updated
                "phones": phones if phones is not None else existing_contact.get("phones", []),
                "emails": emails if emails is not None else existing_contact.get("emails", []),
                "wechat_ids": wechat_ids if wechat_ids is not None else existing_contact.get("wechat_ids", []),
                "github_id": github_id if github_id is not None else existing_contact.get("github_id"),
                "x_id": x_id if x_id is not None else existing_contact.get("x_id"),
                "birthday": birthday if birthday is not None else existing_contact.get("birthday"),
                "notes": notes if notes is not None else existing_contact.get("notes"),
                "extra_fields": extra_fields if extra_fields is not None else existing_contact.get("extra_fields", {}),
                "created_at": existing_contact.get("created_at")
            }
        else:
            # Creating new contact
            contact_data = {
                "name": name,
                "phones": phones if phones is not None else [],
                "emails": emails if emails is not None else [],
                "wechat_ids": wechat_ids if wechat_ids is not None else [],
                "github_id": github_id,
                "x_id": x_id,
                "birthday": birthday,
                "notes": notes,
                "extra_fields": extra_fields if extra_fields is not None else {}
            }
            if contact_id:
                contact_data["id"] = contact_id
        
        # Normalize and validate contact data
        normalized_contact = normalize_contact_data(contact_data)
        
        # Save to database
        if save_contact_to_db(normalized_contact):
            logger.info(f"Successfully saved contact: {name} (ID: {normalized_contact['id']})")
            return {
                "success": True,
                "message": f"成功保存联系人: {name}",
                "contact": normalized_contact,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "保存联系人失败",
                "timestamp": datetime.now().isoformat()
            }
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error editing contact: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def delete_contact(contact_id: Optional[str] = None, name: Optional[str] = None) -> dict:
    """删除指定联系人。可以通过 contact_id 或 name 来指定要删除的联系人。
    
    Args:
        contact_id: 联系人的唯一标识ID（可选，如果提供则优先使用）
        name: 联系人的姓名（可选，如果 contact_id 未提供则使用此参数）
    
    Returns:
        dict: 操作结果，包含成功状态和消息
    """
    try:
        if not contact_id and not name:
            return {
                "success": False,
                "error": "必须提供 contact_id 或 name 参数",
                "timestamp": datetime.now().isoformat()
            }
        
        # Find contact to delete
        contact_to_delete = None
        if contact_id:
            contact_to_delete = get_contact_by_id_from_db(contact_id)
        elif name:
            contact_to_delete = get_contact_by_name_from_db(name)
        
        if not contact_to_delete:
            identifier = contact_id or name
            logger.warning(f"Contact not found for deletion: {identifier}")
            return {
                "success": False,
                "error": f"未找到要删除的联系人: {identifier}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Delete contact
        deleted_name = contact_to_delete.get("name", "Unknown")
        deleted_id = contact_to_delete.get("id")
        
        if delete_contact_from_db(deleted_id):
            logger.info(f"Successfully deleted contact: {deleted_name} (ID: {deleted_id})")
            return {
                "success": True,
                "message": f"成功删除联系人: {deleted_name}",
                "deleted_contact": contact_to_delete,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "删除联系人失败",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def get_birthday_contacts(today: Optional[str] = None) -> dict:
    """获取今天过生日的联系人列表。
    
    Args:
        today: 日期字符串，格式 YYYY-MM-DD（可选，默认为今天）
    
    Returns:
        dict: 今天过生日的联系人列表
    """
    try:
        if today:
            target_date = datetime.strptime(today, "%Y-%m-%d").date()
        else:
            target_date = datetime.now().date()
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Query contacts with birthday matching month and day
            cursor.execute("""
                SELECT * FROM contacts 
                WHERE birthday IS NOT NULL 
                AND strftime('%m-%d', birthday) = ?
            """, (target_date.strftime("%m-%d"),))
            
            rows = cursor.fetchall()
            birthday_contacts = []
            for row in rows:
                birthday_contacts.append(contact_row_to_dict(row, conn))
            
            logger.info(f"Found {len(birthday_contacts)} contacts with birthday today")
            return {
                "success": True,
                "count": len(birthday_contacts),
                "contacts": birthday_contacts,
                "date": target_date.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error getting birthday contacts: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
