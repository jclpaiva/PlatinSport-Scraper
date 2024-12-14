import re
import unicodedata
import pandas as pd
import streamlit as st

def create_flexible_search_pattern(searchterm: str) -> str:
    normalized_term = unicodedata.normalize('NFKD', searchterm.lower().strip())
    escaped_term = re.escape(normalized_term)
    flexible_pattern = escaped_term.replace(r'\.', r'\.\s*')
    return flexible_pattern

def search_matches(searchterm: str, **kwargs):
    if not searchterm or st.session_state.original_table is None:
        return []
    
    search_pattern = create_flexible_search_pattern(searchterm)
    
    matches = st.session_state.original_table[
        (st.session_state.original_table['Match'].str.normalize('NFKD').str.lower().str.contains(search_pattern, case=False, regex=True, na=False)) |
        (st.session_state.original_table['Channel'].str.normalize('NFKD').str.lower().str.contains(search_pattern, case=False, regex=True, na=False))
    ]
    
    st.session_state.search_results = matches.to_dict('records')
    return []