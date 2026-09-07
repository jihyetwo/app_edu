#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_marketing_to_blog.py
마케팅 콘텐츠(00-기획서.md / 00-기획안.md / 00-카드텍스트.md) → 네이버 블로그 & 앱 게시판 자동 배선 및 웹 반영 파이프라인.

기능:
  python3 scripts/sync_marketing_to_blog.py --status           # 전체 캠페인 배선 현황
  python3 scripts/sync_marketing_to_blog.py --sync-all --force # 전 캠페인 고품질 리빌드 및 웹 대시보드 반영
  python3 scripts/sync_marketing_to_blog.py --sync <폴더명>    # 특정 캠페인 동기화
  python3 scripts/sync_marketing_to_blog.py --watch            # EDU 폴더 실시간 감시 (제작 즉시 자동 반영)
  python3 scripts/sync_marketing_to_blog.py --copy-blog <이름> # 네이버 블로그 스마트에디터 복사
  python3 scripts/sync_marketing_to_blog.py --copy-app <이름>  # 앱 게시판 복사
  python3 scripts/sync_marketing_to_blog.py --copy-tags <이름> # 태그 30개 복사
"""

import os
import sys
import time
import argparse
import subprocess
import glob
import json
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blog_generator import extract_metadata, generate_blog_markdown
from app_board_generator import generate_app_board_markdown

# 기본 경로 설정
SOURCE_BASE = "/Users/name/Desktop/Cluade/EDU"
CATEGORIES = ["만든 콘텐츠", "단일 카드뉴스"]
REPO_OUTPUT = "/Users/name/cursor/app_edu/output/blog"
MULTICHANNEL_SYNC = "/Users/name/Desktop/Cluade/다채널"

# 우선 탐색할 기획서 파일명 순위
PLAN_FILE_CANDIDATES = [
    "00-기획안.md",
    "00-기획서.md",
    "00-카드텍스트.md",
    "00-기획서-노션용.md"
]

def get_all_campaigns():
    """EDU 폴더 내 모든 마케팅 캠페인 디렉터리 목록 반환"""
    campaigns = []
    for cat in CATEGORIES:
        cat_path = os.path.join(SOURCE_BASE, cat)
        if not os.path.exists(cat_path):
            continue
        for item in sorted(os.listdir(cat_path)):
            item_path = os.path.join(cat_path, item)
            if not os.path.isdir(item_path) or item.startswith(".") or item.startswith("_"):
                continue
            
            # 우선순위 기준 기획서 파일 탐색
            plan_file = None
            for cand in PLAN_FILE_CANDIDATES:
                cand_path = os.path.join(item_path, cand)
                if os.path.exists(cand_path):
                    plan_file = cand_path
                    break
            
            # 기타 00-*.md 탐색
            if not plan_file:
                for fname in sorted(os.listdir(item_path)):
                    if fname.startswith("00-") and fname.endswith(".md"):
                        plan_file = os.path.join(item_path, fname)
                        break
            
            has_blog = os.path.exists(os.path.join(item_path, "01_블로그.md")) or os.path.exists(os.path.join(REPO_OUTPUT, item, "01_블로그.md"))
            has_app = os.path.exists(os.path.join(item_path, "02_앱게시판.md")) or os.path.exists(os.path.join(REPO_OUTPUT, item, "02_앱게시판.md"))
            in_source = os.path.exists(os.path.join(item_path, "01_블로그.md"))
            in_repo = os.path.exists(os.path.join(REPO_OUTPUT, item, "01_블로그.md"))
            
            campaigns.append({
                "category": cat,
                "folder_name": item,
                "path": item_path,
                "plan_file": plan_file,
                "has_blog": has_blog,
                "has_app": has_app,
                "in_source": in_source,
                "in_repo": in_repo
            })
    return campaigns

def find_campaign_by_query(query):
    """폴더명이나 키워드로 캠페인 검색"""
    all_c = get_all_campaigns()
    for c in all_c:
        if query.lower() in c["folder_name"].lower():
            return c
    return None

def trigger_rebuild():
    """정적 대시보드(index.html) 리빌드 호출"""
    try:
        from build_static_site import build_static_html
        build_static_html()
        return True
    except Exception as e:
        print(f"⚠️  [대시보드 빌드 알림]: {e}")
        return False

def process_campaign(campaign, force=False):
    """단일 캠페인을 고품질 블로그 및 앱 게시판으로 변환 및 배선"""
    item_path = campaign["path"]
    folder_name = campaign["folder_name"]
    plan_file = campaign["plan_file"]

    if not plan_file or not os.path.exists(plan_file):
        print(f"⚠️  [스킵] {folder_name}: 기획서(00-*.md) 파일이 없습니다.")
        return False

    blog_path = os.path.join(item_path, "01_블로그.md")
    app_path = os.path.join(item_path, "02_앱게시판.md")

    if not force and os.path.exists(blog_path) and os.path.exists(app_path):
        print(f"⏩ [이미 생성됨] {folder_name} (강제 갱신: --force)")
        return True

    print(f"⚙️  [변환 중] {folder_name} ({os.path.basename(plan_file)}) ...")
    with open(plan_file, "r", encoding="utf-8", errors="ignore") as fp:
        raw_plan = fp.read()
    meta = extract_metadata(raw_plan, folder_name=folder_name)

    # 1. 고품질 01_블로그.md 및 02_앱게시판.md 생성
    blog_content, blog_info = generate_blog_markdown(meta, folder_name=folder_name)
    app_content, app_info = generate_app_board_markdown(blog_content, meta, folder_name=folder_name)

    # 2. repo output에 안전하게 저장 (대시보드 소스)
    repo_dest = os.path.join(REPO_OUTPUT, folder_name)
    os.makedirs(repo_dest, exist_ok=True)
    with open(os.path.join(repo_dest, "01_블로그.md"), "w", encoding="utf-8") as fp:
        fp.write(blog_content)
    with open(os.path.join(repo_dest, "02_앱게시판.md"), "w", encoding="utf-8") as fp:
        fp.write(app_content)

    # 3. 원본 EDU 마케팅 폴더 및 다채널 폴더에 쓰기 (작업 편의 제공)
    written_to_source = False
    try:
        with open(blog_path, "w", encoding="utf-8") as fp:
            fp.write(blog_content)
        with open(app_path, "w", encoding="utf-8") as fp:
            fp.write(app_content)
        written_to_source = True
    except (PermissionError, OSError):
        pass

    if os.path.exists(MULTICHANNEL_SYNC):
        try:
            multi_dest = os.path.join(MULTICHANNEL_SYNC, folder_name)
            os.makedirs(multi_dest, exist_ok=True)
            with open(os.path.join(multi_dest, "01_블로그.md"), "w", encoding="utf-8") as fp:
                fp.write(blog_content)
            with open(os.path.join(multi_dest, "02_앱게시판.md"), "w", encoding="utf-8") as fp:
                fp.write(app_content)
        except (PermissionError, OSError):
            pass

    print(f"✅ [완료] {folder_name}")
    print(f"   · 카테고리: [{meta['category_type']}] | 글자수: {blog_info['char_count']:,}자 | 태그: {len(blog_info['tags'])}개")
    if written_to_source:
        print(f"   · EDU 원본 동기화 완료: {blog_path}")
    return True

def copy_to_clipboard(text):
    """macOS pbcopy를 이용해 클립보드에 복사"""
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(input=text.encode("utf-8"))
        return p.returncode == 0
    except Exception:
        return False

def show_status():
    """모든 마케팅 캠페인의 블로그 배선 현황 출력"""
    campaigns = get_all_campaigns()
    print("=" * 85)
    print(f"📊 EDU 마케팅 캠페인 → 블로그 & 앱 게시판 배선 현황 (총 {len(campaigns)}개)")
    print("=" * 85)
    print(f"{'분류':<12} | {'캠페인 폴더':<35} | {'기획서':<6} | {'블로그':<6} | {'앱게시판':<6}")
    print("-" * 85)
    
    ready_count = 0
    pending_count = 0
    for c in campaigns:
        p_mark = "✔" if c["plan_file"] else "✘"
        b_mark = "✔" if c["has_blog"] else "—"
        a_mark = "✔" if c["has_app"] else "—"
        if c["has_blog"] and c["has_app"]:
            ready_count += 1
        else:
            if c["plan_file"]:
                pending_count += 1
        print(f"{c['category']:<12} | {c['folder_name'][:33]:<35} | {p_mark:<6} | {b_mark:<6} | {a_mark:<6}")

    print("-" * 85)
    print(f"💡 요약: 배선 완료 {ready_count}개 / 변환 대기 {pending_count}개 / 기획서 없음 {len(campaigns)-ready_count-pending_count}개")
    print("=" * 85)

def watch_mode(interval=3):
    """폴더 감시 모드: EDU 폴더에 새로운 마케팅 기획서가 생기거나 수정되면 즉시 블로그 생성 + index.html 자동 리빌드"""
    print(f"👀 [실시간 감시 모드 가동] {SOURCE_BASE} 폴더를 감시 중입니다...")
    print("   💡 EDU 폴더에서 기획서를 저장하면 1초 내에 블로그 생성 및 웹 대시보드가 자동 갱신됩니다. (종료: Ctrl+C)")
    seen_mtimes = {}
    
    # 초기 mtime 등록
    for c in get_all_campaigns():
        if c["plan_file"] and os.path.exists(c["plan_file"]):
            seen_mtimes[c["folder_name"]] = os.path.getmtime(c["plan_file"])

    while True:
        try:
            campaigns = get_all_campaigns()
            changed = False
            for c in campaigns:
                if not c["plan_file"] or not os.path.exists(c["plan_file"]):
                    continue
                mtime = os.path.getmtime(c["plan_file"])
                # 새로 생겼거나 수정되었을 때
                if c["folder_name"] not in seen_mtimes:
                    seen_mtimes[c["folder_name"]] = mtime
                    print(f"\n✨ [새 캠페인 감지] {c['folder_name']}")
                    process_campaign(c, force=True)
                    changed = True
                elif mtime > seen_mtimes[c["folder_name"]]:
                    seen_mtimes[c["folder_name"]] = mtime
                    print(f"\n🔄 [기획서 수정 감지] {c['folder_name']}")
                    process_campaign(c, force=True)
                    changed = True
                    
            if changed:
                print("⚡ [웹 대시보드 자동 반영 중...]")
                trigger_rebuild()
                print("🎉 [반영 완료] 대시보드(index.html)가 최신 상태로 갱신되었습니다!\n")

            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 감시 모드를 종료합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(interval)

def get_blog_file(campaign):
    p1 = os.path.join(REPO_OUTPUT, campaign["folder_name"], "01_블로그.md")
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(campaign["path"], "01_블로그.md")
    if os.path.exists(p2):
        return p2
    return None

def get_app_file(campaign):
    p1 = os.path.join(REPO_OUTPUT, campaign["folder_name"], "02_앱게시판.md")
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(campaign["path"], "02_앱게시판.md")
    if os.path.exists(p2):
        return p2
    return None

def main():
    parser = argparse.ArgumentParser(description="EDU 마케팅 → 블로그 & 앱게시판 자동 배선 파이프라인")
    parser.add_argument("--status", action="store_true", help="전체 캠페인 배선 상태 확인")
    parser.add_argument("--sync", type=str, help="특정 캠페인 폴더명 동기화 및 블로그/앱게시판 생성")
    parser.add_argument("--sync-all", action="store_true", help="모든 캠페인 일괄 생성 및 대시보드 리빌드")
    parser.add_argument("--force", action="store_true", help="이미 생성된 파일도 강제 덮어쓰기")
    parser.add_argument("--watch", action="store_true", help="실시간 폴더 감시 모드 실행 (새 기획서 감지 시 즉시 반영)")
    parser.add_argument("--copy-blog", type=str, help="해당 캠페인의 블로그 본문을 macOS 클립보드로 복사")
    parser.add_argument("--copy-app", type=str, help="해당 캠페인의 앱게시판 콘텐츠를 macOS 클립보드로 복사")
    parser.add_argument("--copy-tags", type=str, help="해당 캠페인의 네이버 태그 30개를 클립보드로 복사")

    args = parser.parse_args()

    if args.status or len(sys.argv) == 1:
        show_status()
        return

    if args.sync_all:
        campaigns = get_all_campaigns()
        print(f"🚀 총 {len(campaigns)}개 캠페인 고품질 일괄 변환을 시작합니다...")
        success = 0
        for c in campaigns:
            if c["plan_file"]:
                if process_campaign(c, force=args.force):
                    success += 1
        print(f"\n🎉 일괄 변환 완료! 성공: {success}건")
        print("⚡ [웹 대시보드 자동 갱신 중...]")
        trigger_rebuild()
        print("✅ [대시보드 반영 완료] index.html이 최신 상태로 갱신되었습니다.")
        return

    if args.sync:
        c = find_campaign_by_query(args.sync)
        if not c:
            print(f"❌ 검색어 '{args.sync}'에 해당하는 캠페인을 찾을 수 없습니다.")
            return
        process_campaign(c, force=True)
        trigger_rebuild()
        return

    if args.watch:
        watch_mode()
        return

    if args.copy_blog:
        c = find_campaign_by_query(args.copy_blog)
        if not c:
            print(f"❌ '{args.copy_blog}' 캠페인을 찾을 수 없습니다.")
            return
        blog_file = get_blog_file(c)
        if not blog_file:
            print(f"⚠️  먼저 변환을 실행합니다: {c['folder_name']}")
            process_campaign(c, force=True)
            blog_file = get_blog_file(c)
        with open(blog_file, "r", encoding="utf-8") as fp:
            text = fp.read()
        if copy_to_clipboard(text):
            print(f"📋 [복사 완료] '{c['folder_name']}' 블로그 전문이 클립보드에 복사되었습니다!")
            print("   👉 네이버 블로그 스마트에디터 ONE에 붙여넣기(Cmd+V)하세요.")
        return

    if args.copy_app:
        c = find_campaign_by_query(args.copy_app)
        if not c:
            print(f"❌ '{args.copy_app}' 캠페인을 찾을 수 없습니다.")
            return
        app_file = get_app_file(c)
        if not app_file:
            process_campaign(c, force=True)
            app_file = get_app_file(c)
        with open(app_file, "r", encoding="utf-8") as fp:
            text = fp.read()
        if copy_to_clipboard(text):
            print(f"📋 [복사 완료] '{c['folder_name']}' 앱 게시판 전문이 클립보드에 복사되었습니다!")
        return

    if args.copy_tags:
        c = find_campaign_by_query(args.copy_tags)
        if not c:
            print(f"❌ '{args.copy_tags}' 캠페인을 찾을 수 없습니다.")
            return
        blog_file = get_blog_file(c)
        if not blog_file:
            process_campaign(c, force=True)
            blog_file = get_blog_file(c)
        with open(blog_file, "r", encoding="utf-8") as fp:
            text = fp.read()
        tag_match = re.search(r"## 🏷️ 네이버 블로그 태그.*?\n```(.*?)```", text, re.DOTALL)
        if tag_match:
            tags = tag_match.group(1).strip()
            if copy_to_clipboard(tags):
                print(f"🏷️  [복사 완료] 태그 30개가 클립보드에 복사되었습니다!\n{tags}")
        return

if __name__ == "__main__":
    main()
