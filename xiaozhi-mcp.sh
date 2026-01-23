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
    if is_running; then
        echo -e "${GREEN}Following xiaozhi-mcp logs (Ctrl+C to exit)...${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${YELLOW}xiaozhi-mcp is not running. Showing last logs:${NC}"
        tail -n 50 "$LOG_FILE"
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
        logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start xiaozhi-mcp service"
        echo "  stop    - Stop xiaozhi-mcp service"
        echo "  restart - Restart xiaozhi-mcp service"
        echo "  status  - Show service status"
        echo "  logs    - Follow service logs"
        exit 1
        ;;
esac

exit $?
