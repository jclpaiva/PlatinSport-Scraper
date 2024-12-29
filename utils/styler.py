def get_css():
    return """
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
    
    /* Table styling */
    .stSuccess { padding: 2rem !important; }
    .stMarkdown { font-size: 11px !important; }
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
    /* Add CSS for flag images */
    .country-flag {
        width: 14px;
        height: 14px;
        vertical-align: middle;
        margin-right: 5px;
        flex-shrink: 0;
        display: inline-block;
    }
    """
