import streamlit as st

def load_css():
    """Load custom CSS styles for the application"""
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            margin-top: 10px;
            background-color: #FF0000;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #CC0000;
        }
        .download-link {
            display: inline-block;
            padding: 12px 24px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            width: 100%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .download-link:hover {
            background-color: #45a049;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            text-decoration: none;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True) 