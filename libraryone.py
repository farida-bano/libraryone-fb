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

# Custom CSS for styling with background image
st.markdown("""
<style>
    .stApp {
        background-image: url("images/downliad.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.9);
        z-index: -1;
    }
    .main-header {
        font-size: 3rem !important;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #3882f6;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #ECFDF5;
        border-left: 5px solid #108981;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    .book-card {
        background-color: #f3f4f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3882f6;
        transition: transform 0.3s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .read-badge {
        background-color: #108981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-badge {
        background-color: #F87171;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .stButton>button {
        border-radius: 0.375rem !important;
    }
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
    except Exception as e:
        st.error(f"Error loading library: {str(e)}")

def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
    except Exception as e:
        st.error(f"Error saving library: {str(e)}")

def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title.strip(),
        'author': author.strip(),
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

def search_books(search_term, search_by):
    search_term = search_term.lower().strip()
    results = []
    for book in st.session_state.library:
        target = book[search_by.lower()].lower()
        if search_term in target:
            results.append(book)
    st.session_state.search_results = results

def get_library_stats():
    stats = {
        'total_books': len(st.session_state.library),
        'read_books': sum(book['read_status'] for book in st.session_state.library),
        'genres': {},
        'authors': {},
        'decades': {}
    }
    
    stats['percent_read'] = (stats['read_books'] / stats['total_books'] * 100) if stats['total_books'] > 0 else 0
    
    for book in st.session_state.library:
        # Update genre counts
        genre = book['genre']
        stats['genres'][genre] = stats['genres'].get(genre, 0) + 1
        
        # Update author counts
        author = book['author']
        stats['authors'][author] = stats['authors'].get(author, 0) + 1
        
        # Update decade counts
        decade = (book['publication_year'] // 10) * 10
        stats['decades'][decade] = stats['decades'].get(decade, 0) + 1
    
    # Sort dictionaries
    stats['genres'] = dict(sorted(stats['genres'].items(), key=lambda x: -x[1]))
    stats['authors'] = dict(sorted(stats['authors'].items(), key=lambda x: -x[1]))
    stats['decades'] = dict(sorted(stats['decades'].items()))
    
    return stats

def create_visualizations(stats):
    if stats['total_books'] > 0:
        # Read status pie chart
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Unread"],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#108981', '#f87171']
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)
    
    # Genre distribution bar chart
    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df,
            x='Genre',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig_genres.update_layout(
            title_text='Books by Genre',
            xaxis_title='Genre',
            yaxis_title='Number of Books',
            height=400
        )
        st.plotly_chart(fig_genres, use_container_width=True)
    
    # Decades line chart
    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='spline'
        )
        fig_decades.update_layout(
            title_text='Books by Publication Decade',
            xaxis_title='Decade',
            yaxis_title='Number of Books',
            height=400
        )
        st.plotly_chart(fig_decades, use_container_width=True)

# Initial library load
load_library()

# Sidebar Navigation
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_yr6xtg8o.json")
if lottie_book:
    st_lottie(lottie_book, height=150, key='book_animation')

st.session_state.current_view = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)

# Main content
st.markdown("<h1 class='main-header'>Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "Add Book":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input(
                "Publication Year",
                min_value=1000,
                max_value=datetime.now().year,
                value=2023
            )
        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Science", "Technology",
                "Romance", "Poetry", "Self-Help", "Art", "History",
                "Music", "Religion"
            ])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
        
        if st.form_submit_button(label="Add Book") and title.strip() and author.strip():
            add_book(title, author, publication_year, genre, read_status == "Read")
            if st.session_state.book_added:
                st.markdown("<div class='success-message'>Book added successfully! 📚</div>", unsafe_allow_html=True)
                st.balloons()
                st.session_state.book_added = False

elif st.session_state.current_view == "View Library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started! 📖</div>", 
                    unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                        {"Read" if book["read_status"] else "Unread"}
                    </span></p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        if remove_book(i):
                            st.rerun()
                with col2:
                    new_status = not book['read_status']
                    status_label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                    if st.button(status_label, key=f"status_{i}"):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.rerun()
        
        if st.session_state.book_removed:
            st.markdown("<div class='success-message'>Book removed successfully! ❌</div>", unsafe_allow_html=True)
            st.session_state.book_removed = False

elif st.session_state.current_view == "Search Books":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)
    
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term:")
    
    if st.button("Search", use_container_width=True) and search_term.strip():
        with st.spinner("Searching..."):
            time.sleep(0.5)
            search_books(search_term.strip(), search_by)
            if st.session_state.search_results:
                st.markdown(f"<h3>Found {len(st.session_state.search_results)} results:</h3>", 
                           unsafe_allow_html=True)
                for book in st.session_state.search_results:
                    st.markdown(f"""
                    <div class='book-card'>
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                            {"Read" if book["read_status"] else "Unread"}
                        </span></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='warning-message'>No books found matching your search. 🔍</div>", 
                           unsafe_allow_html=True)

elif st.session_state.current_view == "Library Statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to see statistics! 📊</div>", 
                   unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total_books'])
        with col2:
            st.metric("Books Read", stats['read_books'])
        with col3:
            st.metric("Percentage Read", f"{stats['percent_read']:.1f}%")
        
        create_visualizations(stats)
        
        if stats['authors']:
            st.markdown("<h3>Top Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")

# Footer
st.markdown("---")
st.markdown("Copyright © 2024 - Farida Bano Personal Library Manager", unsafe_allow_html=True)
