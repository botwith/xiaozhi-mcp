# netease_music.py
from fastmcp import FastMCP
import sys
import logging
import subprocess
import os
from datetime import datetime

logger = logging.getLogger('NeteaseMusic')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = FastMCP("NeteaseMusic")

# Path to NeteaseMusic app on Mac
NETEASE_MUSIC_APP_PATH = "/Applications/NeteaseMusic.app"

def open_netease_music() -> dict:
    """Open NeteaseMusic application on Mac."""
    try:
        # Check if running on Mac
        if sys.platform != 'darwin':
            return {
                "success": False,
                "error": f"此工具仅支持 macOS 系统。当前系统: {sys.platform}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if the app exists
        if not os.path.exists(NETEASE_MUSIC_APP_PATH):
            return {
                "success": False,
                "error": f"未找到网易云音乐应用，路径: {NETEASE_MUSIC_APP_PATH}",
                "hint": "请确认网易云音乐已安装在 /Applications/NeteaseMusic.app",
                "timestamp": datetime.now().isoformat()
            }
        
        # Open the application using 'open' command
        logger.info(f"Opening NeteaseMusic app: {NETEASE_MUSIC_APP_PATH}")
        result = subprocess.run(
            ["open", NETEASE_MUSIC_APP_PATH],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info("Successfully opened NeteaseMusic app")
            return {
                "success": True,
                "message": "已成功打开网易云音乐应用",
                "app_path": NETEASE_MUSIC_APP_PATH,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Failed to open app: {result.stderr}")
            return {
                "success": False,
                "error": f"打开应用失败: {result.stderr}",
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout while opening NeteaseMusic app")
        return {
            "success": False,
            "error": "打开应用超时",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error opening NeteaseMusic app: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"打开应用时发生错误: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def control_netease_music_via_menu(action: str) -> dict:
    """Control NeteaseMusic app via GUI scripting (menu bar).
    
    Args:
        action: The action to perform ("play", "pause", "playpause", "next", "previous")
    """
    try:
        # Check if running on Mac
        if sys.platform != 'darwin':
            return {
                "success": False,
                "error": f"此工具仅支持 macOS 系统。当前系统: {sys.platform}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if NeteaseMusic is running
        check_app_script = '''
        tell application "System Events"
            return name of processes contains "NeteaseMusic"
        end tell
        '''
        
        result_check = subprocess.run(
            ["osascript", "-e", check_app_script],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if result_check.returncode != 0 or "true" not in result_check.stdout.lower():
            # App not running, try to open it first
            logger.info("NeteaseMusic not running, opening app first")
            open_result = open_netease_music()
            if not open_result.get("success"):
                return {
                    "success": False,
                    "error": "网易云音乐未运行，且无法打开应用",
                    "hint": "请手动打开网易云音乐应用",
                    "timestamp": datetime.now().isoformat()
                }
            # Wait a bit for app to start
            import time
            time.sleep(2)
        
        # Build AppleScript based on action
        # Try English menu first ("Controls"), then Chinese ("控制")
        if action == "playpause":
            # Toggle play/pause - try multiple menu item names
            applescript = '''
            tell application "System Events"
                tell process "NeteaseMusic"
                    tell menu bar 1
                        set menuNames to {"Controls", "控制"}
                        set playNames to {"Play", "播放", "Play/Pause"}
                        set pauseNames to {"Pause", "暂停"}
                        repeat with menuName in menuNames
                            try
                                tell menu bar item menuName
                                    tell menu 1
                                        -- Try pause first (if playing)
                                        repeat with pauseName in pauseNames
                                            if menu item pauseName exists then
                                                click menu item pauseName
                                                return
                                            end if
                                        end repeat
                                        -- Then try play
                                        repeat with playName in playNames
                                            if menu item playName exists then
                                                click menu item playName
                                                return
                                            end if
                                        end repeat
                                    end tell
                                end tell
                                exit repeat
                            end try
                        end repeat
                    end tell
                end tell
            end tell
            '''
        elif action == "next":
            applescript = '''
            tell application "System Events"
                tell process "NeteaseMusic"
                    tell menu bar 1
                        set menuNames to {"Controls", "控制"}
                        set nextNames to {"Next", "下一首", "Next Track"}
                        repeat with menuName in menuNames
                            try
                                tell menu bar item menuName
                                    tell menu 1
                                        repeat with nextName in nextNames
                                            if menu item nextName exists then
                                                click menu item nextName
                                                return
                                            end if
                                        end repeat
                                    end tell
                                end tell
                                exit repeat
                            end try
                        end repeat
                    end tell
                end tell
            end tell
            '''
        elif action == "previous":
            applescript = '''
            tell application "System Events"
                tell process "NeteaseMusic"
                    tell menu bar 1
                        set menuNames to {"Controls", "控制"}
                        set prevNames to {"Previous", "上一首", "Previous Track", "Prev"}
                        repeat with menuName in menuNames
                            try
                                tell menu bar item menuName
                                    tell menu 1
                                        repeat with prevName in prevNames
                                            if menu item prevName exists then
                                                click menu item prevName
                                                return
                                            end if
                                        end repeat
                                    end tell
                                end tell
                                exit repeat
                            end try
                        end repeat
                    end tell
                end tell
            end tell
            '''
        else:
            return {
                "success": False,
                "error": f"未知的控制操作: {action}",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"Controlling NeteaseMusic via menu: {action}")
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            action_names = {
                "playpause": "播放/暂停",
                "next": "下一首",
                "previous": "上一首"
            }
            logger.info(f"Successfully controlled NeteaseMusic: {action}")
            return {
                "success": True,
                "message": f"{action_names.get(action, action)}命令已执行",
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Failed to control NeteaseMusic: {result.stderr}")
            # Fallback to key code method
            return send_media_key_fallback(action)
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout while controlling NeteaseMusic")
        return {
            "success": False,
            "error": "控制网易云音乐超时",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error controlling NeteaseMusic: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"控制网易云音乐时发生错误: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def send_media_key_fallback(action: str) -> dict:
    """Fallback method: send media key using key codes.
    
    Args:
        action: The action ("playpause", "next", "previous")
    """
    key_mapping = {
        "playpause": (145, 100),  # F8: media code, standard code
        "next": (146, 101),       # F9: media code, standard code
        "previous": (144, 98)      # F7: media code, standard code
    }
    
    key_codes = key_mapping.get(action)
    if not key_codes:
        return {
            "success": False,
            "error": f"未知的操作: {action}",
            "timestamp": datetime.now().isoformat()
        }
    
    media_code, standard_code = key_codes
    
    # Try media key code first
    applescript1 = f'''
    tell application "System Events"
        key code {media_code}
    end tell
    '''
    
    logger.info(f"Trying fallback: sending key code {media_code} for {action}")
    result = subprocess.run(
        ["osascript", "-e", applescript1],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        action_names = {"playpause": "播放/暂停", "next": "下一首", "previous": "上一首"}
        return {
            "success": True,
            "message": f"{action_names.get(action, action)}命令已发送（使用按键码）",
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
    
    # Try standard key code
    applescript2 = f'''
    tell application "System Events"
        key code {standard_code}
    end tell
    '''
    
    result2 = subprocess.run(
        ["osascript", "-e", applescript2],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result2.returncode == 0:
        action_names = {"playpause": "播放/暂停", "next": "下一首", "previous": "上一首"}
        return {
            "success": True,
            "message": f"{action_names.get(action, action)}命令已发送（使用标准按键码）",
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "success": False,
            "error": f"发送媒体快捷键失败: {result.stderr}",
            "hint": "请确保网易云音乐正在运行，并且系统允许辅助功能控制",
            "timestamp": datetime.now().isoformat()
        }

# Add tool to open NeteaseMusic
@mcp.tool()
def open_music_app() -> dict:
    """我要使用網易雲音樂聽歌。打开网易云音乐应用程序。当用户想要听音乐时，使用此工具打开网易云音乐应用。
    
    此工具会在 macOS 系统上打开网易云音乐应用（/Applications/NeteaseMusic.app）。
    如果应用不存在或打开失败，将返回错误信息。
    """
    return open_netease_music()

# Add tool to play/pause music
@mcp.tool()
def play_pause_music() -> dict:
    """播放或暂停网易云音乐。控制网易云音乐应用的播放/暂停功能（相当于按F8）。
    
    当用户想要播放或暂停音乐时，使用此工具。
    """
    return control_netease_music_via_menu("playpause")

# Add tool to play previous track
@mcp.tool()
def previous_track() -> dict:
    """播放上一首歌曲。控制网易云音乐应用切换到上一首歌曲（相当于按F7）。
    
    当用户想要播放上一首歌曲时，使用此工具。
    """
    return control_netease_music_via_menu("previous")

# Add tool to play next track
@mcp.tool()
def next_track() -> dict:
    """播放下一首歌曲。控制网易云音乐应用切换到下一首歌曲（相当于按F9）。
    
    当用户想要播放下一首歌曲时，使用此工具。
    """
    return control_netease_music_via_menu("next")

# Add tool to stop music
@mcp.tool()
def stop_music() -> dict:
    """停止播放音乐。控制网易云音乐应用停止播放。
    
    当用户想要停止播放音乐时，使用此工具。如果应用正在播放，会先暂停播放。
    """
    # Stop is essentially pause, so we use playpause
    return control_netease_music_via_menu("playpause")

def control_volume_direct(action: str) -> dict:
    """Control volume directly using AppleScript set volume command on macOS.
    
    Args:
        action: The volume action ("mute", "unmute", "down", "up")
    """
    try:
        # Check if running on Mac
        if sys.platform != 'darwin':
            return {
                "success": False,
                "error": f"此工具仅支持 macOS 系统。当前系统: {sys.platform}",
                "timestamp": datetime.now().isoformat()
            }
        
        if action == "mute":
            # Toggle mute
            applescript = '''
            set isMuted to output muted of (get volume settings)
            set volume output muted (not isMuted)
            return isMuted
            '''
        elif action == "down":
            # Decrease volume by 10%
            applescript = '''
            set cur to output volume of (get volume settings)
            set newVol to cur - 10
            if newVol < 0 then set newVol to 0
            set volume output volume newVol
            return newVol
            '''
        elif action == "up":
            # Increase volume by 10%
            applescript = '''
            set cur to output volume of (get volume settings)
            set newVol to cur + 10
            if newVol > 100 then set newVol to 100
            set volume output volume newVol
            return newVol
            '''
        else:
            return {
                "success": False,
                "error": f"未知的音量控制操作: {action}",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"Controlling volume: {action}")
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully controlled volume: {action}")
            output = result.stdout.strip()
            if action == "mute":
                was_muted = output == "true"
                message = "已取消静音" if was_muted else "已静音"
            elif action == "down":
                message = f"音量已减小至 {output}%"
            elif action == "up":
                message = f"音量已增大至 {output}%"
            
            return {
                "success": True,
                "message": message,
                "action": action,
                "output": output,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"Failed to control volume: {result.stderr}")
            # Fallback: try using key codes
            return send_volume_key_fallback(action)
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout while controlling volume")
        return {
            "success": False,
            "error": "音量控制超时",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error controlling volume: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"音量控制时发生错误: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def send_volume_key_fallback(action: str) -> dict:
    """Fallback method: send volume key using key codes.
    
    Args:
        action: The volume action ("mute", "down", "up")
    """
    # Key codes: F10=109 (mute), F11=103 (down), F12=111 (up)
    key_codes = {
        "mute": 109,
        "down": 103,
        "up": 111
    }
    
    key_code = key_codes.get(action)
    if not key_code:
        return {
            "success": False,
            "error": f"未知的音量控制操作: {action}",
            "timestamp": datetime.now().isoformat()
        }
    
    applescript = f'''
    tell application "System Events"
        key code {key_code}
    end tell
    '''
    
    logger.info(f"Trying fallback: sending key code {key_code} for {action}")
    result = subprocess.run(
        ["osascript", "-e", applescript],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        action_names = {"mute": "静音", "down": "减小音量", "up": "增大音量"}
        return {
            "success": True,
            "message": f"{action_names.get(action, action)}命令已发送",
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "success": False,
            "error": f"发送音量控制键失败: {result.stderr}",
            "hint": "请确保系统允许辅助功能控制",
            "timestamp": datetime.now().isoformat()
        }

# Add tool to mute/unmute volume
@mcp.tool()
def mute_volume() -> dict:
    """静音或取消静音。使用系统音量控制功能来切换静音状态（相当于按F10）。
    
    当用户想要静音或取消静音时，使用此工具。
    """
    return control_volume_direct("mute")

# Add tool to decrease volume
@mcp.tool()
def decrease_volume() -> dict:
    """减小音量。使用系统音量控制功能来减小音量（相当于按F11）。
    
    当用户想要减小音量时，使用此工具。每次调用会减小10%的音量。
    """
    return control_volume_direct("down")

# Add tool to increase volume
@mcp.tool()
def increase_volume() -> dict:
    """增大音量。使用系统音量控制功能来增大音量（相当于按F12）。
    
    当用户想要增大音量时，使用此工具。每次调用会增大10%的音量。
    """
    return control_volume_direct("up")

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
