import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Global Music Top 10", page_icon="🎵")

# 2. 디자인 스타일 (CSS Flip Trick)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    
    .main { background-color: #f8fafc; }
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; color: #1e293b; }
    
    /* [핵심] 전체 컨테이너를 180도 뒤집어 스크롤바를 위로 보냄 */
    .scroll-wrapper {
        display: flex;
        overflow-x: auto;
        padding: 20px 10px;
        gap: 20px;
        transform: rotateX(180deg); /* 컨테이너 뒤집기 */
        -ms-transform: rotateX(180deg); /* IE 9 */
        -webkit-transform: rotateX(180deg); /* Safari and Chrome */
    }
    
    /* [핵심] 내부 카드들은 다시 180도 뒤집어 정방향으로 보이게 함 */
    .chart-col {
        min-width: 320px;
        max-width: 320px;
        flex-shrink: 0;
        transform: rotateX(180deg); /* 콘텐츠 다시 뒤집기 */
        -ms-transform: rotateX(180deg);
        -webkit-transform: rotateX(180deg);
    }

    /* 스크롤바 디자인 */
    .scroll-wrapper::-webkit-scrollbar { height: 10px; }
    .scroll-wrapper::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
    .scroll-wrapper::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 10px; border: 2px solid #f1f5f9; }

    .country-tag { font-size: 1.2rem; font-weight: 800; margin-bottom: 5px; padding-left: 10px; border-left: 4px solid #3b82f6; }
    .source-tag { font-size: 0.75rem; color: #94a3b8; padding-left: 14px; margin-bottom: 20px; }

    .song-card {
        background: #ffffff; border-radius: 12px; padding: 10px; margin-bottom: 12px;
        display: flex; align-items: center; text-decoration: none !important; color: inherit !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04); border: 1px solid #f1f5f9; height: 95px; transition: all 0.2s;
    }
    .song-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08); border-color: #3b82f6; }
    
    .rank-num { font-weight: 800; font-size: 1.1rem; color: #3b82f6; min-width: 35px; text-align: center; }
    .album-img { width: 60px; height: 60px; border-radius: 8px; margin-right: 12px; object-fit: cover; background-color: #f1f5f9; }
    .song-info { display: flex; flex-direction: column; justify-content: center; overflow: hidden; }
    .title { font-size: 0.95rem; font-weight: 700; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .artist { font-size: 0.85rem; color: #64748b; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

    .header-container { text-align: center; margin-top: -20px; margin-bottom: 20px; }
    .stButton > button { float: right; border-radius: 20px; font-size: 0.8rem; background-color: #ffffff; color: #64748b; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 3. 우측 상단 유틸리티
tcol1, tcol2 = st.columns([9, 1])
with tcol2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

# 4. 헤더
st.markdown("""
    <div class="header-container">
        <div class="main-title" style="font-size: 2.2rem; font-weight: 800;">🌎 Global Music Top 10</div>
        <div class="main-caption" style="color: #64748b;">차트 상단의 스크롤바를 밀어 각국의 순위를 확인하세요</div>
    </div>
    """, unsafe_allow_html=True)

# 5. 데이터 수집 함수
@st.cache_data(ttl=1800)
def fetch_data(code):
    HEADERS = {'User-Agent': 'Mozilla/5.0'}
    try:
        if code == "KR":
            res = requests.get("https://www.melon.com/chart/index.htm", headers=HEADERS, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('tr.lst50')[:10]
            return [{"title": r.select_one('.ellipsis.rank01 a').text, "artist": r.select_one('.ellipsis.rank02 span a').text, "img": r.select_one('img')['src']} for r in rows]
        elif code == "US":
            res = requests.get("https://www.billboard.com/charts/hot-100/", headers=HEADERS, timeout=7)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('.o-chart-results-list-row-container')[:10]
            return [{"title": i.select_one('h3#title-of-a-story').text.strip(), "artist": i.select_one('span.c-label.a-no-trucate').text.strip(), "img": i.select_one('img').get('data-lazy-src') or i.select_one('img').get('src')} for i in items]
        else:
            url = f"https://rss.applemarketingtools.com/api/v2/{code.lower()}/music/most-played/10/songs.json"
            res = requests.get(url, timeout=5)
            items = res.json()['feed']['results']
            return [{"title": i['name'], "artist": i['artistName'], "img": i['artworkUrl100']} for i in items]
    except: return None

countries = [
    ("🇰🇷 Korea", "KR", "Melon"), ("🇺🇸 USA", "US", "Billboard"), ("🇬🇧 UK", "GB", "Apple"),
    ("🇯🇵 Japan", "JP", "Apple"), ("🇨🇳 China", "CN", "Apple"), ("🇩🇪 Germany", "DE", "Apple"),
    ("🇫🇷 France", "FR", "Apple"), ("🇧🇷 Brazil", "BR", "Apple"), ("🇮🇳 India", "IN", "Apple"), ("🇨🇦 Canada", "CA", "Apple")
]

all_data = []
with st.spinner('차트 데이터를 불러오는 중...'):
    for name, code, source in countries:
        all_data.append((name, fetch_data(code), source))

# 6. 메인 차트 영역 (상단 스크롤바 적용)
final_html = '<div class="scroll-wrapper">'
for name, data, source in all_data:
    final_html += f'<div class="chart-col"><div class="country-tag">{name}</div><div class="source-tag">Source: {source}</div>'
    if not data:
        final_html += '<p style="text-align:center; color:#94a3b8; font-size:0.8rem;">No data</p>'
    else:
        for idx, item in enumerate(data):
            q = urllib.parse.quote(f"{item['title']} {item['artist']}")
            final_html += f"""
                <a href="https://www.youtube.com/results?search_query={q}" target="_blank" class="song-card">
                    <div class="rank-num">{idx+1}</div>
                    <img src="{item["img"]}" class="album-img">
                    <div class="song-info">
                        <div class="title">{item['title']}</div>
                        <div class="artist">{item['artist']}</div>
                    </div>
                </a>"""
    final_html += '</div>'
final_html += '</div>'

st.markdown(final_html, unsafe_allow_html=True)