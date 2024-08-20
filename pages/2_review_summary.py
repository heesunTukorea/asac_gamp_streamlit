from function import *
import streamlit as st
from streamlit_folium import st_folium
import folium
import streamlit.components.v1 as components
from secrets_1 import *

# Databricks 연결
with sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=PERSONAL_ACCESS_TOKEN) as conn:
    with conn.cursor() as cursor:
        # Streamlit 앱
        st.title("Gmap 장소 추천시스템")

        # 세션 상태 초기화
        if "page" not in st.session_state:
            st.session_state.page = "main"
        if "gmap_id1" not in st.session_state:
            st.session_state.gmap_id1 = ""
        if "recommendations" not in st.session_state:
            st.session_state.recommendations = []
            st.session_state.item_recommend_list = []
            st.session_state.review_recommend_list = []

        if "selected_gmap2" not in st.session_state:
            st.session_state.selected_gmap2 = ""
#######
        

        # 메인 페이지
        if st.session_state.page == "main":
            # 사이드바 설정
            st.sidebar.title("장소 입력")
            gmap_id1 = st.sidebar.text_input("장소 입력", st.session_state.gmap_id1, key="_gmap_id1")
            st.session_state.gmap_id1 = gmap_id1

            # 랜덤 gmap_id1 선택 버튼 추가
            if st.sidebar.button("랜덤 선택"):
                query = """SELECT gmap_id FROM `hive_metastore`.`silver`.`california_meta` ORDER BY RAND() LIMIT 1"""
                cursor.execute(query)
                gmap_id1 = cursor.fetchone()[0]
                st.session_state.gmap_id1 = gmap_id1
                gmap_id1 = gmap_id1

            if gmap_id1:
                # 입력한 Gmap1에 대한 정보 조회
                query =f"""
                SELECT address,gmap_id,avg_rating,description,latitude,longitude,name,num_of_reviews,price,state,url,region,main_category 
                FROM `hive_metastore`.`silver`.`california_meta` 
                WHERE gmap_id = '{gmap_id1}'
                
                """
                cursor.execute(query)
                address,gmap_id,avg_rating,description,latitude,longitude,name,num_of_reviews,price,state,url,region,main_category = cursor.fetchone()
                review_recommend_list,recommendations = [],[]
                

                #텍스트 유사도 쿼리       
                query = f"""
                SELECT address,gmap_id,avg_rating,latitude,longitude,name,main_category
                FROM `hive_metastore`.`silver`.`california_meta`
                ORDER BY RAND() LIMIT 5
                """
                cursor.execute(query)
                similar_items = cursor.fetchall()
                review_recommend_list.extend(similar_items)
                
                
                #세션 개선

                st.session_state.review_recommend_list = review_recommend_list
                recommendations = [st.session_state.review_recommend_list]
                st.session_state.recommendations = recommendations
                
                # Streamlit에서 두 개의 열을 생성합니다. 첫 번째 열은 6의 가중치를, 두 번째 열은 4의 가중치를 가집니다.
                col1, col2 = st.columns([5, 5])

                # 첫 번째 열에서 작업을 수행합니다.
                with col1:
                    # 지정된 높이를 가진 컨테이너를 생성합니다.
                    with st.container(height=1000):
                        # 내부에 추가적인 열을 생성하여 레이아웃을 세분화합니다. 중앙의 큰 열에 주요 내용을 배치합니다.
                        col_dummy, col_main, col_dummy2 = st.columns([0.5, 8, 0.2])
                        
                        # 중앙의 열에서 작업을 수행합니다.
                        with col_main:
                            # 기본 맵 객체를 생성합니다. 지도의 중심을 지정된 위도와 경도로 설정하고, 확대 수준은 16으로 설정합니다.
                            m = folium.Map(location=[latitude, longitude], zoom_start=16)

                            # 빨간색 아이콘으로 마커를 추가합니다. 팝업과 툴팁을 설정하여 마커를 클릭하거나 호버할 때 정보를 표시합니다.
                            folium.Marker(
                                [latitude, longitude],
                                popup=f"<div style='text-align: left; color: black; font-size: 14px;'>{name}<br>{address}</div>",
                                tooltip=f"{name}",
                                icon=folium.Icon(color='red')  # 마커의 아이콘을 빨간색으로 설정합니다.
                            ).add_to(m)

                            # session_list에서 세션 정보를 순회하며 추가적인 마커들을 맵에 추가합니다.
                            for j, session_select in enumerate(recommendations):
                                # 세션별로 다른 색상을 지정합니다.
                                if j == 0:
                                    color_sel = 'green'
                                else:
                                    color_sel = 'blue'
                                
                                # 각 세션 내의 위치 정보를 순회하며 마커를 추가합니다.
                                for i, (address,gmap_id,avg_rating,latitude,longitude,name,main_category) in enumerate(session_select):
                                    folium.Marker(
                                        [latitude, longitude],
                                        popup=f"<div style='text-align: left; color: black; font-size: 14px;'>{name}<br>{address}</div>",
                                        tooltip=f"{name}",
                                        icon=folium.Icon(color=color_sel)  # 지정된 색상의 아이콘으로 마커를 생성합니다.
                                    ).add_to(m)

                            # Streamlit에서 생성된 Folium 지도를 표시합니다. 지도의 너비와 높이를 지정합니다.
                            st_folium(m, width=405, height=325, returned_objects=[])
                            with st.expander("**리뷰 요약**"):
                                st.write('리뷰요약')
                with col2:
                    with st.container(height=1000):
                    # 내부에 추가적인 열을 생성하여 레이아웃을 세분화합니다. 중앙의 큰 열에 주요 내용을 배치합니다.
                        col_dummy, col_main, col_dummy2 = st.columns([0.5, 8, 0.2])
                        
                        # 중앙의 열에서 작업을 수행합니다.
                        with col_main:
                            # 기본 맵 객체를 생성합니다. 지도의 중심을 지정된 위도와 경도로 설정하고, 확대 수준은 16으로 설정합니다.
                            m = folium.Map(location=[latitude, longitude], zoom_start=16)

                            # 빨간색 아이콘으로 마커를 추가합니다. 팝업과 툴팁을 설정하여 마커를 클릭하거나 호버할 때 정보를 표시합니다.
                            folium.Marker(
                                [latitude, longitude],
                                popup=f"<div style='text-align: left; color: black; font-size: 14px;'>{name}<br>{address}</div>",
                                tooltip=f"{name}",
                                icon=folium.Icon(color='red')  # 마커의 아이콘을 빨간색으로 설정합니다.
                            ).add_to(m)

                            # session_list에서 세션 정보를 순회하며 추가적인 마커들을 맵에 추가합니다.
                            for j, session_select in enumerate(recommendations):
                                # 세션별로 다른 색상을 지정합니다.
                                if j == 0:
                                    color_sel = 'green'
                                else:
                                    color_sel = 'blue'
                                
                                # 각 세션 내의 위치 정보를 순회하며 마커를 추가합니다.
                                for i, (address,gmap_id,avg_rating,latitude,longitude,name,main_category) in enumerate(session_select):
                                    folium.Marker(
                                        [latitude, longitude],
                                        popup=f"<div style='text-align: left; color: black; font-size: 14px;'>{name}<br>{address}</div>",
                                        tooltip=f"{name}",
                                        icon=folium.Icon(color=color_sel)  # 지정된 색상의 아이콘으로 마커를 생성합니다.
                                    ).add_to(m)

                            # Streamlit에서 생성된 Folium 지도를 표시합니다. 지도의 너비와 높이를 지정합니다.
                            st_folium(m, width=405, height=325, returned_objects=[])
                            with st.expander("**리뷰 요약**"):
                                st.write('리뷰요약')