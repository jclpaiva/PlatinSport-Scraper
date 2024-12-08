import re
import base64
import requests
import streamlit as st
from bs4 import BeautifulSoup

def bypass_bcvc(link):
    if "bc.vc" in link:
        pos = link.find("https://www.p")
        return link[pos:] if pos != -1 else None
    elif "bcvc.ink" in link:
        match = re.search(r"(https?://[^/]+/[^/]+)$", link)
        if match:
            short_link = match.group(1).split("/")[-1]
            try:
                decoded = base64.b64decode(short_link).decode('utf-8')
                if "platinsport" in decoded:
                    return decoded
            except Exception:
                print("Not Base64 encoded, trying regex extraction")
            direct_match = re.search(r"(https?://.*platinsport[^\s&]+)", link)
            if direct_match:
                return direct_match.group(1)
    return None

def get_platinsport_match_url(homepage_url="https://www.platinsport.com/"):
    try:
        response = requests.get(homepage_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Failed to fetch homepage: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    link_tag = soup.find('a', href=lambda href: href and 'link/' in href)
    if link_tag and link_tag['href']:
        href = link_tag['href']
        if not href.startswith("http"):
            href = homepage_url.rstrip("/") + href
        bypassed_url = bypass_bcvc(href) or href
        return bypassed_url

    st.error("Could not find a valid match URL on the homepage.")
    return None