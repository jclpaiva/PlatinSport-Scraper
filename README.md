# PlatinSport Match Scraper 🎮⚽

A Streamlit-based web application that scrapes and displays sports match data from PlatinSport, providing AceStream links and convenient filtering options.

## 🌟 Features

- **Real-time Match Scraping**: Automatically fetches the latest matches from PlatinSport
- **Interactive Search**: Dynamic search functionality for matches and channels
- **Multiple Export Options**: Download data in Excel or M3U format
- **User-Friendly Interface**: Clean and responsive design with sortable tables
- **UTC Time Conversion**: Automatically converts match times to UTC
- **Link Bypass**: Handles bc.vc and bcvc.ink link redirections

## 🛠️ Technologies Used

- Python 3.x
- Streamlit
- Streamlit-searchbox
- Pandas
- Numpy
- BeautifulSoup4
- Requests
- Keyboard
- Psutil
- xlsxwriter

## 📋 Prerequisites

```bash
pip install streamlit pandas beautifulsoup4 requests keyboard psutil streamlit-searchbox
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/platinsport-scraper.git
cd platinsport-scraper
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

1. Start the Streamlit application:
```bash
streamlit run main.py
```

2. The application will:
   - Automatically fetch the latest match URL
   - Display matches in a searchable table
   - Allow downloading match data in Excel or M3U format
   - Provide clickable AceStream links

## 🔍 Features Breakdown

### Match Scraping
- Automatically retrieves match URLs from the homepage
- Parses match details, channels, and AceStream links
- Converts match times to UTC

### Search Functionality
- Real-time search across matches and channels
- Progressive search with fallback options
- Normalized text comparison for better matching

### Data Export
- Excel export with formatted match data
- M3U playlist generation for AceStream links
- UTC time-stamped filenames

### User Interface
- Responsive table layout
- Sticky headers for better navigation
- Custom icons for AceStream links
- Clean sidebar organization

## 🔧 Configuration

The application uses default configurations but can be modified through the following variables:
- Homepage URL: `homepage_url` in `get_platinsport_match_url()`
- Time conversion: UTC-1 conversion in the scraping function
- Table display settings: Custom CSS in the Streamlit app

## 🚫 Error Handling

The application includes comprehensive error handling for:
- Failed URL fetching
- Invalid data parsing
- Network connectivity issues
- Link bypass failures

## 🔒 Security

- URL validation and sanitization
- Safe request handling with timeouts
- Protected against common web scraping issues

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for complying with local laws and regulations regarding content access and streaming.

## 🙏 Acknowledgments

- PlatinSport for the match data
- AceStream for the streaming technology
- Streamlit for the web framework
- All contributors and users of this project
