import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from typing import Tuple, List, Dict, Optional
from datetime import datetime

class CountryCodeTranslator:
    """Handles country code translations for specific cases."""
    COUNTRY_CODE_MAPPING = {
        'GB': 'UK',
        'UA': 'UKR',
        'TR': 'TR-1'
    }

    @classmethod
    def translate(cls, code: str) -> str:
        """Translate country codes according to mapping."""
        return cls.COUNTRY_CODE_MAPPING.get(code.upper(), code.upper())

class HTMLParser:
    """Handles HTML parsing and data extraction."""
    
    @staticmethod
    def extract_schedule_date(soup: BeautifulSoup) -> str:
        """Extract and format schedule date from myDiv class."""
        date_div = soup.find('div', class_='myDiv')
        if not date_div:
            return "Date not found"
            
        date_text = date_div.get_text(strip=True)
        if "UK+1" in date_text:
            date_text = date_text.replace("UK+1", "UTC")
        return date_text

    @staticmethod
    def extract_match_time(text: str) -> Tuple[str, str]:
        """Extract and convert time from CET to UTC."""
        if ':' not in text:
            return '', text
            
        parts = text.split(' ', 1)
        if len(parts) != 2:
            return '', text
            
        time_str, match_info = parts
        try:
            hour, minute = map(int, time_str.split(':'))
            utc_hour = (hour - 1) % 24  # Convert CET to UTC
            return f"{utc_hour:02d}:{minute:02d}", match_info
        except ValueError:
            return '', text

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

class MatchScraper:
    """Main scraper class for extracting match data."""
    
    def __init__(self):
        self.parser = HTMLParser()
        self.country_translator = CountryCodeTranslator()

    def scrape(self, url: str) -> Tuple[pd.DataFrame, str]:
        """Main scraping function."""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save HTML for debugging if needed
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            schedule_date = self.parser.extract_schedule_date(soup)
            matches_data = self.extract_matches(soup)
            
            if not matches_data:
                st.warning("No matches found in the standard structure. Trying alternative method...")
                matches_data = self.extract_matches_alternative(soup)
            
            if matches_data:
                df = pd.DataFrame(matches_data)
                st.success(f"Successfully scraped {len(matches_data)} matches!")
                return df, schedule_date
            
            st.error("No match data found.")
            return pd.DataFrame(), schedule_date
            
        except requests.RequestException as e:
            st.error(f"Failed to fetch data: {e}")
            return pd.DataFrame(), ""

    def extract_matches(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract matches from the standard structure."""
        matches_data = []
        content_div = soup.find('div', class_='myDiv1')
        
        if not content_div:
            return []
            
        current_match = None
        
        for element in content_div.children:
            if isinstance(element, str) and element.strip():
                text = element.strip()
                time_str, match_info = self.parser.extract_match_time(text)
                if time_str:
                    current_match = f"{time_str} {match_info}"
                else:
                    current_match = text
                    
            elif element.name == 'a' and 'acestream://' in element.get('href', ''):
                if not current_match:
                    continue
                    
                href = element.get('href', '')
                country_code = self.parser.extract_country_code(element)
                translated_code = self.country_translator.translate(country_code)
                channel_name = element.get_text(strip=True)
                
                matches_data.append({
                    "Match": current_match,
                    "CountryCode": translated_code,
                    "Channel": channel_name,
                    "AceStream Link": href.replace('acestream://', '')
                })
        
        return matches_data

    def extract_matches_alternative(self, soup: BeautifulSoup) -> List[Dict]:
        """Alternative method for extracting matches when standard structure fails."""
        matches_data = []
        current_match = None
        
        # Find all text nodes and links
        for element in soup.stripped_strings:
            text = element.strip()
            if not text:
                continue
                
            time_str, match_info = self.parser.extract_match_time(text)
            if time_str:
                current_match = f"{time_str} {match_info}"
            else:
                current_match = text
                
        # Extract acestream links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if not href.startswith('acestream://'):
                continue
                
            if not current_match:
                continue
                
            country_code = self.parser.extract_country_code(link)
            translated_code = self.country_translator.translate(country_code)
            channel_name = link.get_text(strip=True)
            
            matches_data.append({
                "Match": current_match,
                "CountryCode": translated_code,
                "Channel": channel_name,
                "AceStream Link": href.replace('acestream://', '')
            })
        
        return matches_data

def scrape_platinsport(url: str) -> Tuple[pd.DataFrame, str]:
    """Main entry point for scraping PlatinSport."""
    scraper = MatchScraper()
    return scraper.scrape(url)