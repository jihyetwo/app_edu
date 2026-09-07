#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app_board_generator.py
아자스쿨 앱 게시판 표준 포맷(02_앱게시판.md) 자동 변환 엔진.
참조 규격: /Users/name/Desktop/Cluade/다채널/blog-app-prompts.md 2부

변환 핵심 원칙:
1. 제목: 30자 이내, 리듬감 있는 호기심 유발형
2. 설명: 블로그 본문 내용 충실 반영, 이모티콘 100% 제거, bold(**) 100% 제거,
         이미지 마커([이미지:...]) 제거, 체크박스(□) 그대로 유지
3. 태그: 정확히 4개, 아자스쿨/체험학습 관련 태그 금지, # 접두사 한 줄
4. 메타 제목: 검색 최적화 분리 각도
5. 메타 설명: 150자 내외 클릭 유도형
"""

import re

import unicodedata

def remove_emojis(s):
    """Hangul, English, 숫자, 특수문자, 체크박스(□)는 100% 보존하고 모든 이모티콘만 안전하게 제거"""
    res = []
    for ch in s:
        cp = ord(ch)
        cat = unicodedata.category(ch)
        
        # 1. 한글 음절, 자모, 호환자모 100% 보존
        if (0xAC00 <= cp <= 0xD7AF) or (0x1100 <= cp <= 0x11FF) or (0x3130 <= cp <= 0x318F):
            res.append(ch)
            continue
            
        # 2. 기본 ASCII 영문, 숫자, 공백, 줄바꿈 보존
        if (0x20 <= cp <= 0x7E) or ch in "\n\r\t":
            res.append(ch)
            continue
            
        # 3. 체크박스(□) 보존
        if ch in "□■☑️☑":
            res.append("□")
            continue
            
        # 4. 한국어 문장부호 및 기호 보존
        if ch in "·•…※“”‘’「」『』【】（）()[]-~_!?:;.,/\\%&*+=<>":
            res.append(ch)
            continue
            
        # 5. 유니코드 이모지/심볼 카테고리(So, Sk, Sm, Cs 등) 제거
        if cat in ("So", "Sk", "Sm", "Cs"):
            continue
            
        # 6. 일반 문자/숫자/구두점/공백이면 보존
        if cat.startswith(("L", "N", "P", "Z")):
            res.append(ch)
            
    return "".join(res)

def remove_bold_formatting(text):
    """**bold** 또는 __bold__ 제거하고 내부 텍스트만 유지"""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    return text

def remove_image_markers(text):
    """[이미지: ...] 및 [썸네일 이미지] 등 이미지 마커 제거"""
    text = re.sub(r"\[이미지:[^\]]*\]", "", text)
    text = re.sub(r"\[썸네일\s*이미지\]", "", text)
    return text

def extract_blog_body_only(blog_content):
    """01_블로그.md에서 메타데이터 섹션과 태그/UTM을 제외한 순수 본문 블록만 추출"""
    match = re.search(r"## 📝 블로그 본문.*?\n(.*?)(?=\n---\n|\n## 🏷️ 네이버 블로그 태그|\Z)", blog_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return blog_content

def generate_app_board_markdown(blog_content, meta_info, folder_name=""):
    """
    01_블로그.md 내용으로부터 02_앱게시판.md 생성
    """
    main_kw = meta_info.get("main_keyword", "교육정보")
    title_raw = meta_info.get("title", "")
    
    # 1. 앱 게시판 제목 (30자 이내)
    # 예: "연차 안 쓰고 1주일, 단기 육아휴직 총정리"
    app_title = f"{main_kw} 핵심 변경점과 실전 총정리"
    if len(app_title) > 30:
        app_title = f"{main_kw} 핵심 체크 총정리"
    if len(app_title) > 30:
        app_title = app_title[:30]

    # 2. 설명 (본문 텍스트 클리닝)
    raw_body = extract_blog_body_only(blog_content)
    
    # 블로그 본문의 마크다운 헤더(# ...) 제거 또는 플랫화
    clean_desc = remove_image_markers(raw_body)
    clean_desc = remove_bold_formatting(clean_desc)
    clean_desc = remove_emojis(clean_desc)
    
    # H1, H2, H3 마크다운 샵(#) 기호 정리 (일반 텍스트 줄바꿈 형태로)
    clean_lines = []
    for line in clean_desc.splitlines():
        line_s = line.strip()
        if line_s.startswith("# "):
            clean_lines.append(line_s.lstrip("# ").strip())
        elif line_s.startswith("## "):
            clean_lines.append("")
            clean_lines.append(line_s.lstrip("## ").strip())
        elif line_s.startswith("### "):
            clean_lines.append(line_s.lstrip("### ").strip())
        else:
            clean_lines.append(line)
            
    # 연속 빈 줄 정리
    desc_text = "\n".join(clean_lines)
    desc_text = re.sub(r"\n{3,}", "\n\n", desc_text).strip()

    # 3. 태그 정확히 4개 (아자스쿨, 체험학습 금지)
    # 검색 키워드 중심
    candidate_tags = [
        main_kw,
        f"{main_kw}신청",
        f"{main_kw}조건",
        f"{main_kw}대상",
        "학부모정보",
        "초등교육"
    ]
    # 금지어 필터링
    filtered_tags = []
    for t in candidate_tags:
        t_clean = t.replace("#", "").strip()
        if "아자스쿨" in t_clean or "체험학습" in t_clean:
            continue
        if t_clean not in filtered_tags and len(filtered_tags) < 4:
            filtered_tags.append(t_clean)
            
    while len(filtered_tags) < 4:
        filtered_tags.append(f"{main_kw}안내{len(filtered_tags)}")
    
    tag_string = " ".join([f"#{t}" for t in filtered_tags[:4]])

    # 4. 메타 제목 (검색 노출 최적화 텍스트)
    meta_title = f"{main_kw} 대상 조건과 신청방법 한눈에 보기"

    # 5. 메타 설명 (150자 내외)
    meta_desc = f"{main_kw} 대상 및 신청 조건, 일정, 주의사항까지 학부모가 꼭 알아야 할 핵심 정보를 명확하게 정리했습니다. 헛걸음 없이 확인하고 신청하세요."
    if len(meta_desc) > 160:
        meta_desc = meta_desc[:150] + "..."

    # 최종 02_앱게시판.md 조합
    out = []
    out.append(f"# 앱 게시판 콘텐츠 — {main_kw}")
    out.append("")
    out.append(f"- 작성일: {meta_info.get('date', '2026-09-07')}")
    out.append("- 연결 블로그: `01_블로그.md`")
    out.append("- 생성 방식: 블로그 본문 자동 변환 (이모지·bold 제거, 이미지 마커 제외, 체크박스 유지)")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## [제목]")
    out.append("")
    out.append("```")
    out.append(app_title)
    out.append("```")
    out.append("")
    out.append("## [설명]")
    out.append("")
    out.append("```")
    out.append(desc_text)
    out.append("```")
    out.append("")
    out.append("## [태그]")
    out.append("")
    out.append("```")
    out.append(tag_string)
    out.append("```")
    out.append("")
    out.append("## [메타 제목]")
    out.append("")
    out.append("```")
    out.append(meta_title)
    out.append("```")
    out.append("")
    out.append("## [메타 설명]")
    out.append("")
    out.append("```")
    out.append(meta_desc)
    out.append("```")
    out.append("")

    return "\n".join(out), {
        "title": app_title,
        "tags": tag_string,
        "meta_title": meta_title,
        "meta_desc": meta_desc
    }

if __name__ == "__main__":
    sample_blog = """
## 📝 블로그 본문

# 단기 육아휴직 총정리 — 2026년 시행 안내

[썸네일 이미지]

🐶
"단기 육아휴직, 우리 집도 쓸 수 있을까요?"

아이와 함께하는 **소중한 시간**, 놓치지 마세요!

[이미지: 단기육아휴직-대상.png]

## 1. 무엇이 달라졌나요
2026년부터 ✅ 1주 또는 2주 단위로 사용 가능합니다.

□ 대상 자녀 나이 확인
□ 신청 일정 체크

아이와 함께하는 교육 활동, 아자스쿨에서 찾아보세요 💛
👉🏻 지금 바로 신청하세요!

---
## 🏷️ 네이버 블로그 태그
    """
    res, _ = generate_app_board_markdown(sample_blog, {"main_keyword": "단기육아휴직", "date": "2026-09-02"})
    print(res[:400])
