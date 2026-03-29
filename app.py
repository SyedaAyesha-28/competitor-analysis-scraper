import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import io
import re
from datetime import datetime

st.set_page_config(page_title="CompetitorIQ", page_icon="📡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.hero-wrap {
    background: #0f172a; border-radius: 18px;
    padding: 2.2rem 2.8rem; margin-bottom: 1.8rem;
    position: relative; overflow: hidden;
}
.hero-wrap::before {
    content:""; position:absolute; top:-40px; right:-40px;
    width:220px; height:220px;
    background:radial-gradient(circle,#6366f1 0%,transparent 70%); opacity:0.35;
}
.hero-title { color:#f8fafc; font-size:2.1rem; font-weight:700; margin:0 0 0.25rem 0; }
.hero-sub   { color:#94a3b8; font-size:1rem; margin:0; }
.hero-tag   { display:inline-block; background:#1e293b; color:#818cf8;
              border:1px solid #3730a3; border-radius:6px;
              padding:2px 10px; font-size:0.75rem; font-weight:600; margin-top:0.7rem; }

.winner-wrap {
    background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);
    border:1px solid #334155; border-radius:14px; padding:1.4rem 1.8rem;
}
.winner-label { color:#fbbf24; font-size:0.72rem; font-weight:700;
                letter-spacing:1.5px; text-transform:uppercase; }
.winner-name  { color:#f1f5f9; font-size:1.5rem; font-weight:700; margin:4px 0; }
.winner-score { color:#64748b; font-size:0.85rem; }

.score-card     { background:#1e293b; border:1px solid #334155;
                  border-radius:12px; padding:1rem 1.2rem; text-align:center; margin-bottom:8px; }
.score-val      { font-size:1.7rem; font-weight:700; color:#e2e8f0; }
.score-lbl      { font-size:0.72rem; color:#64748b; margin-top:2px; }
.score-win      { background:#1e3a5f; border-color:#2563eb; }
.score-val-win  { color:#60a5fa; }

.ins-good { background:#052e16; border-left:3px solid #22c55e; color:#bbf7d0;
            padding:0.65rem 1rem; border-radius:0 8px 8px 0; margin:5px 0; font-size:0.88rem; }
.ins-warn { background:#2d1a00; border-left:3px solid #f59e0b; color:#fde68a;
            padding:0.65rem 1rem; border-radius:0 8px 8px 0; margin:5px 0; font-size:0.88rem; }
.ins-info { background:#0c1a35; border-left:3px solid #3b82f6; color:#bfdbfe;
            padding:0.65rem 1rem; border-radius:0 8px 8px 0; margin:5px 0; font-size:0.88rem; }

.sec { color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:2px;
       text-transform:uppercase; border-bottom:1px solid #1e293b;
       padding-bottom:6px; margin:1.5rem 0 0.8rem 0; }

.footer { margin-top:3rem; background:#0f172a; border:1px solid #1e293b;
          border-radius:12px; padding:1.2rem 2rem; }
.footer-inner { display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.5rem; }
.f-left  { color:#64748b; font-size:0.82rem; }
.f-right { color:#64748b; font-size:0.82rem; }
.f-name  { color:#818cf8; font-weight:600; }
.f-link  { color:#38bdf8; }

[data-testid="stSidebar"] { background:#0f172a; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p { color:#94a3b8 !important; }
[data-testid="stSidebar"] h3 { color:#e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──
st.markdown("""
<div class="hero-wrap">
  <div class="hero-title">📡 CompetitorIQ</div>
  <div class="hero-sub">Scrape any two websites · compare products, prices & ratings · export structured Excel</div>
  <div class="hero-tag">🤖 Web Scraping &nbsp;·&nbsp; Data Analysis &nbsp;·&nbsp; Competitive Intelligence</div>
</div>
""", unsafe_allow_html=True)

# ── CUSTOM WEBSITE GUIDE ──
with st.expander("📖 How to add a custom website — read this first"):
    st.markdown("""
**The golden rule:** You can only scrape sites that show data **without requiring login.**

---
### ✅ Websites you CAN scrape

| Type | Examples | What you extract |
|---|---|---|
| Practice sites | books.toscrape.com, quotes.toscrape.com | Products, prices, ratings |
| Job boards | remoteok.com, weworkremotely.com | Job titles, salaries |
| News / blogs | Any public blog | Headlines, authors |
| Open directories | Crunchbase public, Product Hunt | Company names, descriptions |
| Government data | data.gov.in | Open datasets |

### ❌ Websites you CANNOT scrape
- Sites requiring **login** (LinkedIn, Amazon account pages)
- Sites with **Cloudflare bot protection** (most large e-commerce block scrapers)
- Instagram, Twitter, Facebook — they actively block scrapers

---
### 🔧 How to find CSS selectors for a custom site

1. Open the site in **Chrome**
2. Right-click on a product name → click **Inspect**
3. Look at the HTML highlighted: e.g. `<h3 class="product-title">Laptop</h3>`
4. Your **Item selector** = `h3.product-title`
5. Do the same for price: e.g. `<span class="price">₹45,000</span>` → selector `span.price`

**Good sites to practice custom scraping:**
- `https://books.toscrape.com` — item: `article.product_pod`, title: `h3 a`, price: `.price_color`
- `https://quotes.toscrape.com` — item: `.quote`, title: `.text`, price: leave empty
- `https://webscraper.io/test-sites/e-commerce/allinone` — item: `.thumbnail`, title: `.title`, price: `.price`
""")

# ── SCRAPERS ──
HEADERS   = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
RMAP      = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}

def scrape_books(col_name, pages):
    rows = []
    for page in range(1, pages+1):
        try:
            r = requests.get(f"https://books.toscrape.com/catalogue/page-{page}.html",
                             headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for b in soup.select("article.product_pod"):
                price = float(re.sub(r"[^\d.]","", b.select_one(".price_color").text) or 0)
                rows.append({"Competitor":col_name,
                             "Product":b.select_one("h3 a")["title"],
                             "Price":price,
                             "Rating":RMAP.get(b.select_one(".star-rating")["class"][1],0),
                             "In_Stock":1 if "In stock" in b.select_one(".availability").text else 0,
                             "Category":"Books"})
            time.sleep(0.4)
        except Exception as e:
            st.warning(f"Page {page}: {e}")
    return pd.DataFrame(rows)

def scrape_quotes(col_name, pages):
    rows = []
    for page in range(1, pages+1):
        try:
            r = requests.get(f"https://quotes.toscrape.com/page/{page}/",
                             headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for q in soup.select(".quote"):
                tags = [t.text for t in q.select(".tag")]
                rows.append({"Competitor":col_name,
                             "Product":q.select_one(".text").text.strip()[:70]+"…",
                             "Price":round(len(tags)*1.5,1),
                             "Rating":min(5,len(tags)),
                             "In_Stock":1,
                             "Category":tags[0] if tags else "general"})
            time.sleep(0.4)
        except Exception as e:
            st.warning(f"Page {page}: {e}")
    return pd.DataFrame(rows)

def scrape_custom(col_name, url, item_sel, title_sel, price_sel, pages):
    rows = []
    for page in range(1, pages+1):
        page_url = url if page==1 else f"{url.rstrip('/')}?page={page}"
        try:
            r = requests.get(page_url, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                st.warning(f"HTTP {r.status_code} — stopping.")
                break
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select(item_sel) if item_sel.strip() else [soup]
            for item in items:
                t_el = item.select_one(title_sel) if title_sel.strip() else None
                p_el = item.select_one(price_sel) if price_sel.strip() else None
                title = t_el.get_text(strip=True)[:80] if t_el else "N/A"
                price = float(re.sub(r"[^\d.]","", p_el.get_text(strip=True)) or 0) if p_el else 0
                if title and title != "N/A":
                    rows.append({"Competitor":col_name,"Product":title,
                                 "Price":price,"Rating":0,"In_Stock":1,"Category":"Custom"})
            time.sleep(0.6)
        except Exception as e:
            st.warning(f"Page {page}: {e}"); break
    return pd.DataFrame(rows)

def get_insights(df_a, df_b, la, lb):
    ins, sa, sb = [], 0, 0
    avg_a,avg_b = df_a["Price"].mean(), df_b["Price"].mean()
    if avg_a < avg_b:
        sa+=1; ins.append(("good",f"💰 **{la}** is cheaper — {avg_a:.2f} vs {avg_b:.2f}"))
    elif avg_b < avg_a:
        sb+=1; ins.append(("good",f"💰 **{lb}** is cheaper — {avg_b:.2f} vs {avg_a:.2f}"))
    ra,rb = df_a["Rating"].mean(), df_b["Rating"].mean()
    if ra > rb:
        sa+=1; ins.append(("info",f"⭐ **{la}** is rated higher — {ra:.2f}/5 vs {rb:.2f}/5"))
    elif rb > ra:
        sb+=1; ins.append(("info",f"⭐ **{lb}** is rated higher — {rb:.2f}/5 vs {ra:.2f}/5"))
    av_a,av_b = df_a["In_Stock"].mean()*100, df_b["In_Stock"].mean()*100
    if av_a > av_b:
        sa+=1; ins.append(("good",f"✅ **{la}** has better availability — {av_a:.0f}% vs {av_b:.0f}%"))
    elif av_b > av_a:
        sb+=1; ins.append(("good",f"✅ **{lb}** has better availability — {av_b:.0f}% vs {av_a:.0f}%"))
    if len(df_a) > len(df_b):
        ins.append(("info",f"📦 **{la}** has larger catalogue — {len(df_a)} vs {len(df_b)}"))
    elif len(df_b) > len(df_a):
        ins.append(("info",f"📦 **{lb}** has larger catalogue — {len(df_b)} vs {len(df_a)}"))
    if df_a["Price"].std() > df_b["Price"].std()*1.4:
        ins.append(("warn",f"⚠️ **{la}** has inconsistent pricing — consider standardising price tiers"))
    elif df_b["Price"].std() > df_a["Price"].std()*1.4:
        ins.append(("warn",f"⚠️ **{lb}** has inconsistent pricing — prices vary widely"))
    winner = la if sa >= sb else lb
    return ins, winner, sa, sb

def to_excel(df_a, df_b, la, lb):
    buf = io.BytesIO()
    comb = pd.concat([df_a, df_b], ignore_index=True)
    summ = pd.DataFrame({"Metric":["Products","Avg Price","Avg Rating","In Stock %"],
                          la:[len(df_a),f"{df_a['Price'].mean():.2f}",f"{df_a['Rating'].mean():.2f}",f"{df_a['In_Stock'].mean()*100:.0f}%"],
                          lb:[len(df_b),f"{df_b['Price'].mean():.2f}",f"{df_b['Rating'].mean():.2f}",f"{df_b['In_Stock'].mean()*100:.0f}%"]})
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        comb.to_excel(w,index=False,sheet_name="All Data")
        df_a.to_excel(w,index=False,sheet_name=la[:31])
        df_b.to_excel(w,index=False,sheet_name=lb[:31])
        summ.to_excel(w,index=False,sheet_name="Summary")
    return buf.getvalue()

# ── SIDEBAR ──
SITES = {"📚 Books Store (books.toscrape.com)":"books",
         "💬 Quotes Platform (quotes.toscrape.com)":"quotes",
         "🔧 Custom URL":"custom"}

with st.sidebar:
    st.markdown("### ⚙️ Competitor A")
    site_a  = st.selectbox("Source A", list(SITES.keys()), key="sa")
    label_a = st.text_input("Label A", "Competitor A", key="la")
    pages_a = st.slider("Pages A", 1, 5, 2, key="pa")
    url_a=item_a=title_a=price_a=""
    if SITES[site_a]=="custom":
        url_a   = st.text_input("URL A", placeholder="https://example.com/products", key="ua")
        item_a  = st.text_input("Item CSS selector", placeholder="article.product", key="ia",
                                 help="Selector for each product card")
        title_a = st.text_input("Title selector", placeholder="h3 a", key="ta")
        price_a = st.text_input("Price selector (optional)", placeholder="span.price", key="pra")

    st.markdown("---")
    st.markdown("### ⚙️ Competitor B")
    site_b  = st.selectbox("Source B", list(SITES.keys()), index=1, key="sb")
    label_b = st.text_input("Label B", "Competitor B", key="lb")
    pages_b = st.slider("Pages B", 1, 5, 2, key="pb")
    url_b=item_b=title_b=price_b=""
    if SITES[site_b]=="custom":
        url_b   = st.text_input("URL B", placeholder="https://example.com/products", key="ub")
        item_b  = st.text_input("Item CSS selector B", placeholder="article.product", key="ib")
        title_b = st.text_input("Title selector B", placeholder="h3 a", key="tb")
        price_b = st.text_input("Price selector B (optional)", placeholder="span.price", key="prb")

    st.markdown("---")
    run_btn = st.button("📡 Run Analysis", type="primary", use_container_width=True)
    st.caption("CompetitorIQ · Built by Syeda Ayesha")

if not run_btn:
    st.markdown('<div class="sec">HOW IT WORKS</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, (icon, title, desc) in zip(cols,[
        ("📡","Pick Sources","2 presets or any custom URL"),
        ("🕷️","Scrape","BeautifulSoup extracts data automatically"),
        ("⚔️","Compare","Side-by-side scorecard with winner"),
        ("📊","Visualise","4 comparison charts"),
        ("📥","Export","4-sheet Excel or CSV"),
    ]):
        col.markdown(f"**{icon} {title}**"); col.caption(desc)
    st.stop()

# ── SCRAPE ──
label_a = label_a.strip() or "Competitor A"
label_b = label_b.strip() or "Competitor B"
SAFE_A, SAFE_B = "A", "B"   # safe internal column names for charts

c1, c2 = st.columns(2)
with c1:
    with st.spinner(f"Scraping {label_a}…"):
        mode = SITES[site_a]
        df_a = (scrape_books(SAFE_A,pages_a) if mode=="books"
                else scrape_quotes(SAFE_A,pages_a) if mode=="quotes"
                else scrape_custom(SAFE_A,url_a,item_a,title_a,price_a,pages_a))
    if df_a.empty: st.error(f"{label_a}: nothing scraped."); st.stop()
    st.success(f"✅ {label_a}: {len(df_a)} records")

with c2:
    with st.spinner(f"Scraping {label_b}…"):
        mode = SITES[site_b]
        df_b = (scrape_books(SAFE_B,pages_b) if mode=="books"
                else scrape_quotes(SAFE_B,pages_b) if mode=="quotes"
                else scrape_custom(SAFE_B,url_b,item_b,title_b,price_b,pages_b))
    if df_b.empty: st.error(f"{label_b}: nothing scraped."); st.stop()
    st.success(f"✅ {label_b}: {len(df_b)} records")

ins, winner, sa, sb = get_insights(df_a, df_b, label_a, label_b)

# ── WINNER ──
st.markdown('<div class="sec">RESULT</div>', unsafe_allow_html=True)
wc, _ = st.columns([3, 7])
with wc:
    st.markdown(f"""
    <div class="winner-wrap">
      <div style="font-size:2rem">🏆</div>
      <div class="winner-label">Overall Winner</div>
      <div class="winner-name">{winner}</div>
      <div class="winner-score">{label_a} {sa}–{sb} {label_b} &nbsp;·&nbsp; price · rating · availability</div>
    </div>""", unsafe_allow_html=True)

# ── SCORECARD ──
st.markdown('<div class="sec">HEAD-TO-HEAD</div>', unsafe_allow_html=True)
metrics = [
    ("Products",    len(df_a),                              len(df_b),             False),
    ("Avg Price",   df_a["Price"].mean(),                   df_b["Price"].mean(),  True),
    ("Avg Rating",  df_a["Rating"].mean(),                  df_b["Rating"].mean(), False),
    ("In Stock %",  df_a["In_Stock"].mean()*100,            df_b["In_Stock"].mean()*100, False),
    ("Min Price",   df_a["Price"].min(),                    df_b["Price"].min(),   True),
    ("5★ Products", int((df_a["Rating"]==5).sum()),         int((df_b["Rating"]==5).sum()), False),
]
ha, hv, hb = st.columns([5,2,5])
ha.markdown(f"**{label_a}**"); hb.markdown(f"**{label_b}**")
for metric, va, vb, lower_wins in metrics:
    win_a = va < vb if lower_wins else va > vb
    fmt = lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)
    ca, cv, cb = st.columns([5,2,5])
    ca.markdown(f'<div class="score-card {"score-win" if win_a else ""}"><div class="score-val {"score-val-win" if win_a else ""}">{fmt(va)}</div><div class="score-lbl">{metric}</div></div>', unsafe_allow_html=True)
    cv.markdown(f'<div style="text-align:center;color:#475569;padding-top:1rem;font-size:0.8rem">{metric}</div>', unsafe_allow_html=True)
    cb.markdown(f'<div class="score-card {"score-win" if not win_a else ""}"><div class="score-val {"score-val-win" if not win_a else ""}">{fmt(vb)}</div><div class="score-lbl">{metric}</div></div>', unsafe_allow_html=True)

# ── CHARTS — using safe column names, explicit int conversion ──
st.markdown('<div class="sec">VISUAL ANALYSIS</div>', unsafe_allow_html=True)
ch1, ch2 = st.columns(2)
with ch1:
    st.markdown("**Price Distribution**")
    pc = pd.concat([df_a["Price"].value_counts().sort_index().rename(label_a),
                    df_b["Price"].value_counts().sort_index().rename(label_b)],axis=1).fillna(0)
    st.bar_chart(pc, height=230)
with ch2:
    st.markdown("**Rating Distribution**")
    rc = pd.concat([df_a["Rating"].value_counts().sort_index().rename(label_a),
                    df_b["Rating"].value_counts().sort_index().rename(label_b)],axis=1).fillna(0)
    st.bar_chart(rc, height=230)

ch3, ch4 = st.columns(2)
with ch3:
    st.markdown("**Avg Price vs Avg Rating**")
    ov = pd.DataFrame([[df_a["Price"].mean(), df_b["Price"].mean()],
                       [df_a["Rating"].mean(), df_b["Rating"].mean()]],
                      index=["Avg Price","Avg Rating"], columns=[label_a, label_b])
    st.bar_chart(ov, height=230)
with ch4:
    st.markdown("**Stock Availability (count)**")
    # Explicit integers and explicit string index — fixes the Altair empty-field ValueError
    av = pd.DataFrame(
        data={"Status":["In Stock","Out of Stock"],
              label_a:[int(df_a["In_Stock"].sum()), int((df_a["In_Stock"]==0).sum())],
              label_b:[int(df_b["In_Stock"].sum()), int((df_b["In_Stock"]==0).sum())]},
    ).set_index("Status")
    st.bar_chart(av, height=230)

# ── INSIGHTS ──
st.markdown('<div class="sec">AI-GENERATED INSIGHTS</div>', unsafe_allow_html=True)
cmap = {"good":"ins-good","warn":"ins-warn","info":"ins-info"}
for kind, text in ins:
    st.markdown(f'<div class="{cmap[kind]}">{text}</div>', unsafe_allow_html=True)

# ── DATA TABLES ──
st.markdown('<div class="sec">RAW DATA</div>', unsafe_allow_html=True)
df_a_d = df_a.copy(); df_a_d["Competitor"] = label_a
df_b_d = df_b.copy(); df_b_d["Competitor"] = label_b
comb   = pd.concat([df_a_d, df_b_d], ignore_index=True)
t1,t2,t3 = st.tabs([f"{label_a} ({len(df_a)})", f"{label_b} ({len(df_b)})", "Combined"])
with t1: st.dataframe(df_a_d, use_container_width=True, height=260)
with t2: st.dataframe(df_b_d, use_container_width=True, height=260)
with t3: st.dataframe(comb,   use_container_width=True, height=260)

# ── EXPORT ──
st.markdown('<div class="sec">EXPORT</div>', unsafe_allow_html=True)
e1, e2 = st.columns(2)
with e1:
    st.download_button("⬇️ Excel Report (4 sheets)",
                       data=to_excel(df_a_d, df_b_d, label_a, label_b),
                       file_name=f"competitoriq_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)
with e2:
    st.download_button("⬇️ CSV",
                       data=comb.to_csv(index=False),
                       file_name=f"competitoriq_{datetime.now().strftime('%Y%m%d')}.csv",
                       mime="text/csv", use_container_width=True)

# ── FOOTER ──
st.markdown(f"""
<div class="footer">
<div class="footer-inner">
  <div class="f-left">📡 <span class="f-name">CompetitorIQ</span> &nbsp;·&nbsp;
    Built with Python, BeautifulSoup & Streamlit &nbsp;·&nbsp; {len(df_a)+len(df_b)} records scraped</div>
  <div class="f-right">Made by <span class="f-name">Syeda Ayesha</span> &nbsp;·&nbsp;
    <a class="f-link" href="https://github.com/syedaayesha-28">GitHub</a> &nbsp;·&nbsp;
    <a class="f-link" href="https://linkedin.com/in/engineer-syeda-ayesha">LinkedIn</a></div>
</div></div>
""", unsafe_allow_html=True)
