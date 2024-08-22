
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
            st.session_state.hybrid_recommend_list = []

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
                query = """SELECT gmap_id1 FROM `hive_metastore`.`streamlit`.`gbdt_sample` ORDER BY RAND() LIMIT 1"""
                cursor.execute(query)
                gmap_id1 = cursor.fetchone()[0]
                st.session_state.gmap_id1 = gmap_id1
                gmap_id1 = gmap_id1

            if gmap_id1:
                # 입력한 Gmap1에 대한 정보 조회
                query =f"""
                SELECT address1,gmap_id1,avg_rating1,description1,latitude1,longitude1,name1,num_of_reviews1,price1,state1,url1,main_category1,first_main_category1,region1 
                FROM `hive_metastore`.`streamlit`.`gmap_id1_info`
                WHERE gmap_id1 = '{gmap_id1}'
                
                """
                cursor.execute(query)
                address1,gmap_id1,avg_rating1,description1,latitude1,longitude1,name1,num_of_reviews1,price1,state1,url1,main_category1,first_main_category1,region1  = cursor.fetchone()

                
                # text candidate 쿼리
                
                # 추천 결과 생성 리스트
                item_recommend_list,hybrid_recommend_list,review_recommend_list,recommendations = [],[],[],[]
                
                #------------------------------------------------------------------------------------
                #gbdt 쿼리
                query = f"""
                SELECT gmap_id2, prob
                FROM `hive_metastore`.`streamlit`.`gbdt_sample`
                WHERE gmap_id1 = '{gmap_id1}'
                ORDER BY rank DESC
                LIMIT 5
                """
                cursor.execute(query)
                gbdt_gmap2_list = cursor.fetchall()
                # gmap_id2 값만 추출
                gmap_id2_values = [t[0] for t in gbdt_gmap2_list]
                gbdt_prob = [t[1] for t in gbdt_gmap2_list]

                # SQL 쿼리에 사용할 수 있도록 튜플 형태로 변환
                gmap_id2_tuple = tuple(gmap_id2_values)

                #item2item 쿼리         
                query = f"""
                SELECT address2,gmap_id2,avg_rating2,description2,latitude2,longitude2,name2,num_of_reviews2,price2,state2,url2,main_category2,first_main_category2,region2
                FROM `hive_metastore`.`streamlit`.`gmap_id2_info`
                WHERE gmap_id2 in {gmap_id2_tuple}
                LIMIT 5
                """
                cursor.execute(query)
                similar_items = cursor.fetchall()
                item_recommend_list.extend(similar_items)

                #--------------------------------------------------------------------------
                #하이브리드 쿼리       
                query = f"""
                SELECT gmap_id2, prob
                FROM `hive_metastore`.`streamlit`.`hybrid_sample`
                WHERE gmap_id1 = '{gmap_id1}'
                ORDER BY rank DESC
                LIMIT 5
                """
                cursor.execute(query)
                gbdt_gmap2_list = cursor.fetchall()
                # gmap_id2 값만 추출
                gmap_id2_values = [t[0] for t in gbdt_gmap2_list]
                hybrid_prob = [t[1] for t in gbdt_gmap2_list]

                # SQL 쿼리에 사용할 수 있도록 튜플 형태로 변환
                gmap_id2_tuple = tuple(gmap_id2_values)

                #gmap_id1 추출        
                query = f"""
                SELECT address2,gmap_id2,avg_rating2,description2,latitude2,longitude2,name2,num_of_reviews2,price2,state2,url2,main_category2,first_main_category2,region2
                FROM `hive_metastore`.`streamlit`.`gmap_id2_info`
                WHERE gmap_id2 in {gmap_id2_tuple}
                LIMIT 5
                """
                cursor.execute(query)
                similar_items = cursor.fetchall()
                hybrid_recommend_list.extend(similar_items)
                
                #-----------------------------------------------------------------------------------
                #리뷰 텍스트 쿼리       
                query = f"""
                SELECT gmap_id2, cosine_top4
                FROM `hive_metastore`.`streamlit`.`text_sample`
                WHERE gmap_id1 = '{gmap_id1}'
                ORDER BY rank DESC
                LIMIT 5
                """
                cursor.execute(query)
                gbdt_gmap2_list = cursor.fetchall()
                # gmap_id2 값만 추출
                gmap_id2_values = [t[0] for t in gbdt_gmap2_list]
                reveiw_prob = [t[1] for t in gbdt_gmap2_list]

                # SQL 쿼리에 사용할 수 있도록 튜플 형태로 변환
                gmap_id2_tuple = tuple(gmap_id2_values)

                #gmap_id1 추출        
                query = f"""
                SELECT address2,gmap_id2,avg_rating2,description2,latitude2,longitude2,name2,num_of_reviews2,price2,state2,url2,main_category2,first_main_category2,region2
                FROM `hive_metastore`.`streamlit`.`gmap_id2_info`
                WHERE gmap_id2 in {gmap_id2_tuple}
                LIMIT 5
                """
                cursor.execute(query)
                similar_items = cursor.fetchall()
                review_recommend_list.extend(similar_items)
                
                total_prob = [gbdt_prob,hybrid_prob,reveiw_prob]
                #세션 개선
                st.session_state.item_recommend_list = item_recommend_list
                st.session_state.review_recommend_list = review_recommend_list
                st.session_state.hybrid_recommend_list = hybrid_recommend_list
                recommendations = [st.session_state.item_recommend_list,st.session_state.review_recommend_list,st.session_state.hybrid_recommend_list]
                st.session_state.recommendations = recommendations
                
                # Streamlit에서 두 개의 열을 생성합니다. 첫 번째 열은 6의 가중치를, 두 번째 열은 4의 가중치를 가집니다.
                col1, col2 = st.columns([6, 4])

                # 첫 번째 열에서 작업을 수행합니다.
                with col1:
                    # 지정된 높이를 가진 컨테이너를 생성합니다.
                    with st.container(height=350):
                        # 내부에 추가적인 열을 생성하여 레이아웃을 세분화합니다. 중앙의 큰 열에 주요 내용을 배치합니다.
                        col_dummy, col_main, col_dummy2 = st.columns([0.5, 8, 0.2])
                        
                        # 중앙의 열에서 작업을 수행합니다.
                        with col_main:
                            # 기본 맵 객체를 생성합니다. 지도의 중심을 지정된 위도와 경도로 설정하고, 확대 수준은 16으로 설정합니다.
                            m = folium.Map(location=[latitude1, longitude1], zoom_start=16)

                            # 빨간색 아이콘으로 마커를 추가합니다. 팝업과 툴팁을 설정하여 마커를 클릭하거나 호버할 때 정보를 표시합니다.
                            folium.Marker(
                                [latitude1, longitude1],
                                popup=f"<div style='text-align: left; color: black; font-size: 14px;'>{name1}<br>{address1}</div>",
                                tooltip=f"{name1}",
                                icon=folium.Icon(color='red')  # 마커의 아이콘을 빨간색으로 설정합니다.
                            ).add_to(m)

                            # session_list에서 세션 정보를 순회하며 추가적인 마커들을 맵에 추가합니다.
                            for j, session_select in enumerate(recommendations):
                                # 세션별로 다른 색상을 지정합니다.
                                if j == 0:
                                    color_sel = 'green'
                                elif j==1:
                                    color_sel = 'orange'
                                else:
                                    color_sel = 'blue'
                                
                                # 각 세션 내의 위치 정보를 순회하며 마커를 추가합니다.
                                for i, (address,gmap_id,avg_rating,description,latitude,longitude,name,num_of_reviews,price,state,url,main_category,first_main_category,region) in enumerate(session_select):
                                    folium.Marker(
                                        [latitude, longitude],
                                        popup=f"<div style='text-align: left; color: black; font-size: 14px;'>{name}<br>{address}</div>",
                                        tooltip=f"{name}",
                                        icon=folium.Icon(color=color_sel)  # 지정된 색상의 아이콘으로 마커를 생성합니다.
                                    ).add_to(m)

                            # Streamlit에서 생성된 Folium 지도를 표시합니다. 지도의 너비와 높이를 지정합니다.
                            st_folium(m, width=405, height=325, returned_objects=[])
                #장소 세부정보 화면
                with col2:
                    with st.container(height=350):
                        st.write(f'**장소명**: {name}')
                        st.write(f'**카테고리**: {main_category}')
                        st.write(f'**지역명**: {region}')
                        col3, col4 = st.columns([2, 8])
                        with col3:
                            st.write(f'**별점**:') 
                            st.write(f'**가격**:')
                        with col4:
                            # 별점
                            rating = avg_rating
                            star_html = f"""
                                <head>
                                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
                                </head>{render_stars(rating)}
                                """
                            components.html(star_html, height=20)
                        
                            #달러
                            price = price
                            dollars_html = f"""
                                <head>
                                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
                                </head>{render_dollars(float(3.5))}
                                """
                            components.html(dollars_html, height=22)
                img_url = "http://wordnbow.net/wp-content/uploads/2021/01/unnamed.png"
                # 추천 결과 출력
                # with st.expander("**Item2Item**"):
                #     cols = st.columns(5)
                #     for i, (address,gmap_id,avg_rating,latitude,longitude,name,main_category) in enumerate(st.session_state.item_recommend_list):
                #         img_resized = resize_image(img_url)
                #         with cols[i % 5]:
                #             if st.button(f"추천상품: {gmap2}", key=f"image_{i}"):
                #                 st.session_state.selected_gmap2 = gmap2
                #                 change_page("메타정보")
                #             display_image(img_resized, f"유사도: {cosine_similarity:.3f}")
                title_list = ['**Item2Item Model**','**Hybrid Model**','**Review Simiarity**']
                for idx,recommend_session in enumerate(recommendations):
                    with st.expander(title_list[idx]):
                        cols = st.columns(5)
                        for i, (address,gmap_id,avg_rating,description,latitude,longitude,name,num_of_reviews,price,state,url,main_category,first_main_category,region) in enumerate(recommend_session):
                            img_resized = resize_image(img_url)

                            with cols[i % 5]:
                                display_image(img_resized, f"")
                                html_code = f"""
                                <div style='text-align: center; color: gray; font-size: 18px;'>
                                    유사도: {round(float(total_prob[idx][i]),4)*100}%<br>
                                    Name: {name}<br>
                                    
                                </div>
                                """
    #Category: {main_category}
                                st.markdown(html_code, unsafe_allow_html=True)
                                



        # # 메타정보 페이지
        # elif st.session_state.page == "메타정보":
        #     if st.button("메인 페이지로 이동"):
        #         change_page("main")
        #     meta_info(conn, cursor)