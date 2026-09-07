#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_static_site.py
GitHub Pages 배포용 정적 웹 대시보드(index.html) 빌드 스크립트.
모든 블로그/앱게시판 렌더링 데이터를 단일 index.html에 임베딩하여 서버 없이 완벽 구동.
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preview_server import simple_markdown_to_html
from sync_marketing_to_blog import get_all_campaigns, REPO_OUTPUT

def build_static_html(output_file="index.html"):
    campaigns = get_all_campaigns()
    data = []

    for c in campaigns:
        folder = c["folder_name"]
        blog_path = os.path.join(REPO_OUTPUT, folder, "01_블로그.md")
        app_path = os.path.join(REPO_OUTPUT, folder, "02_앱게시판.md")
        if os.path.exists(blog_path):
            with open(blog_path, "r", encoding="utf-8") as fp:
                blog_md = fp.read()
            app_md = ""
            if os.path.exists(app_path):
                with open(app_path, "r", encoding="utf-8") as fp:
                    app_md = fp.read()
            blog_html = simple_markdown_to_html(blog_md)
            data.append({
                "category": c["category"],
                "folder_name": folder,
                "data": {
                    "folder": folder,
                    "blog_md": blog_md,
                    "app_md": app_md,
                    "blog_html": blog_html
                }
            })

    data_json = json.dumps(data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EDU 키즈 체험 & 교육정보 블로그 대시보드</title>
  <meta name="description" content="초등·유아 학부모를 위한 무료 체험학습 장소, 주말 나들이 가이드, 정부 양육 지원금 및 최신 교육 입시 정책 총정리">
  <meta name="keywords" content="무료체험, 아이랑가볼만한곳, 초등체험학습, 아자스쿨, 부모급여, 자녀장려금, 5등급제, 주말나들이">
  
  <!-- Open Graph (카카오톡, 페이스북 링크 공유 최적화) -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="EDU 키즈 체험 & 교육정보 블로그 대시보드">
  <meta property="og:description" content="학부모 필수 무료 체험 장소 및 정부 지원금, 교육 정책 완벽 가이드">
  <meta property="og:url" content="https://edu.form8.app/">
  <meta name="twitter:card" content="summary_large_image">
  
  <!-- 검색엔진 최적화 (SEO) -->
  <link rel="canonical" href="https://edu.form8.app/">
  <meta name="robots" content="index, follow">
  <style>
    :root {{
      --naver-green: #03C75A;
      --naver-dark: #029f48;
      --ajaschool-yellow: #FFB300;
      --bg: #F5F6F8;
      --card-bg: #FFFFFF;
      --text: #1E293B;
      --text-muted: #64748B;
      --border: #E2E8F0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Apple SD Gothic Neo", sans-serif; }}
    body {{ background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }}
    
    /* 사이드바 */
    .sidebar {{ width: 340px; background: #fff; border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }}
    .sidebar-header {{ padding: 18px 20px; border-bottom: 1px solid var(--border); background: #fafafa; }}
    .sidebar-header h1 {{ font-size: 16px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px; }}
    .sidebar-header p {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}
    .search-box {{ padding: 12px 16px; border-bottom: 1px solid var(--border); }}
    .search-input {{ width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; outline: none; }}
    .search-input:focus {{ border-color: var(--naver-green); }}
    .campaign-list {{ flex: 1; overflow-y: auto; list-style: none; }}
    .campaign-item {{ padding: 14px 16px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s; }}
    .campaign-item:hover {{ background: #f8fafc; }}
    .campaign-item.active {{ background: #ecfdf5; border-left: 4px solid var(--naver-green); }}
    .campaign-cat {{ font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }}
    .campaign-name {{ font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 2px; word-break: break-all; }}
    .campaign-badges {{ display: flex; gap: 6px; margin-top: 6px; }}
    .badge {{ font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }}
    .badge-blog {{ background: #dcfce7; color: #15803d; }}
    .badge-app {{ background: #e0f2fe; color: #0369a1; }}
    
    /* 메인 컨텐츠 영역 */
    .main {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
    .top-bar {{ height: 64px; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; display: flex; align-items: center; justify-content: space-between; }}
    .top-title {{ font-size: 16px; font-weight: 700; }}
    .top-actions {{ display: flex; gap: 10px; }}
    .btn {{ padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; transition: 0.15s; display: inline-flex; align-items: center; gap: 6px; }}
    .btn-naver {{ background: var(--naver-green); color: #fff; }}
    .btn-naver:hover {{ background: var(--naver-dark); }}
    .btn-secondary {{ background: #f1f5f9; color: #334155; }}
    .btn-secondary:hover {{ background: #e2e8f0; }}
    
    .tab-bar {{ display: flex; background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; gap: 20px; }}
    .tab {{ padding: 12px 4px; font-size: 14px; font-weight: 600; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; }}
    .tab.active {{ color: var(--naver-green); border-bottom-color: var(--naver-green); }}

    .content-area {{ flex: 1; overflow-y: auto; padding: 32px; display: flex; justify-content: center; }}
    .preview-container {{ width: 100%; max-width: 820px; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid var(--border); }}
    
    /* 네이버 블로그 스타일 본문 렌더링 */
    .naver-post h1 {{ font-size: 26px; font-weight: 800; line-height: 1.4; color: #111; margin-bottom: 24px; }}
    .naver-post h2 {{ font-size: 20px; font-weight: 700; color: #222; margin: 36px 0 16px; border-left: 4px solid var(--naver-green); padding-left: 10px; }}
    .naver-post p {{ font-size: 16px; line-height: 1.8; color: #333; margin-bottom: 18px; word-break: keep-all; }}
    .naver-post .img-placeholder {{ background: #f8fafc; border: 1px dashed #cbd5e1; padding: 24px; text-align: center; border-radius: 8px; color: #64748b; font-size: 14px; margin: 20px 0; }}
    .naver-post .summary-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px; margin: 24px 0; }}
    .naver-post .cta-box {{ background: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 20px; margin: 24px 0; }}
    .naver-post ul {{ padding-left: 20px; margin-bottom: 18px; }}
    .naver-post li {{ font-size: 15px; line-height: 1.7; color: #333; margin-bottom: 6px; }}
    .naver-post pre {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 13px; margin: 16px 0; }}
    
    /* 알림 토스트 */
    .toast {{ position: fixed; bottom: 24px; right: 24px; background: #0f172a; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 14px; font-weight: 500; display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 999; }}
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
    const CAMPAIGNS = {data_json};
    let currentCampaign = null;
    let currentTab = 'blog';

    function init() {{
      renderList(CAMPAIGNS);
      if (CAMPAIGNS.length > 0) {{
        selectCampaign(CAMPAIGNS[0].folder_name);
      }}
    }}

    function renderList(list) {{
      const ul = document.getElementById('campaign-list');
      ul.innerHTML = list.map(c => `
        <li class="campaign-item ${{currentCampaign && currentCampaign.folder_name === c.folder_name ? 'active' : ''}}" onclick="selectCampaign('${{c.folder_name}}')">
          <div class="campaign-cat">${{c.category}}</div>
          <div class="campaign-name">${{c.folder_name}}</div>
          <div class="campaign-badges">
            <span class="badge badge-blog">블로그 2,500자</span>
            <span class="badge badge-app">앱게시판</span>
          </div>
        </li>
      `).join('');
    }}

    function filterList() {{
      const q = document.getElementById('search').value.toLowerCase();
      const filtered = CAMPAIGNS.filter(c => c.folder_name.toLowerCase().includes(q) || c.category.toLowerCase().includes(q));
      renderList(filtered);
    }}

    function selectCampaign(folderName) {{
      currentCampaign = CAMPAIGNS.find(c => c.folder_name === folderName);
      if (!currentCampaign) return;
      document.getElementById('current-title').innerText = currentCampaign.folder_name;
      renderList(CAMPAIGNS);
      renderContent();
    }}

    function switchTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.getElementById('tab-' + tab).classList.add('active');
      renderContent();
    }}

    function renderContent() {{
      if (!currentCampaign || !currentCampaign.data) return;
      const view = document.getElementById('content-view');
      const data = currentCampaign.data;

      if (currentTab === 'blog') {{
        view.innerHTML = data.blog_html || '<pre>' + escapeHtml(data.blog_md) + '</pre>';
      }} else if (currentTab === 'app') {{
        view.innerHTML = '<pre style="white-space: pre-wrap; line-height: 1.7;">' + escapeHtml(data.app_md) + '</pre>';
      }} else {{
        view.innerHTML = '<pre style="white-space: pre-wrap; line-height: 1.6; font-size:13px;">' + escapeHtml(data.blog_md) + '</pre>';
      }}
    }}

    function escapeHtml(str) {{
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }}

    function showToast(msg) {{
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.display = 'block';
      setTimeout(() => {{ t.style.display = 'none'; }}, 2500);
    }}

    async function copyBlogHTML() {{
      if (!currentCampaign || !currentCampaign.data) return;
      await navigator.clipboard.writeText(currentCampaign.data.blog_md);
      showToast('📋 네이버 블로그용 본문이 복사되었습니다! (스마트에디터 ONE 붙여넣기)');
    }}

    async function copyMarkdown() {{
      if (!currentCampaign || !currentCampaign.data) return;
      await navigator.clipboard.writeText(currentCampaign.data.blog_md);
      showToast('📄 마크다운 전문이 복사되었습니다!');
    }}

    async function copyTags() {{
      if (!currentCampaign || !currentCampaign.data) return;
      const text = currentCampaign.data.blog_md;
      const m = text.match(/## 🏷️ 네이버 블로그 태그.*?\\n```(.*?)```/s);
      if (m) {{
        await navigator.clipboard.writeText(m[1].trim());
        showToast('🏷️ 태그 30개가 복사되었습니다!');
      }} else {{
        showToast('태그를 찾을 수 없습니다.');
      }}
    }}

    init();
  </script>
</body>
</html>
"""
    with open(output_file, "w", encoding="utf-8") as fp:
        fp.write(html_content)
    print(f"🎉 [정적 대시보드 빌드 완료] {output_file} ({len(data)}개 캠페인 내장, {os.path.getsize(output_file):,} bytes)")

    # sitemap.xml 자동 동기화
    base_url = os.environ.get("SITE_BASE_URL", "https://edu.form8.app").rstrip("/")
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{base_url}/</loc>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>'
    ]
    for item in data:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{base_url}/#{item["folder_name"]}</loc>')
        xml_lines.append('    <changefreq>weekly</changefreq>')
        xml_lines.append('    <priority>0.8</priority>')
        xml_lines.append('  </url>')
    xml_lines.append('</urlset>')
    sitemap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as sfp:
        sfp.write("\n".join(xml_lines) + "\n")
    print(f"🗺️  [sitemap.xml 자동 갱신] 총 {len(data)+1}개 URL 등록 완료 ({sitemap_path})")

if __name__ == "__main__":
    build_static_html()
