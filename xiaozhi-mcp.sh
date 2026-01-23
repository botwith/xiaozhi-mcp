#!/bin/bash
# xiaozhi-mcp service script for Ubuntu
# Usage: ./xiaozhi-mcp.sh {start|stop|restart|status}

# Auto-detect project directory (where this script is located)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$PROJECT_DIR/.xiaozhi-mcp.pid"
LOG_FILE="$PROJECT_DIR/app.log"
ERROR_LOG="$PROJECT_DIR/app.error.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    fi
}

is_running() {
    local pid=$(get_pid)
    if [ -n "$pid" ]; then
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is not running
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

start() {
    if is_running; then
        echo -e "${YELLOW}xiaozhi-mcp is already running (PID: $(get_pid))${NC}"
        return 1
    fi

    echo -e "${GREEN}Starting xiaozhi-mcp...${NC}"

    cd "$PROJECT_DIR" || {
        echo -e "${RED}Failed to cd to $PROJECT_DIR${NC}"
        return 1
    }

    # Start in background with nohup
    nohup uv run python src/app.py >> "$LOG_FILE" 2>> "$ERROR_LOG" &
    local pid=$!

    # Save PID
    echo $pid > "$PID_FILE"

    # Wait a moment and check if process is still running
    sleep 2

    if is_running; then
        echo -e "${GREEN}xiaozhi-mcp started successfully (PID: $pid)${NC}"
        echo -e "Log file: $LOG_FILE"
        echo -e "Error log: $ERROR_LOG"
        return 0
    else
        echo -e "${RED}Failed to start xiaozhi-mcp. Check logs:${NC}"
        echo -e "  tail -f $ERROR_LOG"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop() {
    if ! is_running; then
        echo -e "${YELLOW}xiaozhi-mcp is not running${NC}"
        return 0
    fi

    local pid=$(get_pid)
    echo -e "${YELLOW}Stopping xiaozhi-mcp (PID: $pid)...${NC}"

    kill $pid 2>/dev/null

    # Wait for process to terminate
    local count=0
    while is_running && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done

    if is_running; then
        echo -e "${RED}Process did not stop gracefully, forcing...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
    fi

    rm -f "$PID_FILE"
    echo -e "${GREEN}xiaozhi-mcp stopped${NC}"
}

restart() {
    echo -e "${YELLOW}Restarting xiaozhi-mcp...${NC}"
    stop
    sleep 2
    start
}

status() {
    if is_running; then
        local pid=$(get_pid)
        echo -e "${GREEN}xiaozhi-mcp is running${NC}"
        echo -e "  PID: $pid"
        echo -e "  Log: $LOG_FILE"
        echo -e "  Error log: $ERROR_LOG"
        
        # Show recent logs
        echo -e "\n${YELLOW}Recent log entries:${NC}"
        tail -n 5 "$LOG_FILE" 2>/dev/null || echo "  (no log file yet)"
        return 0
    else
        echo -e "${RED}xiaozhi-mcp is not running${NC}"
        return 1
    fi
}

logs() {
    local lines=${2:-50}
    if is_running; then
        echo -e "${GREEN}Following xiaozhi-mcp logs (Ctrl+C to exit)...${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}xiaozhi-mcp is not running. Showing last $lines logs:${NC}"
        tail -n "$lines" "$LOG_FILE"
    fi
}

log() {
    local lines=${2:-50}
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${RED}Log file does not exist: $LOG_FILE${NC}"
        return 1
    fi

    echo -e "${BLUE}=== Last $lines lines of application log ===${NC}"
    tail -n "$lines" "$LOG_FILE"
}

error_logs() {
    local lines=${2:-50}
    if [ ! -f "$ERROR_LOG" ]; then
        echo -e "${RED}Error log file does not exist: $ERROR_LOG${NC}"
        echo -e "${YELLOW}No errors logged yet or service hasn't started.${NC}"
        return 1
    fi

    local error_count=$(wc -l < "$ERROR_LOG" 2>/dev/null || echo "0")
    echo -e "${BLUE}=== Error log ($error_count lines) ===${NC}"
    tail -n "$lines" "$ERROR_LOG"
}

search_logs() {
    if [ -z "$2" ]; then
        echo -e "${RED}Usage: $0 search-logs <keyword>${NC}"
        return 1
    fi

    local keyword="$2"
    local log_type="${3:-all}"  # all, app, error

    echo -e "${BLUE}=== Searching for '$keyword' ===${NC}\n"

    if [ "$log_type" = "all" ] || [ "$log_type" = "app" ]; then
        if [ -f "$LOG_FILE" ]; then
            echo -e "${GREEN}--- Application Log ---${NC}"
            grep -i --color=always "$keyword" "$LOG_FILE" || echo -e "${YELLOW}No matches found${NC}"
        fi
    fi

    if [ "$log_type" = "all" ] || [ "$log_type" = "error" ]; then
        if [ -f "$ERROR_LOG" ]; then
            echo -e "\n${RED}--- Error Log ---${NC}"
            grep -i --color=always "$keyword" "$ERROR_LOG" || echo -e "${YELLOW}No matches found${NC}"
        fi
    fi
}

clear_logs() {
    if [ ! -f "$LOG_FILE" ] && [ ! -f "$ERROR_LOG" ]; then
        echo -e "${YELLOW}No log files exist${NC}"
        return 0
    fi

    echo -e "${RED}This will delete all log files. Continue? (yes/no)${NC}"
    read -r response

    if [ "$response" != "yes" ]; then
        echo -e "${YELLOW}Cancelled${NC}"
        return 0
    fi

    if is_running; then
        echo -e "${YELLOW}Stopping service before clearing logs...${NC}"
        stop
        sleep 1
    fi

    local log_size=0
    if [ -f "$LOG_FILE" ]; then
        log_size=$(du -h "$LOG_FILE" 2>/dev/null | cut -f1)
        rm -f "$LOG_FILE"
        echo -e "${GREEN}Cleared app.log ($log_size)${NC}"
    fi

    if [ -f "$ERROR_LOG" ]; then
        local error_size=$(du -h "$ERROR_LOG" 2>/dev/null | cut -f1)
        rm -f "$ERROR_LOG"
        echo -e "${GREEN}Cleared app.error.log ($error_size)${NC}"
    fi

    echo -e "${GREEN}All logs cleared${NC}"
}

log_stats() {
    echo -e "${BLUE}=== Log Statistics ===${NC}\n"

    # App log stats
    if [ -f "$LOG_FILE" ]; then
        local app_size=$(du -h "$LOG_FILE" 2>/dev/null | cut -f1)
        local app_lines=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
        echo -e "${GREEN}Application Log:${NC}"
        echo -e "  File: $LOG_FILE"
        echo -e "  Size: $app_size"
        echo -e "  Lines: $app_lines"
    else
        echo -e "${YELLOW}Application Log: Not created yet${NC}"
    fi

    echo ""

    # Error log stats
    if [ -f "$ERROR_LOG" ]; then
        local error_size=$(du -h "$ERROR_LOG" 2>/dev/null | cut -f1)
        local error_lines=$(wc -l < "$ERROR_LOG" 2>/dev/null || echo "0")
        echo -e "${RED}Error Log:${NC}"
        echo -e "  File: $ERROR_LOG"
        echo -e "  Size: $error_size"
        echo -e "  Lines: $error_lines"
    else
        echo -e "${GREEN}Error Log: No errors yet${NC}"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$@"
        ;;
    log)
        log "$@"
        ;;
    error-logs)
        error_logs "$@"
        ;;
    search-logs)
        search_logs "$@"
        ;;
    clear-logs)
        clear_logs
        ;;
    log-stats)
        log_stats
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|log|error-logs|search-logs|clear-logs|log-stats}"
        echo ""
        echo "Service Commands:"
        echo "  start        - Start xiaozhi-mcp service"
        echo "  stop         - Stop xiaozhi-mcp service"
        echo "  restart      - Restart xiaozhi-mcp service"
        echo "  status       - Show service status"
        echo ""
        echo "Log Commands:"
        echo "  logs [n]             - Follow service logs (default 50 lines if not running)"
        echo "  log [n]              - Show last n lines of app log (default 50)"
        echo "  error-logs [n]       - Show last n lines of error log (default 50)"
        echo "  search-logs <keyword>  - Search logs for keyword (app+error logs)"
        echo "  clear-logs           - Clear all log files"
        echo "  log-stats            - Show log file statistics"
        echo ""
        echo "Examples:"
        echo "  $0 logs                # Follow logs in real-time"
        echo "  $0 log 100            # Show last 100 lines"
        echo "  $0 error-logs          # Show error log"
        echo "  $0 search-logs ERROR   # Search for 'ERROR' in logs"
        exit 1
        ;;
esac

exit $?
