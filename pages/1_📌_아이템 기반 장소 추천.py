from function import *
import streamlit as st
from streamlit_folium import st_folium
import folium
import streamlit.components.v1 as components
from secrets_1 import HOST, HTTP_PATH, PERSONAL_ACCESS_TOKEN

# 4.chatbot과 연결
query_params = st.query_params
chat_gmap_id = query_params.get("gmap_id", None)  # 'None'은 'gmap_id'가 없을 때 반환됩니다.
print("gmap_id", chat_gmap_id)

st.set_page_config(page_title="아이템 기반 Gmap 추천시스템", page_icon="🗺️", layout="wide")


# Databricks 연결
with sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=PERSONAL_ACCESS_TOKEN) as conn:
    with conn.cursor() as cursor:
        # Streamlit 앱
        st.title("아이템 기반 Gmap 추천시스템🌎")
        
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
        if "selected_gmap_id" not in st.session_state:
            st.session_state.selected_gmap_id = ""

        # 메인 페이지
        if st.session_state.page == "main":
            # 사이드바 설정
            st.sidebar.title("장소 입력")
            # if chat_gmap_id: 
            #     gmap_id1=chat_gmap_id
            # else: gmap_id1 = st.sidebar.text_input("장소 입력", st.session_state.gmap_id1, key="_gmap_id1")
            # st.session_state.gmap_id1 = gmap_id1
            
            if chat_gmap_id:
                # chat_gmap_id가 존재할 때
                gmap_id1 = chat_gmap_id
                query = f"""
                SELECT address1, gmap_id1, avg_rating1, description1, latitude1, longitude1, name1, num_of_reviews1, price1, state1, url1, main_category1, first_main_category1, region1, city1, hash_tag1 
                FROM `hive_metastore`.`streamlit`.`gmap_id1_info`
                WHERE gmap_id1 = '{gmap_id1}'
                """
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    # 결과가 있을 때
                    address1, gmap_id1, avg_rating1, description1, latitude1, longitude1, name1, num_of_reviews1, price1, state1, url1, main_category1, first_main_category1, region1, city1, hash_tag1 = result
                    st.session_state.gmap_id1 = gmap_id1
                    chat_gmap_id=None
                else:
                    # 결과가 없을 때
                    st.session_state.gmap_id1 = ""  # gmap_id 초기화
                    st.sidebar.write("해당 데이터는 아직 추천 결과가 존재하지 않습니다.")
                    gmap_id1 = None  # 이후 코드에서 쿼리를 수행하지 않도록 설정
            else:
                gmap_id1 = st.sidebar.text_input("장소 입력", st.session_state.gmap_id1, key="_gmap_id1")
                st.session_state.gmap_id1 = gmap_id1
            chat_gmap_id=None


            # 랜덤 gmap_id1 선택 버튼 추가
            if st.sidebar.button("🎲랜덤 선택"):
                query = """SELECT gmap_id1 FROM `hive_metastore`.`streamlit`.`gbdt_sample` ORDER BY RAND() LIMIT 1"""
                cursor.execute(query)
                gmap_id1 = cursor.fetchone()[0]
                st.session_state.gmap_id1 = gmap_id1
                gmap_id1 = gmap_id1

            if gmap_id1:
                try:
                    # 입력한 Gmap1에 대한 정보 조회
                    query = f"""
                    SELECT address1, gmap_id1, avg_rating1, description1, latitude1, longitude1, name1, num_of_reviews1, price1, state1, url1, main_category1, first_main_category1, region1, city1,hash_tag1 
                    FROM `hive_metastore`.`streamlit`.`gmap_id1_info`
                    WHERE gmap_id1 = '{gmap_id1}'
                    """
                    cursor.execute(query)
                    address1, gmap_id1, avg_rating1, description1, latitude1, longitude1, name1, num_of_reviews1, price1, state1, url1, main_category1, first_main_category1, region1,city1,hash_tag1  = cursor.fetchone()
                    st.sidebar.write(f'선택된 장소: {name1}')
                    # 추천 결과 생성
                    item_recommend_list, hybrid_recommend_list, review_recommend_list, recommendations = [], [], [], []
                    
                    # GBDT 쿼리
                    query = f"""
                    SELECT gmap_id2, prob, rank
                    FROM `hive_metastore`.`streamlit`.`gbdt_sample`
                    WHERE gmap_id1 = '{gmap_id1}'
                    ORDER BY rank DESC
                    LIMIT 5
                    """
                    cursor.execute(query)
                    gbdt_gmap2_list = cursor.fetchall()
                    gmap_id2_values = [t[0] for t in gbdt_gmap2_list]
                    gbdt_prob = [t[1] for t in gbdt_gmap2_list]
                    gbdt_rank = [str(t) for t in range(len(gbdt_gmap2_list),0,-1)]
                    gbdt_prob_dict,gbdt_rank_dict = create_gmap_id_prob_dict(gmap_id2_values, gbdt_prob,gbdt_rank)
                    
                    gmap_id2_tuple = tuple(gmap_id2_values)

                    # item2item 쿼리
                    query = f"""
                    SELECT address2,gmap_id2,avg_rating2,description2,latitude2,longitude2,name2,num_of_reviews2,price2,state2,url2,main_category2,first_main_category2,region2,city2,hash_tag2 
                    FROM `hive_metastore`.`streamlit`.`gmap_id2_info`
                    WHERE gmap_id2 in {gmap_id2_tuple}
                    LIMIT 5
                    """
                    cursor.execute(query)
                    similar_items = cursor.fetchall()
                    item_recommend_list.extend(similar_items)

                    # 하이브리드 쿼리
                    query = f"""
                    SELECT gmap_id2, prob,rank
                    FROM `hive_metastore`.`streamlit`.`hybrid_sample`
                    WHERE gmap_id1 = '{gmap_id1}'
                    ORDER BY rank DESC
                    LIMIT 5
                    """
                    cursor.execute(query)
                    gbdt_gmap2_list = cursor.fetchall()
                    gmap_id2_values = [t[0] for t in gbdt_gmap2_list]
                    hybrid_prob = [t[1] for t in gbdt_gmap2_list]
                    hybrid_rank = [str(t) for t in range(len(gbdt_gmap2_list),0,-1)]
                    hybrid_prob_dict,hybrid_rank_dict = create_gmap_id_prob_dict(gmap_id2_values, hybrid_prob,hybrid_rank)
                    gmap_id2_tuple = tuple(gmap_id2_values)

                    query = f"""
                    SELECT address2,gmap_id2,avg_rating2,description2,latitude2,longitude2,name2,num_of_reviews2,price2,state2,url2,main_category2,first_main_category2,region2,city2,hash_tag2 
                    FROM `hive_metastore`.`streamlit`.`gmap_id2_info`
                    WHERE gmap_id2 in {gmap_id2_tuple}
                    LIMIT 5
                    """
                    cursor.execute(query)
                    similar_items = cursor.fetchall()
                    
                    hybrid_recommend_list.extend(similar_items)

                    # 리뷰 텍스트 쿼리
                    query = f"""
                    SELECT gmap_id2, cosine_top4,rank
                    FROM `hive_metastore`.`streamlit`.`text_sample`
                    WHERE gmap_id1 = '{gmap_id1}'
                    ORDER BY rank DESC
                    LIMIT 5
                    """
                    cursor.execute(query)
                    gbdt_gmap2_list = cursor.fetchall()
                    gmap_id2_values = [t[0] for t in gbdt_gmap2_list]
                    review_prob = [t[1] for t in gbdt_gmap2_list]
                    review_rank = [str(t) for t in range(len(gbdt_gmap2_list),0,-1)]
                    review_prob_dict,review_rank_dict = create_gmap_id_prob_dict(gmap_id2_values, review_prob,review_rank)
                    
                    gmap_id2_tuple = tuple(gmap_id2_values)

                    query = f"""
                    SELECT address2,gmap_id2,avg_rating2,description2,latitude2,longitude2,name2,num_of_reviews2,price2,state2,url2,main_category2,first_main_category2,region2,city2,hash_tag2 
                    FROM `hive_metastore`.`streamlit`.`gmap_id2_info`
                    WHERE gmap_id2 in {gmap_id2_tuple}
                    LIMIT 5
                    """
                    cursor.execute(query)
                    similar_items = cursor.fetchall()
                    review_recommend_list.extend(similar_items)

                    total_prob = [gbdt_prob, hybrid_prob, review_prob]
                    st.session_state.item_recommend_list = item_recommend_list
                    st.session_state.review_recommend_list = review_recommend_list
                    st.session_state.hybrid_recommend_list = hybrid_recommend_list
                    recommendations = [st.session_state.item_recommend_list, st.session_state.review_recommend_list, st.session_state.hybrid_recommend_list]
                    st.session_state.recommendations = recommendations

                    
                    merged_dict = {**gbdt_prob_dict, **hybrid_prob_dict,**review_prob_dict}
                    merged_rank_dict = {**gbdt_rank_dict, **hybrid_rank_dict,**review_rank_dict}

                    first_value = list(merged_dict.keys())[0]

                    

                    # 레이아웃
                    col1, col2 = st.columns([7, 3])
                    con_size = 500

                    with col1:
                        with st.container(height=con_size):
                            col_dummy, col_main, col_dummy2 = st.columns([0.5, 8, 0.2])
                            with col_main:
                                m = folium.Map(location=[latitude1, longitude1], zoom_start=12)
                                group1 = folium.FeatureGroup(name="🟩GBDT")
                                group2 = folium.FeatureGroup(name="🟧Hybrid")
                                group3 = folium.FeatureGroup(name="🟦Review")

                                #create_marker(latitude1, longitude1, name1, address1, gmap_id1, 'red').add_to(m)
                                create_emoji_marker(latitude1, longitude1, name1, address1, gmap_id1, first_main_category1,'red','',url1).add_to(m)

                                for j, session_select in enumerate(recommendations):
                                    group = group1 if j == 0 else group2 if j == 1 else group3
                                    color = 'green' if j == 0 else 'orange' if j == 1 else 'blue'
                                    for i, (address, gmap_id, avg_rating, description, latitude, longitude, name, num_of_reviews, price, state, url, main_category, first_main_category, region,city,hash_tag ) in enumerate(session_select):
                                        #create_marker(latitude, longitude, name, address, gmap_id, color).add_to(group)
                                        g_rank = f'{merged_rank_dict.get(str(gmap_id), None)}️⃣'
                                        create_emoji_marker(latitude, longitude, name, address, gmap_id, first_main_category,color,g_rank,url).add_to(group)

                                m.add_child(group1)
                                m.add_child(group2)
                                m.add_child(group3)
                                folium.LayerControl(collapsed=False).add_to(m)
                                
                                map_data = st_folium(m, width=600, height=480)
                            
                        
                    # Keep the first red item unchanged
                    all_places = [(gmap_id1, f'🟥{name1}')]

                    # Initialize lists to hold items by color group
                    green_items = []
                    orange_items = []
                    blue_items = []

                    # Separate items into color groups
                    for index, sublist in enumerate(recommendations):
                        for r_c,item in enumerate(sublist):
                            if index < 1:  # 첫 5개 아이템 (0~4)
                                emoji = '🟩'
                                green_items.append((item[1], f'{emoji}/{merged_rank_dict.get(str(item[1]), None)}️⃣{item[6]}'))
                            elif index < 2:  # 다음 5개 아이템 (5~9)
                                emoji = '🟧'
                                orange_items.append((item[1], f'{emoji}/{merged_rank_dict.get(str(item[1]), None)}️⃣{item[6]}'))
                            else:  # 그 외 아이템
                                emoji = '🟦'
                                blue_items.append((item[1], f'{emoji}/{merged_rank_dict.get(str(item[1]), None)}️⃣{item[6]}'))

                    # Sort items within each color group by the merged_rank_dict value (ascending order)
                    green_items.sort(key=lambda x: merged_rank_dict.get(str(x[0]), float('inf')))
                    orange_items.sort(key=lambda x: merged_rank_dict.get(str(x[0]), float('inf')))
                    blue_items.sort(key=lambda x: merged_rank_dict.get(str(x[0]), float('inf')))

                    # Combine the sorted lists and append them to all_places, while keeping the first red item unchanged
                    all_places.extend(green_items + orange_items + blue_items)

                    
                    with col2:
                        with st.container(height=con_size):
                            # 선택 박스를 추가하여 사용자가 장소를 선택할 수 있게 합니다.
                            #all_places = [(gmap_id1, name1)] + [(item[1], item[6]) for sublist in recommendations for item in sublist]
                            selected_place = st.selectbox("장소 선택", all_places, format_func=lambda x: x[1])
                            
                            if selected_place:
                                st.session_state.selected_gmap_id = selected_place[0]
                            update_info_container(st.session_state.selected_gmap_id,merged_dict)
                    # import streamlit as st

                    # # 장소 리스트 초기화 및 색깔별 아이템 분류
                    # all_places = [(gmap_id1, f'🟥{name1}')]  # 초기 장소 설정 - 레드 아이템
                    # green_items = []
                    # orange_items = []
                    # blue_items = []

                    # # 각 아이템을 색깔 그룹에 할당
                    # for index, sublist in enumerate(recommendations):
                    #     for item in sublist:
                    #         if index < 1:
                    #             green_items.append((item[1], f'🟩 {item[6]}'))
                    #         elif index < 2:
                    #             orange_items.append((item[1], f'🟧 {item[6]}'))
                    #         else:
                    #             blue_items.append((item[1], f'🟦 {item[6]}'))

                    # # 모든 아이템을 하나의 리스트로 결합
                    # all_places.extend(green_items + orange_items + blue_items)

                    # # 멀티셀렉트를 사용하여 사용자가 여러 장소를 선택할 수 있도록 설정
                    # selected_places = st.multiselect("여러 장소 선택", all_places, format_func=lambda x: x[1])

                    # # 선택된 장소로부터 선택 박스 제공
                    # if selected_places:
                    #     # 선택 박스에 들어갈 선택된 장소 리스트
                    #     select_options = [(place[0], place[1]) for place in selected_places]
                    #     selected_place = st.selectbox("장소 세부 선택", select_options, format_func=lambda x: x[1])

                    #     if selected_place:
                    #         st.session_state.selected_gmap_id = selected_place[0]
                    #         update_info_container(st.session_state.selected_gmap_id, merged_dict)

                    # # 선택된 장소가 없을 경우 초기 상태 유지
                    # else:
                    #     st.write("선택된 장소가 없습니다.")
            

                    img_url = "http://wordnbow.net/wp-content/uploads/2021/01/unnamed.png"
                    title_list = ['**GBDT Model**', '**Hybrid Model**', '**Review Similarity**']
                    for idx, recommend_session in enumerate(recommendations):
                        # Sort items by descending similarity within each recommendation session
                        sorted_items = sorted(enumerate(recommend_session), key=lambda x: total_prob[idx][x[0]], reverse=True)
                        if title_list[idx] =='**Review Similarity**':
                            p_name = '유사도'
                        else:
                            p_name = 'Prob'
                        with st.expander(title_list[idx]):
                            cols = st.columns(5)
                            for i, (index, (address, gmap_id, avg_rating, description, latitude, longitude, name, num_of_reviews, price, state, url, main_category, first_main_category, region, city, hash_tag)) in enumerate(sorted_items):
                                category_emoji = get_category_emoji(first_main_category)
                                emoji_code = resize_emoji(category_emoji, font_size=80)
                                #img_resized = resize_image(img_url)
                                with cols[i % 5]:
                                    #display_image(img_resized, f"")
                                    st.write(f'{i+1}️⃣')
                                    st.markdown(emoji_code, unsafe_allow_html=True)
                                    html_code = f"""
                                    <div style='text-align: center; color: gray; font-size: 18px;'>
                                        {p_name} : {round(float(total_prob[idx][index])* 100, 2)}%<br>
                                    </div>
                                    """
                                    st.markdown(html_code, unsafe_allow_html=True)
                                    st.write_stream(stream_data(f'*Name* : [{name}]({url})'))
                                    st.write_stream(stream_data(f'*Category* : {category_emoji}{main_category}'))
                                    st.write_stream(stream_data(f'*City* : 🏙️{city}'))
                                    st.write_stream(stream_data(f'*Rating* : ⭐{avg_rating}'))
                                    st.write_stream(stream_data(f'*Adress* : 🏡{address}'))
                except:
                    st.sidebar.write('해당되는 장소 정보가 없습니다')
                




                # # 메타정보 페이지
                # elif st.session_state.page == "메타정보":
                #     if st.button("메인 페이지로 이동"):
                #         change_page("main")
                #     meta_info(conn, cursor)