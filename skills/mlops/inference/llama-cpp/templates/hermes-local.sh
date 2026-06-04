#!/usr/bin/env bash
# hermes-local — Start/stop llama.cpp server for the 'local' Hermes profile
#
# Usage:
#   hermes-local start    — start llama-server in background
#   hermes-local stop     — stop llama-server
#   hermes-local status   — check if running
#   hermes-local restart  — restart
#   hermes-local chat     — start interactive chat with local model
#   hermes-local logs     — tail server logs
#
# Edit the paths below to match your setup.

LLAMA_CPP_DIR="/home/kng/projects/llama.cpp"
SERVER_BIN="${LLAMA_CPP_DIR}/build/bin/llama-server"
MODEL="/mnt/h/lmstudio/models/lmstudio-community/Qwen3.6-27B-GGUF/Qwen3.6-27B-Q4_K_M.gguf"
MMPROJ="/mnt/h/lmstudio/models/lmstudio-community/Qwen3.6-27B-GGUF/mmproj-Qwen3.6-27B-BF16.gguf"
PORT=8080
LOG_FILE="${HOME}/.hermes/profiles/local/logs/llama-server.log"
PID_FILE="${HOME}/.hermes/profiles/local/llama-server.pid"

mkdir -p "$(dirname "$LOG_FILE")"

start_server() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "llama-server already running (PID $(cat "$PID_FILE"))"
        return 0
    fi

    if [ ! -f "$SERVER_BIN" ]; then
        echo "ERROR: llama-server not found at $SERVER_BIN"
        echo "Build llama.cpp first:"
        echo "  cd $LLAMA_CPP_DIR && cmake -B build -DGGML_CUDA=OFF && cmake --build build -j\$(nproc) --target llama-server"
        return 1
    fi

    echo "Starting llama-server on port $PORT..."
    echo "  Model: $MODEL"

    # GPU offload: adjust n_gpu_layers based on your VRAM
    # RTX 4060 8GB: 20 layers works for 27B Q4
    N_GPU_LAYERS=20

    nohup "$SERVER_BIN" \
        --model "$MODEL" \
        --mmproj "$MMPROJ" \
        --host 127.0.0.1 \
        --port "$PORT" \
        --ctx-size 32768 \
        --n-gpu-layers "$N_GPU_LAYERS" \
        --jinja \
        --metrics \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    echo "Started (PID $!) — waiting for server..."

    for i in $(seq 1 30); do
        if curl -sf "http://127.0.0.1:${PORT}/health" > /dev/null 2>&1; then
            echo "✓ llama-server ready on port $PORT"
            return 0
        fi
        sleep 2
    done

    echo "⚠ Server may still be loading (large model). Check logs: $LOG_FILE"
    return 0
}

stop_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null
            sleep 2
            kill -9 "$PID" 2>/dev/null
            rm -f "$PID_FILE"
            echo "✓ llama-server stopped (PID $PID)"
        else
            echo "PID $PID not running, cleaning up"
            rm -f "$PID_FILE"
        fi
    else
        echo "No PID file found. Check: pgrep -f llama-server"
    fi
}

status_server() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        PID=$(cat "$PID_FILE")
        echo "✓ llama-server running (PID $PID) on port $PORT"
        curl -s "http://127.0.0.1:${PORT}/health" /dev/null 2>&1 || echo "  (server not responding yet)"
    else
        echo "✗ llama-server not running"
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
    fi
}

case "${1:-help}" in
    start)   start_server ;;
    stop)    stop_server ;;
    restart) stop_server; sleep 2; start_server ;;
    status)  status_server ;;
    chat)
        echo "Starting Hermes with local profile..."
        local -m "local/qwen3.6-27b" chat
        ;;
    logs)
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "Usage: hermes-local {start|stop|restart|status|chat|logs}"
        ;;
esac
