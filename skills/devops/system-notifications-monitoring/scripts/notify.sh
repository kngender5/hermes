#!/bin/bash
# notify.sh — reusable ntfy notification helper
# Usage: notify.sh <topic> <message> [title] [priority]

TOPIC="${1:?Usage: notify.sh <topic> <message> [title] [priority]}"
shift
MSG="${*:- }"
TITLE="${2:- Hermes}"
PRIORITY="${3:- 3}"
SERVER="${NTFY_SERVER:-https://ntfy.sh}"

curl -s -X POST "$SERVER/$TOPIC" \
    -H "Title: $TITLE" \
    -H "Priority: $PRIORITY" \
    -d "$MSG"
