import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

# Update the CountryCodeTranslator class
class CountryCodeTranslator:
    """Handles country code translations for specific cases."""
    COUNTRY_CODE_MAPPING = {
        'TR': 'tr',  # Keep the -1 suffix
    }

    @classmethod
    def translate(cls, code: str) -> str:
        """Translate country codes according to mapping."""
        # If not in mapping, return the uppercase code
        return cls.COUNTRY_CODE_MAPPING.get(code.upper(), code.upper())

    @staticmethod
    def extract_country_code(element) -> str:
        """Extract country code from span element."""
        span = element.find('span', class_='fi')
        if span and 'class' in span.attrs:
            classes = span['class']
            for cls in classes:
                if cls.startswith('fi-'):
                    return cls.split('-')[1].upper()
        return ''

def scrape_platinsport(url: str) -> tuple:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame(), ""

    soup = BeautifulSoup(response.text, 'html.parser')
    matches, channels, acestream_links, country_codes = [], [], [], []

    date_divs = soup.find_all('div', class_='myDiv')
    if len(date_divs) >= 2:
        schedule_date = date_divs[1].text.strip()
        date_parts = schedule_date.split()
        if len(date_parts) >= 4:
            day = date_parts[0].capitalize()
            date_num = date_parts[1].lower()
            month = date_parts[2].capitalize()
            year = date_parts[3]
            schedule_date = f"{day} {date_num} {month} {year} (UTC)"
    else:
        schedule_date = "Date not found"

    content_div = soup.find('div', class_='myDiv1')
    if content_div:
        current_match = None
        for element in content_div.contents:
            if isinstance(element, str) and element.strip():
                text = element.strip()
                if ':' in text:
                    parts = text.split()
                    time_str = parts[0]
                    try:
                        hour = int(time_str.split(':')[0])
                        minute = time_str.split(':')[1]
                        utc_hour = hour - 1
                        utc_time = f"{utc_hour:02d}:{minute}"
                        current_match = f"{utc_time} {' '.join(parts[1:])}"
                    except ValueError:
                        current_match = text
                else:
                    current_match = text
            elif element.name == 'a' and 'acestream://' in element.get('href', ''):
                country_code = CountryCodeTranslator.extract_country_code(element)
                translated_code = CountryCodeTranslator.translate(country_code)
                channel_name = element.text.strip()
                acestream_link = element.get('href').replace('acestream://', '')
                matches.append(current_match)
                channels.append(channel_name)
                acestream_links.append(acestream_link)
                country_codes.append(translated_code)

    df = pd.DataFrame({
        "Match": matches,
        "CountryCode": country_codes,
        "Channel": channels,
        "AceStream Link": acestream_links
    })
    
    return df, schedule_date