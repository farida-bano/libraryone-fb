import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.graph_objects as go

# --- Set Page Configuration ---
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Apply Background Image ---
def set_background(image_file):
    """Sets a background image for the Streamlit app."""
    page_bg_img = f"""
    <style>
    .stApp {{
        background: url({image_file});
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Call the function to set background
set_background("farida.jpg")  # Make sure the image is in the same directory

# --- Constants ---
LIBRARY_FILE = "library.json"

# --- Ensure Required Files Exist ---
def initialize_library():
    """Ensures that the library.json file exists and is correctly formatted."""
    if not os.path.exists(LIBRARY_FILE) or os.stat(LIBRARY_FILE).st_size == 0:
        with open(LIBRARY_FILE, "w") as f:
            json.dump([], f)
    else:
        try:
            with open(LIBRARY_FILE, "r") as file:
                json.load(file)  # Try loading JSON to check validity
        except json.JSONDecodeError:
            with open(LIBRARY_FILE, "w") as f:
                json.dump([], f)  # Reset to empty list if invalid

initialize_library()

# --- Load and Save Library Data ---
def load_library():
    """Loads books from JSON file into session state."""
    try:
        with open(LIBRARY_FILE, "r") as file:
            st.session_state.library = json.load(file)
    except Exception as e:
        st.error(f"Error loading library: {e}")
        st.session_state.library = []

def save_library():
    """Saves session state library to JSON file."""
    try:
        with open(LIBRARY_FILE, "w") as file:
            json.dump(st.session_state.library, file, indent=4)
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Load library at startup
if "library" not in st.session_state:
    st.session_state.library = []
    load_library()

# --- Add a Book ---
def add_book(title, author, year, genre, read_status):
    """Adds a new book to the library."""
    new_book = {
        "title": title,
        "author": author,
        "publication_year": year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(new_book)
    save_library()
    st.success("Book added successfully!")
    st.balloons()

# --- Remove a Book ---
def remove_book(index):
    """Removes a book from the library."""
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.success("Book removed successfully!")
        st.experimental_rerun()

# --- Search Books ---
def search_books(term, search_by):
    """Searches for books based on title, author, or genre."""
    term = term.lower()
    return [book for book in st.session_state.library if term in book[search_by].lower()]

# --- Sidebar Navigation ---
st.sidebar.header("📚 Navigation")
nav_option = st.sidebar.radio(
    "Select an option:",
    ["🏠 View Library", "➕ Add Book", "🔍 Search Books", "📊 Library Statistics"]
)

# --- Main Content ---
st.title("📚 Personal Library Manager")

if nav_option == "➕ Add Book":
    st.subheader("➕ Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Book Title", max_chars=100)
        author = st.text_input("Author", max_chars=100)
        year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=2023)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "History", "Romance", "Poetry"])
        read_status = st.radio("Read Status", ["Read ✅", "Unread 📖"])
        
        if st.form_submit_button("Add Book"):
            if title and author:
                add_book(title, author, year, genre, read_status == "Read ✅")
            else:
                st.warning("Please fill in all fields!")

elif nav_option == "🏠 View Library":
    st.subheader("📚 Your Library")
    if not st.session_state.library:
        st.info("No books found. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.expander(f"{book['title']} by {book['author']}"):
                st.write(f"**Publication Year:** {book['publication_year']}")
                st.write(f"**Genre:** {book['genre']}")
                st.write(f"**Status:** {'✅ Read' if book['read_status'] else '📖 Unread'}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        remove_book(i)
                with col2:
                    if st.button("Toggle Read Status", key=f"toggle_{i}"):
                        st.session_state.library[i]['read_status'] = not book['read_status']
                        save_library()
                        st.experimental_rerun()

elif nav_option == "🔍 Search Books":
    st.subheader("🔍 Search Books")
    search_by = st.selectbox("Search by", ["title", "author", "genre"])
    search_term = st.text_input("Enter search term")
    
    if st.button("Search"):
        if search_term:
            results = search_books(search_term, search_by)
            if results:
                st.success(f"Found {len(results)} result(s).")
                for book in results:
                    st.write(f"📖 **{book['title']}** by {book['author']} ({book['publication_year']})")
            else:
                st.warning("No matching books found.")

elif nav_option == "📊 Library Statistics":
    st.subheader("📊 Library Statistics")
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    unread_books = total_books - read_books
    
    st.metric("Total Books", total_books)
    st.metric("Books Read", read_books)
    st.metric("Books Unread", unread_books)

    if total_books:
        fig = go.Figure(data=[go.Pie(labels=["Read", "Unread"], values=[read_books, unread_books], hole=0.4)])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No books in library to generate statistics.")

st.write("©️ 2024 Personal Library Manager | Developed by Farida Bano")
