import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import io
from datetime import datetime

st.set_page_config(
    page_title="Competitor Analysis Tool",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #0D9488; margin-bottom: 0.2rem; }
    .sub-header { color: #64748B; margin-bottom: 2rem; font-size: 1rem; }
    .metric-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem; text-align: center; }
    .tag { background: #CCFBF1; color: #0D9488; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin: 2px; display: inline-block; }
    .insight-box { background: #F0FDF4; border-left: 4px solid #10B981; padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
    .warning-box { background: #FFF7ED; border-left: 4px solid #F59E0B; padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🔍 Competitor Analysis Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Scrape, structure & compare competitor product/pricing data — export to Excel</div>', unsafe_allow_html=True)

DEMO_DATA = {
    "books.toscrape.com": {
        "description": "Book store — scrapes titles, prices, ratings, availability",
        "url": "https://books.toscrape.com/catalogue/page-{page}.html",
        "type": "books"
    },
    "quotes.toscrape.com": {
        "description": "Quotes site — scrapes quotes, authors, tags",
        "url": "https://quotes.toscrape.com/page/{page}/",
        "type": "quotes"
    }
}

def scrape_books(pages=2):
    results = []
    for page in range(1, pages + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            books = soup.select("article.product_pod")
            for b in books:
                title = b.select_one("h3 a")["title"]
                price = b.select_one(".price_color").text.strip().replace("Â", "").replace("£", "£")
                rating_word = b.select_one(".star-rating")["class"][1]
                rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
                rating = rating_map.get(rating_word, 0)
                availability = b.select_one(".availability").text.strip()
                results.append({
                    "Title": title,
                    "Price (£)": float(price.replace("£", "").strip()),
                    "Rating (1-5)": rating,
                    "Availability": availability,
                    "Source": "books.toscrape.com",
                    "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
            time.sleep(0.5)
        except Exception as e:
            st.warning(f"Page {page} failed: {e}")
    return results

def scrape_quotes(pages=2):
    results = []
    for page in range(1, pages + 1):
        url = f"https://quotes.toscrape.com/page/{page}/"
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            quotes = soup.select(".quote")
            for q in quotes:
                text = q.select_one(".text").text.strip().strip("\u201c\u201d")
                author = q.select_one(".author").text.strip()
                tags = [t.text for t in q.select(".tag")]
                results.append({
                    "Quote": text[:120] + ("..." if len(text) > 120 else ""),
                    "Author": author,
                    "Tags": ", ".join(tags),
                    "Tag Count": len(tags),
                    "Source": "quotes.toscrape.com",
                    "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
            time.sleep(0.5)
        except Exception as e:
            st.warning(f"Page {page} failed: {e}")
    return results

def generate_insights_books(df):
    insights = []
    avg_price = df["Price (£)"].mean()
    cheapest = df.loc[df["Price (£)"].idxmin()]
    most_expensive = df.loc[df["Price (£)"].idxmax()]
    top_rated = df[df["Rating (1-5)"] == 5]
    insights.append(f"📊 Average price across {len(df)} products: **£{avg_price:.2f}**")
    insights.append(f"💰 Cheapest: **{cheapest['Title'][:50]}** at £{cheapest['Price (£)']:.2f}")
    insights.append(f"💎 Most expensive: **{most_expensive['Title'][:50]}** at £{most_expensive['Price (£)']:.2f}")
    insights.append(f"⭐ **{len(top_rated)} products** have a 5-star rating — potential bestsellers")
    in_stock = df[df["Availability"] == "In stock"]
    insights.append(f"✅ **{len(in_stock)}/{len(df)}** products in stock ({100*len(in_stock)//len(df)}% availability rate)")
    return insights

def generate_insights_quotes(df):
    insights = []
    top_authors = df["Author"].value_counts().head(3)
    all_tags = ", ".join(df["Tags"].dropna().tolist()).split(", ")
    from collections import Counter
    tag_counts = Counter([t.strip() for t in all_tags if t.strip()])
    top_tags = tag_counts.most_common(5)
    insights.append(f"✍️ Most quoted author: **{top_authors.index[0]}** ({top_authors.iloc[0]} quotes)")
    insights.append(f"🏷️ Top themes: {', '.join([f'**{t[0]}**' for t in top_tags[:3]])}")
    insights.append(f"📝 Average tags per quote: **{df['Tag Count'].mean():.1f}**")
    insights.append(f"📚 {df['Author'].nunique()} unique authors across {len(df)} quotes scraped")
    return insights

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Raw Data")
        summary = df.describe(include="all").reset_index()
        summary.to_excel(writer, index=False, sheet_name="Summary Stats")
    return output.getvalue()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Scraper Settings")
    target = st.selectbox("Select Target Site", list(DEMO_DATA.keys()))
    st.caption(DEMO_DATA[target]["description"])
    pages = st.slider("Pages to scrape", 1, 5, 2)
    st.markdown("---")
    st.markdown("### 📌 About")
    st.markdown("""
    This tool demonstrates:
    - **Web scraping** with BeautifulSoup
    - **Data structuring** with Pandas
    - **Competitor insights** generation
    - **Excel export** for reporting
    
    Built by **Syeda Ayesha** · [GitHub](https://github.com/syedaayesha-28)
    """)

# --- MAIN ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    run = st.button("🚀 Run Scraper", type="primary", use_container_width=True)
with col2:
    st.markdown("")

if run:
    with st.spinner(f"Scraping {DEMO_DATA[target]['description']}..."):
        if DEMO_DATA[target]["type"] == "books":
            data = scrape_books(pages)
        else:
            data = scrape_quotes(pages)

    if data:
        df = pd.DataFrame(data)
        st.success(f"✅ Scraped **{len(df)} records** from {target}")

        # Metrics row
        st.markdown("### 📊 Quick Stats")
        cols = st.columns(4)
        cols[0].metric("Records Scraped", len(df))
        cols[1].metric("Columns", len(df.columns))
        cols[2].metric("Source", target.split(".")[0].capitalize())
        cols[3].metric("Pages Scraped", pages)

        # Insights
        st.markdown("### 💡 Automated Insights")
        if DEMO_DATA[target]["type"] == "books":
            insights = generate_insights_books(df)
        else:
            insights = generate_insights_quotes(df)

        for i in insights:
            st.markdown(f'<div class="insight-box">{i}</div>', unsafe_allow_html=True)

        # Data table
        st.markdown("### 📋 Structured Data")
        st.dataframe(df, use_container_width=True, height=300)

        # Charts
        if DEMO_DATA[target]["type"] == "books":
            st.markdown("### 📈 Visual Analysis")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Price Distribution**")
                price_hist = df["Price (£)"].value_counts().sort_index()
                st.bar_chart(price_hist)
            with c2:
                st.markdown("**Rating Distribution**")
                rating_dist = df["Rating (1-5)"].value_counts().sort_index()
                st.bar_chart(rating_dist)

        # Export
        st.markdown("### 📥 Export")
        c1, c2 = st.columns(2)
        with c1:
            excel_data = to_excel(df)
            st.download_button(
                "⬇️ Download Excel Report",
                data=excel_data,
                file_name=f"competitor_analysis_{target.split('.')[0]}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with c2:
            csv = df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                data=csv,
                file_name=f"competitor_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.error("No data scraped. Check your connection and try again.")
else:
    st.markdown("""
    <div class="warning-box">
    👆 <strong>Select a target site from the sidebar and click "Run Scraper" to begin.</strong><br>
    Uses only legal, public scraping practice sites — safe to demo to recruiters.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗺️ How It Works")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("**1️⃣ Select Target**\nChoose a competitor site to scrape from the sidebar")
    c2.markdown("**2️⃣ Configure**\nSet how many pages to scrape")
    c3.markdown("**3️⃣ Scrape & Structure**\nData is cleaned and structured into a DataFrame")
    c4.markdown("**4️⃣ Export**\nDownload as Excel with summary stats sheet")
