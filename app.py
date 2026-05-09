import streamlit as st
import json
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(dotenv_path=r"C:\Users\my coms\Desktop\biojobs\.env", override=True)
client = Anthropic()

st.set_page_config(page_title="바이오 취업 플랫폼", page_icon="🧬", layout="wide")

# CSS 스타일
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp { background-color: #f8fafb; }
    
    /* 헤더 */
    h1 { color: #1a1a2e; font-size: 2rem !important; font-weight: 700 !important; }
    
    /* 공고 카드 */
    .job-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        border: 1px solid #eef0f3;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s;
    }
    .job-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .job-title { font-size: 15px; font-weight: 600; color: #1a1a2e; margin-bottom: 6px; }
    .job-meta { font-size: 12px; color: #6b7280; }
    .job-tag {
        display: inline-block;
        background: #f0f4ff;
        color: #4361ee;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        margin-right: 4px;
        margin-top: 4px;
    }
    .job-tag.green { background: #f0fdf4; color: #16a34a; }
    .job-tag.orange { background: #fff7ed; color: #ea580c; }
    
    /* AI 분석 박스 */
    .ai-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        margin-bottom: 20px;
    }
    .ai-result {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        color: #1a1a2e;
        border-left: 4px solid #667eea;
    }
    
    /* 히스토리 카드 */
    .history-card {
        background: white;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 8px;
        border: 1px solid #eef0f3;
        font-size: 13px;
        cursor: pointer;
    }
    .history-date { font-size: 11px; color: #9ca3af; margin-bottom: 4px; }
    .history-preview { color: #374151; font-weight: 500; }
    
    /* 사이드바 */
    .css-1d391kg { background-color: #ffffff; }
    
    /* 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
    }
    .stButton > button:hover { opacity: 0.9; }
    
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)


# 데이터 로드
@st.cache_data
def load_jobs():
    with open('jobs.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 대화 히스토리 로드/저장
def load_history():
    if os.path.exists('history.json'):
        with open('history.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(background, result):
    history = load_history()
    history.insert(0, {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "background": background,
        "result": result
    })
    history = history[:20]  # 최근 20개만 유지
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

jobs = load_jobs()
df = pd.DataFrame(jobs)

# 사이드바
with st.sidebar:
    st.markdown("### 🧬 바이오 취업 플랫폼")
    st.caption(f"총 {len(df)}개 공고")
    st.divider()
    
    st.markdown("**🔍 필터**")
    source = st.selectbox("출처", ["전체"] + sorted(df['source'].unique().tolist()))
    edu_options = ["전체"] + sorted(df['company'].dropna().unique().tolist())
    edu = st.selectbox("학력", edu_options)
    
    st.divider()
    
    # 히스토리
    st.markdown("**🕘 분석 히스토리**")
    history = load_history()
    
    if not history:
        st.caption("아직 분석 기록이 없어요.")
    else:
        for i, h in enumerate(history):
            with st.expander(f"📄 {h['date']}"):
                st.caption(f"배경: {h['background'][:50]}...")
                st.markdown(h['result'])

# 메인
st.markdown("# 🧬 바이오 취업 플랫폼")
st.caption(f"마지막 업데이트: {df['crawled_at'].max()}")

# AI 분석 섹션
st.markdown("""
<div class="ai-box">
    <div style="font-size:18px; font-weight:700; margin-bottom:8px;">🤖 AI 맞춤 분석</div>
    <div style="font-size:13px; opacity:0.9;">본인의 학력, 경력, 관심 분야를 입력하면 AI가 맞춤 공고를 추천해드려요.</div>
</div>
""", unsafe_allow_html=True)

background = st.text_area(
    "본인 배경 입력",
    placeholder="예) 분자생물학 석사 졸업, 항체 연구 2년 경험, CRO 분야 관심, 연봉 4000만원 이상 희망...",
    height=90,
    label_visibility="collapsed"
)

if st.button("✨ AI 분석 시작"):
    if not background:
        st.warning("배경을 입력해주세요!")
    else:
        with st.spinner("AI가 분석 중이에요..."):
            job_summaries = []
            for job in jobs:
                summary = f"- {job['title']} ({job.get('company','')} {' '.join(job.get('tags',[])[:3])})"
                job_summaries.append(summary)
            job_list_text = "\n".join(job_summaries)
            
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"""당신은 바이오/제약 업계 취업 전문가입니다.

아래는 구직자의 배경입니다:
{background}

아래는 현재 채용 공고 목록입니다:
{job_list_text}

다음 형식으로 답변해주세요:
1. 강점 분석: (2-3문장)
2. 추천 직무 분야: (3가지)
3. 추천 공고: (위 목록에서 3-5개 선택, 이유 포함)
4. 취업 조언: (2-3문장)"""
                }]
            )
            
            result = response.content[0].text
            save_history(background, result)
            
            st.markdown('<div class="ai-result">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
            st.success("✅ 분석 결과가 히스토리에 저장됐어요!")
            st.rerun()

st.divider()

# 검색 + 공고 목록
keyword = st.text_input("🔍 키워드 검색", placeholder="직무, 키워드 입력...")

filtered = df.copy()
if keyword:
    filtered = filtered[
        filtered['title'].str.contains(keyword, case=False, na=False) |
        filtered['tags'].astype(str).str.contains(keyword, case=False, na=False)
    ]
if source != "전체":
    filtered = filtered[filtered['source'] == source]
if edu != "전체":
    filtered = filtered[filtered['company'] == edu]

st.caption(f"{len(filtered)}개 공고")

# 공고 카드
for _, job in filtered.iterrows():
    tags = job['tags'] if isinstance(job['tags'], list) else []
    
    tag_html = ""
    if job['company']:
        tag_html += f'<span class="job-tag">{job["company"]}</span>'
    if len(tags) > 0:
        tag_html += f'<span class="job-tag green">{tags[0]}</span>'
    if len(tags) > 1:
        tag_html += f'<span class="job-tag">{tags[1]}</span>'
    if len(tags) > 2:
        tag_html += f'<span class="job-tag orange">{tags[2]}</span>'
    if len(tags) > 3:
        tag_html += f'<span class="job-tag">{tags[3]}</span>'
    
    period_html = f'<span style="margin-left:8px;">📅 {job["period"]}</span>' if job['period'] else ''
    source_html = f'<span style="margin-left:8px;">📌 {job["source"]}</span>'
    link_html = f'<a href="{job["link"]}" target="_blank" style="float:right; background:linear-gradient(135deg,#667eea,#764ba2); color:white; padding:6px 16px; border-radius:8px; text-decoration:none; font-size:13px; font-weight:500;">지원하기</a>' if job['link'] else ''
    
    st.markdown(f"""
    <div class="job-card">
        {link_html}
        <div class="job-title">{job['title']}</div>
        <div class="job-meta">{period_html}{source_html}</div>
        <div style="margin-top:8px;">{tag_html}</div>
    </div>
    """, unsafe_allow_html=True)
