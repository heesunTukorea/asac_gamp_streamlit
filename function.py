import os
import streamlit as st
from databricks import sql
from PIL import Image, ImageOps
from io import BytesIO
import requests


# Databricks 연결 정보 설정


# 이미지 크기 조정 함수 정의
def resize_image(image_url, target_width=150, target_height=150):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img_resized = img.resize((target_width, target_height), Image.LANCZOS)
    return img_resized

# 이미지 출력 함수 정의
def display_image(img, caption):
    st.image(img, caption=caption, width=150)

    


# 페이지 변경 함수
def change_page(page):
    st.session_state.page = page
    st.experimental_rerun()





# 별점을 HTML로 변환하는 함수
def render_stars(rating):
    full_stars = int(rating)  # 전체 별 개수
    half_star = (rating - full_stars) >= 0.5  # 반 별이 필요한지
    empty_stars = 5 - full_stars - int(half_star)  # 빈 별 개수

    # 별 아이콘만 살짝 위로 올리기 위한 CSS 적용
    stars_html = '<div style="font-size: 18px; color: orange; margin-top: -10px; margin-left: -8px;">'
    stars_html += '<i class="fas fa-star"></i> ' * full_stars
    if half_star:
        stars_html += '<i class="fas fa-star-half-alt"></i> '
    stars_html += '<i class="far fa-star"></i> ' * empty_stars
    stars_html += '</div>'

    return stars_html

def render_dollars(d_rating):
    full_dollars = int(d_rating)  # 전체 달러의 수
    half_dollar = int((d_rating - full_dollars) >= 0.5)  # 반 달러의 유무
    empty_dollars = 4 - full_dollars - half_dollar  # 빈 달러의 수

    # 달러 아이콘을 포함하는 HTML 문자열 생성
    
    dollars_html = '<div style="width: 200px; height: 200px; font-size: 22px; color: green; margin-top: -13px; margin-left: -6px;">'
    dollars_html += '<i class="fas fa-dollar-sign"></i> ' * full_dollars
    
    if half_dollar:
        dollars_html += '<i class="fas fa-dollar-sign" style="opacity: 0.5;"></i> '
    dollars_html += '<i class="fas fa-dollar-sign" style="opacity: 0.3;"></i> ' * empty_dollars
    dollars_html += '</div>'

    return dollars_html

