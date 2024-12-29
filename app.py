import os
import re
import psutil
import keyboard
import pandas as pd
import streamlit as st

from io import BytesIO
from datetime import datetime
from streamlit_searchbox import st_searchbox
from utils.styler import get_css
from utils.export import create_m3u
from utils.scraper import scrape_platinsport
from utils.image import create_clickable_icon
from utils.url import get_platinsport_match_url
from utils.search import create_flexible_search_pattern, search_matches

# Initialize session state for reactive updates
if 'original_table' not in st.session_state:
    st.session_state.original_table = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'search_term' not in st.session_state:
    st.session_state.search_term = ''


def load_css(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject CSS
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: left; margin-top: -3.5rem'><i>PlatinSport</i> Matches <span style='color: #4A90E2'>Scraper</span> ⚽</h1>", unsafe_allow_html=True)

def apply_search_filter(selected_match=None):
    if selected_match:
        st.session_state.filtered_df = st.session_state.original_table[
            (st.session_state.original_table['Match'] == selected_match) | 
            (st.session_state.original_table['Channel'] == selected_match)
        ]
    elif st.session_state.search_results:
        st.session_state.filtered_df = pd.DataFrame(st.session_state.search_results)
    else:
        st.session_state.filtered_df = st.session_state.original_table

match_url = get_platinsport_match_url()
if match_url:
    st.write(f"Derived Match URL: {match_url}")
    
    data, schedule_date = scrape_platinsport(match_url)
    if isinstance(data, pd.DataFrame) and not data.empty:
        st.success(f"Matches successfully scraped!  \u2003 {schedule_date}")
        
        # Create display table if not already in session state
        if st.session_state.original_table is None:
            display_df = data.copy()
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "ace_48.png")
            display_df['AceLink'] = display_df['AceStream Link'].apply(
                lambda x: create_clickable_icon(x, icon_path) if pd.notna(x) else ""
            )
            # Add country flag to the Channel column
            display_df['Channel'] = display_df.apply(
                lambda row: f'<img src="https://www.platinsport.com/wp-content/uploads/2023/12/{row["CountryCode"].lower()}.png" class="country-flag" alt="{row["CountryCode"]}">{row["Channel"]}', 
                axis=1
            )   
            
            st.session_state.original_table = pd.DataFrame({
                'Match': display_df['Match'],
                'Channel': display_df['Channel'],
                'AceLink': display_df['AceLink']
            })
            st.session_state.filtered_df = st.session_state.original_table

        # Sidebar search with dynamic updates
        with st.sidebar:
            selected_match = st_searchbox(
                search_matches,
                key="match_searchbox",
                placeholder="Search matches...",
                default_value=st.session_state.search_term,
                label_visibility='collapsed'
            )

            st.session_state.search_term = st.session_state.match_searchbox if hasattr(st.session_state, 'match_searchbox') else ''
            apply_search_filter(selected_match)

            if st.session_state.filtered_df.empty:
                st.warning("No matches found")
                st.session_state.filtered_df = st.session_state.original_table

        # Display filtered table
        st.markdown(f"""
            <div class="scrollable-table">
                {st.session_state.filtered_df.to_html(escape=False, index=False)}
            </div>
        """, unsafe_allow_html=True)

        # Export options
        st.sidebar.write("---")
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False, sheet_name="Matches")
        excel_buffer.seek(0)
        st.sidebar.download_button(
            label="Download as Excel",
            data=excel_buffer,
            file_name=f"matches_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        m3u_content = create_m3u(data)
        st.sidebar.download_button(
            label="Download as M3U",
            data=m3u_content,
            file_name=f"matches_{datetime.now().strftime('%Y-%m-%d')}.m3u",
            mime="text/plain"
        )

        # Exit button
        exit_app = st.sidebar.button("Exit", type="primary")
        if exit_app:
            keyboard.press_and_release('ctrl+w')
            pid = os.getpid()
            p = psutil.Process(pid)
            p.terminate()
            st.stop()
    else:
        st.error("No match data found.")
else:
    st.error("Failed to retrieve match URL from the homepage.")