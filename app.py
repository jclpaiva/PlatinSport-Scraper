import os
import re
import time
import psutil
import keyboard
import unicodedata
import pandas as pd
import streamlit as st

from io import BytesIO
from datetime import datetime
from utils.export import create_m3u
from streamlit_searchbox import st_searchbox
from utils.scraper import scrape_platinsport
from utils.image_utils import create_clickable_icon
from utils.url_utils import get_platinsport_match_url

# Initialize session state for reactive updates
if 'original_table' not in st.session_state:
    st.session_state.original_table = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'search_term' not in st.session_state:
    st.session_state.search_term = ''

def create_flexible_search_pattern(searchterm: str):
    """
    Create a flexible regex pattern that handles dots and spaces precisely
    
    Args:
        searchterm (str): Raw search input
    
    Returns:
        str: Flexible regex pattern
    """
    # Normalize the search term
    normalized_term = unicodedata.normalize('NFKD', searchterm.lower().strip())
    
    # Escape special regex characters
    escaped_term = re.escape(normalized_term)
    
    # Replace escaped dot with flexible dot pattern
    # This allows optional spaces around the dot
    flexible_pattern = escaped_term.replace(r'\.', r'\.\s*')
    
    return flexible_pattern

def search_matches(searchterm: str, **kwargs):
    """
    Search function for matches with auto-filtering
    
    Args:
        searchterm (str): Search term input by user
        **kwargs: Additional keyword arguments passed by st_searchbox
    
    Returns:
        list: Filtered matches or empty list
    """
    if not searchterm or st.session_state.original_table is None:
        return []
    
    # Create flexible search pattern
    search_pattern = create_flexible_search_pattern(searchterm)
    
    # Normalize table columns for consistent matching
    matches = st.session_state.original_table[
        (st.session_state.original_table['Match'].str.normalize('NFKD').str.lower().str.contains(search_pattern, case=False, regex=True, na=False)) |
        (st.session_state.original_table['Channel'].str.normalize('NFKD').str.lower().str.contains(search_pattern, case=False, regex=True, na=False))
    ]
    
    # Store search results in session state
    st.session_state.search_results = matches.to_dict('records')
    
    # Return match names for dropdown
    return []  # Return empty list to prevent dropdown
    
    # Create flexible search pattern
    search_pattern = create_flexible_search_pattern(searchterm)
    
    # Normalize table columns for consistent matching
    matches = st.session_state.original_table[
        (st.session_state.original_table['Match'].str.normalize('NFKD').str.lower().str.contains(search_pattern, case=False, regex=True, na=False)) |
        (st.session_state.original_table['Channel'].str.normalize('NFKD').str.lower().str.contains(search_pattern, case=False, regex=True, na=False))
    ]
    
    # Store search results in session state
    st.session_state.search_results = matches.to_dict('records')
    
    # Return match names for dropdown
    return []  # Return empty list to prevent dropdown

def apply_search_filter(selected_match=None):
    """
    Apply search filter based on selected match or search results
    
    Args:
        selected_match (str, optional): Selected match from dropdown
    """
    if selected_match:
        # If a specific match is selected
        st.session_state.filtered_df = st.session_state.original_table[
            (st.session_state.original_table['Match'] == selected_match) | 
            (st.session_state.original_table['Channel'] == selected_match)
        ]
    elif st.session_state.search_results:
        # If search results exist but no specific match selected
        st.session_state.filtered_df = pd.DataFrame(st.session_state.search_results)
    else:
        # If no results, show original table
        st.session_state.filtered_df = st.session_state.original_table

# Add custom CSS to completely remove any dropdown elements
st.markdown("""
<style>
    /* Aggressive dropdown removal */
    .stSelectbox, 
    .stSearchbox > div > div > div > div,
    .stSearchbox-dropdown {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    
    /* Ensure input field remains */
    .stSearchbox > div > div > div > input {
        display: block !important;
        visibility: visible !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: left; margin-top: -3.5rem'><i>PlatinSport</i> Matches <span style='color: #4A90E2'>Scraper</span> ⚽</h1>", unsafe_allow_html=True)

st.markdown("""
<style>
    .stSuccess { padding: 2rem !important; }
    .stMarkdown { font-size: 12px !important; }
    th {
        font-size: 1rem !important;
        font-family: "Source Sans Pro", sans-serif !important;
        background-color: #d4ac0d !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 1 !important;
        color: black !important;
    }
    td { font-size: 12px !important; }
    td:nth-child(1), th:nth-child(1) { text-align: left !important; }
    td:nth-child(2), th:nth-child(2) { text-align: left !important; }
    td:nth-child(3), th:nth-child(3) { text-align: center !important; }
    .scrollable-table {
        height: 340px;
        overflow-y: auto;
        border: 1px solid #ddd;
    }
    .scrollable-table table {
        width: 100%;
        border-collapse: collapse;
    }
</style>
""", unsafe_allow_html=True)

match_url = get_platinsport_match_url()
if match_url:
    st.write(f"Derived Match URL: {match_url}")
    
    data, schedule_date = scrape_platinsport(match_url)
    if isinstance(data, pd.DataFrame) and not data.empty:
        # Parse the scraped date and reformat it
        try:
            parsed_date = datetime.strptime(schedule_date.split('SCHEDULE')[0].strip(), "%A %dTH %B %Y")
            formatted_date = parsed_date.strftime("%A %d %B %Y (UTC)")
            st.success(f"Matches successfully scraped!  \u2003 {formatted_date}")
        except ValueError:
            st.error("Failed to parse the schedule date format.")
        
    
        # Create display table if not already in session state
        if st.session_state.original_table is None:
            display_df = data.copy()
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "ace_48.png")
            display_df['AceLink'] = display_df['AceStream Link'].apply(
                lambda x: create_clickable_icon(x, icon_path) if pd.notna(x) else ""
            )
            
            st.session_state.original_table = pd.DataFrame({
                'Match': display_df['Match'],
                'Channel': display_df['Channel'],
                'AceLink': display_df['AceLink']
            })
            st.session_state.filtered_df = st.session_state.original_table

        # Sidebar search with dynamic updates
        with st.sidebar:
            # Searchbox with term persistence
            selected_match = st_searchbox(
                search_matches,
                key="match_searchbox",
                placeholder="Search matches...",
                default_value=st.session_state.search_term,  # Use session state as default
                label_visibility='collapsed'
            )

            # Update search term in session state
            st.session_state.search_term = st.session_state.match_searchbox if hasattr(st.session_state, 'match_searchbox') else ''

            # Apply search filter
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
    else:
        st.error("No match data found.")
else:
    st.error("Failed to retrieve match URL from the homepage.")

exit_app = st.sidebar.button("Exit", type="primary")
if exit_app:
    time.sleep(2)
    keyboard.press_and_release('ctrl+w')
    pid = os.getpid()
    p = psutil.Process(pid)
    p.terminate()
    st.stop()