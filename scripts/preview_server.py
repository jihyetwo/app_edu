#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preview_server.py
네이버 블로그 및 앱 게시판 시각적 미리보기 & 원클릭 클립보드 복사 로컬 웹 서버.
실행: python3 scripts/preview_server.py [--port 8765]
"""

import os
import re
import json
import http.server
import socketserver
import urllib.parse
from sync_marketing_to_blog import get_all_campaigns, get_blog_file, get_app_file, process_campaign, REPO_OUTPUT

PORT = 8765

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EDU 마케팅 → 블로그 & 앱게시판 배선 대시보드</title>
  <style>
    :root {
      --naver-green: #03C75A;
      --naver-dark: #029f48;
      --ajaschool-yellow: #FFB300;
      --bg: #F5F6F8;
      --card-bg: #FFFFFF;
      --text: #1E293B;
      --text-muted: #64748B;
      --border: #E2E8F0;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Apple SD Gothic Neo", sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
    
    /* 사이드바 */
    .sidebar { width: 340px; background: #fff; border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
    .sidebar-header { padding: 18px 20px; border-bottom: 1px solid var(--border); background: #fafafa; }
    .sidebar-header h1 { font-size: 17px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px; }
    .sidebar-header p { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
    .search-box { padding: 12px 16px; border-bottom: 1px solid var(--border); }
    .search-input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; outline: none; }
    .search-input:focus { border-color: var(--naver-green); }
    .campaign-list { flex: 1; overflow-y: auto; list-style: none; }
    .campaign-item { padding: 14px 16px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s; }
    .campaign-item:hover { background: #f8fafc; }
    .campaign-item.active { background: #ecfdf5; border-left: 4px solid var(--naver-green); }
    .campaign-cat { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }
    .campaign-name { font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 2px; }
    .campaign-badges { display: flex; gap: 6px; margin-top: 6px; }
    .badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
    .badge-blog { background: #dcfce7; color: #15803d; }
    .badge-app { background: #e0f2fe; color: #0369a1; }
    .badge-empty { background: #f1f5f9; color: #94a3b8; }
    
    /* 메인 컨텐츠 영역 */
    .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
    .top-bar { height: 64px; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; display: flex; align-items: center; justify-content: space-between; }
    .top-title { font-size: 16px; font-weight: 700; }
    .top-actions { display: flex; gap: 10px; }
    .btn { padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; transition: 0.15s; display: inline-flex; align-items: center; gap: 6px; }
    .btn-naver { background: var(--naver-green); color: #fff; }
    .btn-naver:hover { background: var(--naver-dark); }
    .btn-secondary { background: #f1f5f9; color: #334155; }
    .btn-secondary:hover { background: #e2e8f0; }
    
    .tab-bar { display: flex; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; gap: 20px; }
    .tab { padding: 12px 4px; font-size: 14px; font-weight: 600; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; }
    .tab.active { color: var(--naver-green); border-bottom-color: var(--naver-green); }

    .content-area { flex: 1; overflow-y: auto; padding: 32px; display: flex; justify-content: center; }
    .preview-container { width: 100%; max-width: 820px; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid var(--border); }
    
    /* 네이버 블로그 스타일 본문 렌더링 */
    .naver-post h1 { font-size: 26px; font-weight: 800; line-height: 1.4; color: #111; margin-bottom: 24px; }
    .naver-post h2 { font-size: 20px; font-weight: 700; color: #222; margin: 36px 0 16px; border-left: 4px solid var(--naver-green); padding-left: 10px; }
    .naver-post p { font-size: 16px; line-height: 1.8; color: #333; margin-bottom: 18px; word-break: keep-all; }
    .naver-post .img-placeholder { background: #f8fafc; border: 1px dashed #cbd5e1; padding: 24px; text-align: center; border-radius: 8px; color: #64748b; font-size: 14px; margin: 20px 0; }
    .naver-post .summary-box { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin: 24px 0; }
    .naver-post .cta-box { background: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 20px; margin: 24px 0; }
    .naver-post ul { padding-left: 20px; margin-bottom: 18px; }
    .naver-post li { font-size: 15px; line-height: 1.7; color: #333; margin-bottom: 6px; }
    .naver-post pre { background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 13px; margin: 16px 0; }
    
    /* 알림 토스트 */
    .toast { position: fixed; bottom: 24px; right: 24px; background: #0f172a; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 14px; font-weight: 500; display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 999; }
  </style>
</head>
<body>
  <div class="sidebar">
    <div class="sidebar-header">
      <h1>🚀 EDU 배선 대시보드</h1>
      <p>마케팅 산출물 → 블로그 & 앱게시판 파이프라인</p>
    </div>
    <div class="search-box">
      <input type="text" class="search-input" id="search" placeholder="캠페인 검색..." oninput="filterList()">
    </div>
    <ul class="campaign-list" id="campaign-list">
      <!-- 캠페인 리스트 동적 주입 -->
    </ul>
  </div>

  <div class="main">
    <div class="top-bar">
      <div class="top-title" id="current-title">캠페인을 선택하세요</div>
      <div class="top-actions">
        <button class="btn btn-secondary" onclick="copyTags()">🏷️ 태그 30개 복사</button>
        <button class="btn btn-secondary" onclick="copyMarkdown()">📄 마크다운 복사</button>
        <button class="btn btn-naver" onclick="copyBlogHTML()">📋 네이버 블로그용 복사</button>
      </div>
    </div>
    <div class="tab-bar">
      <div class="tab active" id="tab-blog" onclick="switchTab('blog')">네이버 블로그 미리보기</div>
      <div class="tab" id="tab-app" onclick="switchTab('app')">앱 게시판 원문</div>
      <div class="tab" id="tab-raw" onclick="switchTab('raw')">마크다운 소스</div>
    </div>
    <div class="content-area">
      <div class="preview-container">
        <div id="content-view" class="naver-post">
          <p style="color:#94a3b8; text-align:center; padding: 60px 0;">왼쪽 목록에서 캠페인을 선택하면 본문이 렌더링됩니다.</p>
        </div>
      </div>
    </div>
  </div>

  <div class="toast" id="toast">클립보드에 복사되었습니다!</div>

  <script>
    let campaigns = [];
    let currentCampaign = null;
    let currentTab = 'blog';

    async function loadCampaigns() {
      const res = await fetch('/api/campaigns');
      campaigns = await res.json();
      renderList(campaigns);
      if (campaigns.length > 0) {
        selectCampaign(campaigns[0].folder_name);
      }
    }

    function renderList(list) {
      const ul = document.getElementById('campaign-list');
      ul.innerHTML = list.map(c => `
        <li class="campaign-item ${currentCampaign && currentCampaign.folder_name === c.folder_name ? 'active' : ''}" onclick="selectCampaign('${c.folder_name}')">
          <div class="campaign-cat">${c.category}</div>
          <div class="campaign-name">${c.folder_name}</div>
          <div class="campaign-badges">
            <span class="badge badge-blog">블로그 2,500자</span>
            <span class="badge badge-app">앱게시판</span>
          </div>
        </li>
      `).join('');
    }

    function filterList() {
      const q = document.getElementById('search').value.toLowerCase();
      const filtered = campaigns.filter(c => c.folder_name.toLowerCase().includes(q) || c.category.toLowerCase().includes(q));
      renderList(filtered);
    }

    async function selectCampaign(folderName) {
      currentCampaign = campaigns.find(c => c.folder_name === folderName);
      document.getElementById('current-title').innerText = currentCampaign.folder_name;
      renderList(campaigns);
      
      const res = await fetch('/api/content?folder=' + encodeURIComponent(folderName));
      const data = await res.json();
      currentCampaign.data = data;
      renderContent();
    }

    function switchTab(tab) {
      currentTab = tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.getElementById('tab-' + tab).classList.add('active');
      renderContent();
    }

    function renderContent() {
      if (!currentCampaign || !currentCampaign.data) return;
      const view = document.getElementById('content-view');
      const data = currentCampaign.data;

      if (currentTab === 'blog') {
        view.innerHTML = data.blog_html || '<pre>' + escapeHtml(data.blog_md) + '</pre>';
      } else if (currentTab === 'app') {
        view.innerHTML = '<pre style="white-space: pre-wrap; line-height: 1.7;">' + escapeHtml(data.app_md) + '</pre>';
      } else {
        view.innerHTML = '<pre style="white-space: pre-wrap; line-height: 1.6; font-size:13px;">' + escapeHtml(data.blog_md) + '</pre>';
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 2500);
    }

    async function copyBlogHTML() {
      if (!currentCampaign || !currentCampaign.data) return;
      const html = currentCampaign.data.blog_html || currentCampaign.data.blog_md;
      await navigator.clipboard.writeText(currentCampaign.data.blog_md);
      showToast('📋 네이버 블로그용 본문이 복사되었습니다! (스마트에디터 ONE 붙여넣기)');
    }

    async function copyMarkdown() {
      if (!currentCampaign || !currentCampaign.data) return;
      await navigator.clipboard.writeText(currentCampaign.data.blog_md);
      showToast('📄 마크다운 전문이 복사되었습니다!');
    }

    async function copyTags() {
      if (!currentCampaign || !currentCampaign.data) return;
      const text = currentCampaign.data.blog_md;
      const m = text.match(/## 🏷️ 네이버 블로그 태그.*?\n```(.*?)```/s);
      if (m) {
        await navigator.clipboard.writeText(m[1].trim());
        showToast('🏷️ 태그 30개가 복사되었습니다!');
      } else {
        showToast('태그를 찾을 수 없습니다.');
      }
    }

    loadCampaigns();
  </script>
</body>
</html>
"""

def simple_markdown_to_html(md_text):
    """네이버 스마트에디터 ONE 스타일에 맞춘 기본 마크다운 HTML 렌더러"""
    lines = md_text.splitlines()
    html_out = []
    in_blog_body = False
    in_pre = False

    for line in lines:
        line_s = line.strip()
        if "## 📝 블로그 본문" in line_s:
            in_blog_body = True
            continue
        if in_blog_body and line_s.startswith("---") and "네이버 블로그 태그" in md_text[md_text.find(line):]:
            in_blog_body = False

        if not in_blog_body:
            continue

        if line_s.startswith("```"):
            in_pre = not in_pre
            continue

        if in_pre:
            html_out.append(f"<pre style='background:#f8fafc; padding:10px;'>{line}</pre>")
            continue

        if line_s.startswith("# "):
            html_out.append(f"<h1>{line_s[2:]}</h1>")
        elif line_s.startswith("## "):
            html_out.append(f"<h2>{line_s[3:]}</h2>")
        elif line_s.startswith("### "):
            html_out.append(f"<h3>{line_s[4:]}</h3>")
        elif line_s.startswith("[이미지:") or line_s.startswith("[썸네일 이미지]"):
            html_out.append(f"<div class='img-placeholder'>🖼️ <b>{line_s.strip('[]')}</b> (이미지 업로드 위치)</div>")
        elif "핵심 요약" in line_s:
            html_out.append(f"<div class='summary-box'><b>{line_s}</b>")
        elif line_s.startswith("✅"):
            html_out.append(f"<p style='color:#15803d; font-weight:600;'>{line_s}</p>")
        elif "👉🏻" in line_s or "아자스쿨에서" in line_s:
            html_out.append(f"<div class='cta-box'><p>{line_s}</p></div>")
        elif line_s.startswith("- ") or line_s.startswith("· "):
            html_out.append(f"<li>{line_s[2:]}</li>")
        elif line_s.startswith("□ "):
            html_out.append(f"<p><b>□</b> {line_s[2:]}</p>")
        elif line_s:
            # 볼드 처리
            formatted = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line_s)
            html_out.append(f"<p>{formatted}</p>")

    return "\n".join(html_out)

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        if parsed.path == "/api/campaigns":
            all_c = get_all_campaigns()
            data = []
            for c in all_c:
                if c["has_blog"]:
                    data.append({
                        "category": c["category"],
                        "folder_name": c["folder_name"]
                    })
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        if parsed.path == "/api/content":
            qs = urllib.parse.parse_qs(parsed.query)
            folder = qs.get("folder", [""])[0]
            
            blog_path = os.path.join(REPO_OUTPUT, folder, "01_블로그.md")
            app_path = os.path.join(REPO_OUTPUT, folder, "02_앱게시판.md")

            blog_md = ""
            app_md = ""
            if os.path.exists(blog_path):
                with open(blog_path, "r", encoding="utf-8") as fp:
                    blog_md = fp.read()
            if os.path.exists(app_path):
                with open(app_path, "r", encoding="utf-8") as fp:
                    app_md = fp.read()

            blog_html = simple_markdown_to_html(blog_md)

            res = {
                "folder": folder,
                "blog_md": blog_md,
                "app_md": app_md,
                "blog_html": blog_html
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
            return

        self.send_error(404, "Not Found")

def run_server(port=PORT):
    server = socketserver.TCPServer(("", port), DashboardHandler)
    print(f"🌐 [대시보드 실행 완료] http://localhost:{port}")
    print("   브라우저에서 접속하여 블로그 및 앱 게시판을 확인하고 원클릭 복사할 수 있습니다.")
    server.serve_forever()

if __name__ == "__main__":
    import sys
    p = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
