#!/bin/bash
# sync.sh - EDU 마케팅 폴더 ↔ 블로그 & 대시보드 자동 동기화 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ "$1" == "--watch" ] || [ "$1" == "-w" ]; then
    echo "👀 [EDU 실시간 감시 모드 시작]"
    echo "EDU 폴더에서 마케팅 기획서가 생성/수정되면 즉시 블로그 생성 및 웹 대시보드(index.html)가 자동 갱신됩니다."
    python3 scripts/sync_marketing_to_blog.py --watch
elif [ "$1" == "--status" ] || [ "$1" == "-s" ]; then
    python3 scripts/sync_marketing_to_blog.py --status
elif [ "$1" == "--copy-blog" ]; then
    python3 scripts/sync_marketing_to_blog.py --copy-blog "$2"
elif [ "$1" == "--copy-app" ]; then
    python3 scripts/sync_marketing_to_blog.py --copy-app "$2"
elif [ "$1" == "--copy-tags" ]; then
    python3 scripts/sync_marketing_to_blog.py --copy-tags "$2"
elif [ -n "$1" ]; then
    python3 scripts/sync_marketing_to_blog.py --sync "$1"
else
    echo "🚀 [전체 캠페인 일괄 동기화 및 대시보드 리빌드 시작]"
    python3 scripts/sync_marketing_to_blog.py --sync-all --force
    echo "🎉 동기화 완료! index.html 대시보드가 최신 상태입니다."
fi
