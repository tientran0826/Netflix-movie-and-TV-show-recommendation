import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import pickle as p
import requests
import json
import base64
from PIL import Image

load_dotenv()
API_KEY = os.getenv('api_key')
session = requests.Session()

def get_infor_movie(title):
    url = "https://api.apilayer.com/unogs/search/titles"

    params={
        'title':title,
        'limit': 1
    }
    headers= {
        'apikey': API_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }

    response = session.request("GET", url, headers=headers,params=params,stream=True)
    data = json.loads(response.text)
    results = data["results"]
    try:
        result = results[0]
        if result["title"] == title:
            img_link = result["img"]
        else:
            img_link = Image.open('imgs/poster-holder.jpg')
    except:
            img_link = Image.open('imgs/poster-holder.jpg')
    return img_link

def recommend_movies(selected_movie,movies_list,sim_scores):
    indices = pd.Series(movies_list.index, index=movies_list['title'])
    idx = indices[selected_movie]
    sim_score_results = pd.DataFrame(enumerate(sim_scores[idx]),columns = ['index','sim_score'])
    sim_score_results.sort_values(by = 'sim_score',ascending=False,inplace=True,ignore_index=True)
    index_results = sim_score_results['index'].iloc[1:6]
    return movies_list.iloc[index_results]['title']

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

def read_files():
    movies_list = p.load(open('model/movie_list.pkl','rb'))
    cosine_sim = p.load(open('model/similarity.pkl','rb'))
    return (movies_list,cosine_sim)

def create_input_box(movies_list,cosine_sim):
    selected_movie = st.selectbox(
        'Select a movie from the dropdown',
        movies_list['title'])

    if st.button('Get Recommendation'):
        img_link = get_infor_movie(selected_movie)
        st.header("Selected Movie")
        col1, _, _, _, _ = st.columns(5)
        with col1:
            st.image(img_link,caption = selected_movie)

        rc_movies = recommend_movies(selected_movie,movies_list,cosine_sim)
        titles = [title for _,title in rc_movies.items()]
        st.header("Suggest for you")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            img_link = get_infor_movie(titles[0])
            st.image(img_link,caption = titles[0])

        with col2:
            img_link = get_infor_movie(titles[1])
            st.image(img_link,caption = titles[1])

        with col3:
            img_link = get_infor_movie(titles[2]) 
            st.image(img_link,caption = titles[2])
        with col4:
            img_link = get_infor_movie(titles[3])
            st.image(img_link,caption = titles[3])

        with col5:
            img_link = get_infor_movie(titles[4])
            st.image(img_link,caption = titles[4])

def create_footer():
    footer= """
        <style>
            footer {visibility: hidden;}
            .custom_footer{
                position: fixed;
                bottom: 0px;
                width: 100%;
            }
        </style>
        <div class = 'custom_footer'>
            <p> P4DS Project <a href = "https://github.com/tientran0826/content-based-movie-recommendation"> Github </p>

        </div>
    """

    st.markdown(footer, unsafe_allow_html=True)

if __name__ == '__main__':
    st.set_page_config(
        page_title="Netflix TV shows and Movies - Movies/Series Recommendation",
        page_icon= Image.open("imgs/icon.png"),
        layout="centered",
        initial_sidebar_state="auto",
        menu_items={
            'About': "Project Python For Data Science\nhttps://github.com/tientran0826/content-based-movie-recommendation"
            }
    )
    add_bg_from_local("imgs/bkg.jpg")
    st.title("Movie Recommendation (Content-based)")
    movies_list, cosine_sim = read_files()
    create_input_box(movies_list, cosine_sim)
    create_footer()


