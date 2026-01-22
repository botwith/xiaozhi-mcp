# todo.py
from fastmcp import FastMCP
import sys
import logging
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import uuid

logger = logging.getLogger('Todo')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("Todo")

# Data file paths
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DB_FILE = DATA_DIR / "todos.db"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_db_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def init_database():
    """Initialize SQLite database with required tables."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Main todos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at)")
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def todo_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a database row to a todo dictionary."""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }

def normalize_todo_data(todo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and validate todo data."""
    normalized = {}
    
    # ID (generate if not provided)
    normalized["id"] = todo_data.get("id") or str(uuid.uuid4())
    
    # Title (required)
    title = todo_data.get("title")
    if not title:
        raise ValueError("标题不能为空")
    title = str(title).strip()
    if not title:
        raise ValueError("标题不能为空")
    normalized["title"] = title
    
    # Description (optional)
    description = todo_data.get("description")
    normalized["description"] = str(description).strip() if description else None
    
    # Completed status (default False)
    completed = todo_data.get("completed", False)
    normalized["completed"] = 1 if completed else 0
    
    # Created and updated timestamps
    normalized["created_at"] = todo_data.get("created_at") or datetime.now().isoformat()
    normalized["updated_at"] = datetime.now().isoformat()
    
    return normalized

def save_todo_to_db(todo: Dict[str, Any]) -> bool:
    """Save a todo to SQLite database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Insert or update todo record
        cursor.execute("""
            INSERT OR REPLACE INTO todos (id, title, description, completed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            todo["id"],
            todo["title"],
            todo["description"],
            todo["completed"],
            todo["created_at"],
            todo["updated_at"]
        ))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving todo to database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_todos_from_db() -> List[Dict[str, Any]]:
    """Get all todos from database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        todos = []
        for row in rows:
            todos.append(todo_row_to_dict(row))
        
        return todos
    finally:
        conn.close()

def get_todo_by_id_from_db(todo_id: str) -> Optional[Dict[str, Any]]:
    """Get a todo by ID from database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        
        if row:
            return todo_row_to_dict(row)
        return None
    finally:
        conn.close()

def delete_todo_from_db(todo_id: str) -> bool:
    """Delete a todo from database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting todo from database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Initialize database on module load
init_database()

@mcp.tool()
def get_all_todos() -> dict:
    """获取所有待办事项列表。
    
    Returns:
        dict: 包含所有待办事项的列表，每个待办事项包含以下字段：
            - id: 待办事项唯一标识
            - title: 标题（必填）
            - description: 描述（可选）
            - completed: 是否完成（布尔值）
            - created_at: 创建时间
            - updated_at: 更新时间
    """
    try:
        todos = get_all_todos_from_db()
        logger.info(f"Retrieved {len(todos)} todos")
        return {
            "success": True,
            "count": len(todos),
            "todos": todos,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting todos: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def create_todo(
    title: str,
    description: Optional[str] = None
) -> dict:
    """创建新的待办事项。
    
    Args:
        title: 待办事项标题（必填）
        description: 待办事项描述（可选）
    
    Returns:
        dict: 操作结果，包含成功状态和待办事项信息
    """
    try:
        # Prepare todo data
        todo_data = {
            "title": title,
            "description": description,
            "completed": False
        }
        
        # Normalize and validate todo data
        normalized_todo = normalize_todo_data(todo_data)
        
        # Save to database
        if save_todo_to_db(normalized_todo):
            logger.info(f"Successfully created todo: {title} (ID: {normalized_todo['id']})")
            return {
                "success": True,
                "message": f"成功创建待办事项: {title}",
                "todo": {
                    "id": normalized_todo["id"],
                    "title": normalized_todo["title"],
                    "description": normalized_todo["description"],
                    "completed": bool(normalized_todo["completed"]),
                    "created_at": normalized_todo["created_at"],
                    "updated_at": normalized_todo["updated_at"]
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "创建待办事项失败",
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
        logger.error(f"Error creating todo: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def update_todo(
    todo_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """更新待办事项信息。
    
    Args:
        todo_id: 待办事项的唯一标识ID（必填）
        title: 新的标题（可选）
        description: 新的描述（可选）
    
    Returns:
        dict: 操作结果，包含成功状态和更新后的待办事项信息
    """
    try:
        # Get existing todo
        existing_todo = get_todo_by_id_from_db(todo_id)
        
        if not existing_todo:
            logger.warning(f"Todo not found: {todo_id}")
            return {
                "success": False,
                "error": f"未找到ID为 {todo_id} 的待办事项",
                "timestamp": datetime.now().isoformat()
            }
        
        # Prepare update data
        todo_data = {
            "id": todo_id,
            "title": title if title is not None else existing_todo["title"],
            "description": description if description is not None else existing_todo["description"],
            "completed": existing_todo["completed"],
            "created_at": existing_todo["created_at"]
        }
        
        # Normalize and validate todo data
        normalized_todo = normalize_todo_data(todo_data)
        
        # Save to database
        if save_todo_to_db(normalized_todo):
            logger.info(f"Successfully updated todo: {todo_id}")
            return {
                "success": True,
                "message": f"成功更新待办事项",
                "todo": {
                    "id": normalized_todo["id"],
                    "title": normalized_todo["title"],
                    "description": normalized_todo["description"],
                    "completed": bool(normalized_todo["completed"]),
                    "created_at": normalized_todo["created_at"],
                    "updated_at": normalized_todo["updated_at"]
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "更新待办事项失败",
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
        logger.error(f"Error updating todo: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def delete_todo(todo_id: str) -> dict:
    """删除指定的待办事项。
    
    Args:
        todo_id: 待办事项的唯一标识ID
    
    Returns:
        dict: 操作结果，包含成功状态和消息
    """
    try:
        # Get todo to delete
        todo_to_delete = get_todo_by_id_from_db(todo_id)
        
        if not todo_to_delete:
            logger.warning(f"Todo not found for deletion: {todo_id}")
            return {
                "success": False,
                "error": f"未找到要删除的待办事项: {todo_id}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Delete todo
        deleted_title = todo_to_delete.get("title", "Unknown")
        
        if delete_todo_from_db(todo_id):
            logger.info(f"Successfully deleted todo: {deleted_title} (ID: {todo_id})")
            return {
                "success": True,
                "message": f"成功删除待办事项: {deleted_title}",
                "deleted_todo": todo_to_delete,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "删除待办事项失败",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error deleting todo: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
def toggle_todo_completion(todo_id: str, completed: Optional[bool] = None) -> dict:
    """切换待办事项的完成状态。如果不提供 completed 参数，则自动切换状态；如果提供了 completed 参数，则设置为指定状态。
    
    Args:
        todo_id: 待办事项的唯一标识ID
        completed: 完成状态（可选，如果提供则设置为该状态，否则自动切换）
    
    Returns:
        dict: 操作结果，包含成功状态和更新后的待办事项信息
    """
    try:
        # Get existing todo
        existing_todo = get_todo_by_id_from_db(todo_id)
        
        if not existing_todo:
            logger.warning(f"Todo not found: {todo_id}")
            return {
                "success": False,
                "error": f"未找到ID为 {todo_id} 的待办事项",
                "timestamp": datetime.now().isoformat()
            }
        
        # Determine new completion status
        if completed is None:
            # Toggle status
            new_completed = not existing_todo["completed"]
        else:
            # Set to specified status
            new_completed = completed
        
        # Prepare update data
        todo_data = {
            "id": todo_id,
            "title": existing_todo["title"],
            "description": existing_todo["description"],
            "completed": new_completed,
            "created_at": existing_todo["created_at"]
        }
        
        # Normalize and validate todo data
        normalized_todo = normalize_todo_data(todo_data)
        
        # Save to database
        if save_todo_to_db(normalized_todo):
            status_text = "完成" if new_completed else "未完成"
            logger.info(f"Successfully set todo {todo_id} to {status_text}")
            return {
                "success": True,
                "message": f"成功将待办事项设置为{status_text}",
                "todo": {
                    "id": normalized_todo["id"],
                    "title": normalized_todo["title"],
                    "description": normalized_todo["description"],
                    "completed": bool(normalized_todo["completed"]),
                    "created_at": normalized_todo["created_at"],
                    "updated_at": normalized_todo["updated_at"]
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "更新待办事项状态失败",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error toggling todo completion: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
