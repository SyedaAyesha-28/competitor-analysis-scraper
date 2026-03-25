# 🔍 Competitor Analysis Scraper

> A production-ready web scraping and competitor analysis tool with a live Streamlit dashboard.

🌐 **[Live Demo →](https://competitor-analysis-ayesha.streamlit.app)**  
📁 Built by [Syeda Ayesha](https://github.com/syedaayesha-28)

---

## 🎯 Problem Statement

Manually tracking competitor products, prices, and data is time-consuming. This tool automates scraping, structures raw data, generates insights, and exports polished Excel reports — all from a browser UI.

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Scraping | Python, BeautifulSoup, Requests |
| Data Processing | Pandas, openpyxl |
| UI / Dashboard | Streamlit |
| Export | Excel (multi-sheet), CSV |
| Deployment | Streamlit Cloud |

## ✨ Features

- 🕷️ Scrape product/price data from target sites
- 📊 Auto-generate competitor insights (avg price, top rated, availability)
- 📈 Visual charts (price distribution, rating breakdown)
- 📥 Export structured Excel reports with summary stats sheet
- 🔧 Configurable — choose pages, targets from sidebar

## 🏗️ Architecture

```
User (Browser)
    ↓
Streamlit UI (app.py)
    ↓
Scraper Module (BeautifulSoup + Requests)
    ↓
Data Pipeline (Pandas — clean, structure, analyse)
    ↓
Insights Engine → Charts → Excel Export
```

## 🚀 How to Run Locally

```bash
git clone https://github.com/syedaayesha-28/competitor-analysis-scraper
cd competitor-analysis-scraper
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 📁 Folder Structure

```
competitor-analysis-scraper/
├── app.py               # Main Streamlit app
├── requirements.txt     # Dependencies
└── README.md
```

## 📊 Sample Output

- Scrapes 100+ records in seconds
- Exports multi-sheet Excel: Raw Data + Summary Stats
- Insights: average pricing, availability rate, top-rated products

## 🔗 Related Skills Demonstrated

- Web scraping & data extraction
- Data cleaning and structuring (Pandas)
- Dashboard/UI development (Streamlit)
- Excel report generation (openpyxl)
- Cloud deployment (Streamlit Cloud)
