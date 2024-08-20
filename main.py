import streamlit as st
from PIL import Image




st.title("LLM과 협업 필터링을 이용한 구글 맵 추천 시스템 개발")




x2 = st.expander('프로젝트 소개')
x2.write('''
구글 맵의 텍스트 리뷰, 평점, 메타 정보를 활용하여 개인화된 추천을 제공하는 챗봇 개발 프로젝트. Item to Item, User to Item 두 종류의 협업 필터링과 LLM을 보완한 RAG기법을 통합해 사용자에게 맞춤형 서비스를 제공하고자 함.

''')

with st.sidebar:
    st.write("목록")