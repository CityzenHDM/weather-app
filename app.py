import streamlit as st
import requests

# -----------------------------------------------------------------------------
# API KEY 설정
# -----------------------------------------------------------------------------
weather_api_key = st.secrets.get("WEATHER_API_KEY")
naver_client_id = st.secrets.get("NAVER_CLIENT_ID")
naver_client_secret = st.secrets.get("NAVER_CLIENT_SECRET")

# -----------------------------------------------------------------------------
# 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="오늘의 날씨 & 지역 뉴스",
    page_icon="🌤️",
    layout="centered"
)

st.markdown("""
<style>
.di-box {
    padding: 20px;
    background-color: #fff9db;
    border-radius: 10px;
    border-left: 5px solid #f1c40f;
}
.style-box {
    padding: 20px;
    background-color: #e3f2fd;
    border-radius: 10px;
    border-left: 5px solid #2196f3;
}
.news-box {
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #dee2e6;
    margin-bottom: 10px;
}
.section-title {
    font-weight: bold;
    font-size: 1.2rem;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 날씨 분석 로직
# -----------------------------------------------------------------------------
def get_weather_insights(temp, humidity):
    di = 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3

    if di >= 80:
        di_lvl, di_dsc, keyword = "🔴 매우 높음", "폭염으로 불쾌감이 큽니다.", "폭염"
    elif di >= 75:
        di_lvl, di_dsc, keyword = "🟠 높음", "무더위와 습도가 높습니다.", "무더위"
    elif di >= 68:
        di_lvl, di_dsc, keyword = "🟡 보통", "무난한 날씨입니다.", "날씨"
    else:
        di_lvl, di_dsc, keyword = "🟢 낮음", "쾌적한 날씨입니다.", "쾌청"

    if temp >= 28:
        comm, outfit = "🥵 무더운 날씨!", "민소매, 반바지, 린넨"
    elif 20 <= temp < 28:
        comm, outfit = "😎 활동하기 좋은 날씨", "반팔, 셔츠, 청바지"
    elif 12 <= temp < 20:
        comm, outfit = "🧥 쌀쌀한 날씨", "자켓, 가디건"
    else:
        comm, outfit = "❄️ 추운 날씨", "코트, 패딩"

    return di, di_lvl, di_dsc, comm, outfit, keyword

# -----------------------------------------------------------------------------
# 네이버 뉴스 API (도시별)
# -----------------------------------------------------------------------------
def get_weather_news_naver(city, keyword):
    if not naver_client_id or not naver_client_secret:
        return []

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret
    }
    params = {
        "query": f"{city} {keyword} 날씨",
        "display": 5,
        "sort": "date"
    }

    res = requests.get(url, headers=headers, params=params)
    return res.json().get("items", [])

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
st.title("🌤️ Weather & Local Life Guide")
st.markdown("도시별 실시간 날씨 · 생활지수 · 코디 · 지역 뉴스")
st.divider()

# 사이드바
with st.sidebar:
    st.header("⚙️ Settings")
    if not weather_api_key:
        weather_api_key = st.text_input("Weather API Key", type="password")
    if not naver_client_id:
        naver_client_id = st.text_input("Naver Client ID", type="password")
    if not naver_client_secret:
        naver_client_secret = st.text_input("Naver Client Secret", type="password")

# 입력
city = st.text_input("도시 이름 (영어)", placeholder="Seoul, Asan, Busan")

if st.button("날씨 분석", use_container_width=True):
    if not weather_api_key or not city:
        st.warning("API Key와 도시를 입력하세요.")
    else:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&lang=ko"
        data = requests.get(url).json()

        t = data["current"]["temp_c"]
        h = data["current"]["humidity"]

        di_v, di_l, di_d, comm, outfit, keyword = get_weather_insights(t, h)

        # 실제 지역명 (한글)
        city_ko = data["location"]["name"]

        st.success(f"📍 {city_ko}, {data['location']['country']}")

        # 요약
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 온도", f"{t}°C")
        c2.metric("체감 온도", f"{data['current']['feelslike_c']}°C")
        c3.metric("습도", f"{h}%")

        st.write("")

        # 불쾌지수 / 스타일링
        left, right = st.columns(2)

        with left:
            st.markdown('<p class="section-title">📊 생활 지수 분석</p>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="di-box">
                    <b>불쾌지수:</b> {di_l} ({di_v:.1f})<br>
                    {di_d}
                </div>
            """, unsafe_allow_html=True)

        with right:
            st.markdown('<p class="section-title">👕 오늘의 스타일링</p>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="style-box">
                    <b>{comm}</b><br>
                    추천 아이템: {outfit}
                </div>
            """, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 📰 지역별 날씨 뉴스
        # ---------------------------------------------------------------------
        st.divider()
        st.markdown(f"### 📰 {city_ko} 날씨 뉴스")

        news_list = get_weather_news_naver(city_ko, keyword)

        if not news_list:
            st.info(f"{city_ko} 관련 날씨 뉴스가 없습니다.")
        else:
            for n in news_list:
                st.markdown(f"""
                    <div class="news-box">
                        <a href="{n['link']}" target="_blank">
                            <b>{n['title']}</b>
                        </a><br>
                        <small>{n['originallink']}</small>
                    </div>
                """, unsafe_allow_html=True)
