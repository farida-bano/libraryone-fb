import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 3rem !important; font-weight: 600; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
    .sub-header { font-size: 1.8rem !important; color: #3882f6; font-weight: 600; margin-bottom: 1rem; }
    .success-message { padding: 1rem; background-color: #ECFDF5; border-left: 5px solid #1f2937; border-radius: 0.375rem; margin-bottom: 1rem; }
    .warning-message { padding: 1rem; background-color: #fef3c7; border-left: 5px solid #f59e0b; border-radius: 0.375rem; margin-bottom: 1rem; }
    .book-card { background-color: #f3f4f6; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; border-left: 5px solid #3882f6; transition: transform 0.3s ease; }
    .book-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .read-badge { background-color: #108981; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.875rem; font-weight: 600; }
    .unread-badge { background-color: #F87171; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.875rem; font-weight: 600; }
    .stButton>button { border-radius: 0.375rem !important; }
    .stApp { background-image: url("https://images.unsplash.com/photo-1495446815901-a7297e633e8d"); background-size: cover; background-position: center; }
    .main .block-container { background-color: rgba(255, 255, 255, 0.95); padding: 3rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2); }
</style>
""", unsafe_allow_html=True)

# Functions
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def save_library():
    with open('library.json', 'w') as file:
        json.dump(st.session_state.library, file, indent=4)

def load_library():
    if os.path.exists('library.json'):
        try:
            with open('library.json', 'r') as file:
                data = file.read()
                st.session_state.library = json.loads(data) if data else []
        except json.JSONDecodeError:
            st.session_state.library = []
    else:
        st.session_state.library = []

def add_book(title, author, publication_year, genre, read_status):
    st.session_state.library.append({
        'title': title.strip(),
        'author': author.strip(),
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_library()
    st.success("✅ Book added successfully!")
    st.rerun()

def remove_book(index):
    del st.session_state.library[index]
    save_library()
    st.success("🗑️ Book removed successfully!")
    st.rerun()

# Load Library Data
if 'library' not in st.session_state:
    load_library()

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center;'>📚 Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_yr6xtg8o.json")
if lottie_book:
    st_lottie(lottie_book, height=150, key='book_animation')

page = st.sidebar.radio("Choose an option:", ["📚 View Library", "➕ Add Book"])

# Main
st.markdown("<h1 class='main-header'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

if page == "➕ Add Book":
    st.markdown("<h2 class='sub-header'>➕ Add New Book</h2>", unsafe_allow_html=True)
    
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("📖 Book Title")
            author = st.text_input("✍️ Author")
            publication_year = st.number_input("📅 Publication Year", min_value=1000, max_value=datetime.now().year, value=2023)
        with col2:
            genre = st.selectbox("📚 Genre", ["Fiction", "Non-Fiction", "Technology", "History", "Self-Help"])
            read_status = st.radio("✅ Read Status", ["Read", "Unread"], horizontal=True)
        
        if st.form_submit_button(label="➕ Add Book"):
            add_book(title, author, publication_year, genre, read_status == "Read")

elif page == "📚 View Library":
    st.markdown("<h2 class='sub-header'>📚 Your Library Collection</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.warning("📭 Your library is empty. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.container():
                st.markdown(f"""
                <div class='book-card'>
                    <h3>📖 {book['title']}</h3>
                    <p><strong>✍️ Author:</strong> {book['author']}</p>
                    <p><strong>📅 Published:</strong> {book['publication_year']}</p>
                    <p><strong>📚 Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                        {"✅ Read" if book["read_status"] else "📖 Unread"}
                    </span></p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        remove_book(i)
                with col2:
                    new_status = not book['read_status']
                    if st.button("✅ Toggle Read Status", key=f"status_{i}"):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.rerun()          
