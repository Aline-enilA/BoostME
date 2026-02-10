import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =============================
# CONFIG & THEME
# =============================
st.set_page_config(
    page_title="Boost Me – Labo d'influence",
    page_icon="🚀",
    layout="wide"
)

BOOSTME = {
    "orange": "#FF8A00",
    "violet": "#7B61FF",
    "rose":   "#FF4D8D",
    "jaune":  "#FFD600",
    "bg":     "#0F0F14",
    "card":   "#171724",
    "stroke": "rgba(255,255,255,0.08)",
    "text":   "#FFFFFF",
    "muted":  "rgba(255,255,255,0.70)"
}

def inject_css():
    st.markdown(
        f"""
        <style>
            /* Layout */
            .block-container {{
                padding-top: 1.2rem;
                padding-bottom: 3rem;
            }}
            /* Headings */
            h1, h2, h3 {{
                letter-spacing: .2px;
            }}
            /* Cards */
            .bm-card {{
                background: {BOOSTME["card"]};
                border: 1px solid {BOOSTME["stroke"]};
                border-radius: 18px;
                padding: 14px 16px;
                box-shadow: 0 10px 22px rgba(0,0,0,.20);
            }}
            .bm-kpi-title {{
                font-size: 0.90rem;
                color: {BOOSTME["muted"]};
                margin-bottom: 6px;
            }}
            .bm-kpi-value {{
                font-size: 1.55rem;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 4px;
            }}
            .bm-chip {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 0.80rem;
                border: 1px solid {BOOSTME["stroke"]};
                color: {BOOSTME["muted"]};
            }}

            /* Plotly container look */
            .stPlotlyChart > div {{
                border-radius: 18px !important;
                border: 1px solid {BOOSTME["stroke"]};
                overflow: hidden;
                background: {BOOSTME["card"]};
                padding: 10px;
            }}

            /* Sidebar */
            section[data-testid="stSidebar"] {{
                border-right: 1px solid {BOOSTME["stroke"]};
            }}

            /* Buttons / inputs rounding */
            .stButton>button {{
                border-radius: 12px;
            }}
            div[data-baseweb="select"] > div {{
                border-radius: 12px !important;
            }}
            div[data-baseweb="input"] > div {{
                border-radius: 12px !important;
            }}

            /* Small divider */
            .bm-divider {{
                height: 1px;
                background: {BOOSTME["stroke"]};
                margin: 14px 0 18px 0;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

inject_css()

# =============================
# LOGO
# =============================
LOGO_PATH = Path("LOGO_BoostMe.png")

def show_header():
    left, right = st.columns([1, 3], vertical_alignment="center")
    with left:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=170)
        else:
            st.warning("Logo non trouvé : mets ton fichier dans assets/LOGO_BoostMe.png")
    with right:
        st.markdown(
            f"""
            <div style="padding-top:6px">
                <h1 style="margin:0">Boost Me — Dashboard YouTube</h1>
                <div style="margin-top:6px">
                    <span class="bm-chip">Orange</span>
                    <span class="bm-chip">Violet</span>
                    <span class="bm-chip">Rose</span>
                    <span class="bm-chip">Jaune</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('<div class="bm-divider"></div>', unsafe_allow_html=True)

# =============================
# 1) LOAD DATA
# =============================
@st.cache_data
def load_data():
    cats = pd.read_csv("data/cats.csv")
    chaines = pd.read_csv("data/chaines.csv")
    videos = pd.read_csv("data/videos.csv", parse_dates=["published_at"])
    return cats, chaines, videos

cats, chaines, videos = load_data()

# =============================
# 2) CLEAN COLUMNS
# =============================
def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("%", "pct", regex=False)
    )
    return df

cats = clean_columns(cats)
chaines = clean_columns(chaines)
videos = clean_columns(videos)

# =============================
# 3) SECURE VARIABLE COLUMNS
# =============================

# 3a) engagement rate côté chaines (auto)
candidates = [c for c in chaines.columns if "engagement" in c and "rate" in c]
if len(candidates) == 0:
    st.error("Je ne trouve aucune colonne 'engagement' + 'rate' dans la table chaines.")
    st.write("Colonnes chaines :", list(chaines.columns))
    st.stop()

engagement_col = candidates[0]
if engagement_col != "engagement_rate_pct":
    chaines.rename(columns={engagement_col: "engagement_rate_pct"}, inplace=True)
chaines["engagement_rate_pct"] = pd.to_numeric(chaines["engagement_rate_pct"], errors="coerce")

# 3b) taux engagement côté videos (auto)
eng_candidates = [c for c in videos.columns if "taux" in c and "engagement" in c]
if len(eng_candidates) == 0:
    st.error("Je ne trouve pas la colonne de taux d'engagement dans videos.")
    st.write("Colonnes videos :", list(videos.columns))
    st.stop()

taux_eng_col = eng_candidates[0]
if taux_eng_col != "taux_engagement_pct":
    videos.rename(columns={taux_eng_col: "taux_engagement_pct"}, inplace=True)
videos["taux_engagement_pct"] = pd.to_numeric(videos["taux_engagement_pct"], errors="coerce")

# =============================
# 4) CALCULATED COLUMNS (from published_at)
# =============================
videos["published_at"] = pd.to_datetime(videos["published_at"], errors="coerce")
videos["heure_publication"] = videos["published_at"].dt.hour
videos["jour_semaine_num"] = videos["published_at"].dt.weekday

jours_map = {0:"Lundi",1:"Mardi",2:"Mercredi",3:"Jeudi",4:"Vendredi",5:"Samedi",6:"Dimanche"}
videos["jour_semaine"] = videos["jour_semaine_num"].map(jours_map)

ordre_jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
videos["jour_semaine"] = pd.Categorical(videos["jour_semaine"], categories=ordre_jours, ordered=True)

videos["annee"] = videos["published_at"].dt.year
videos["engagement_total"] = videos["likes"].fillna(0) + videos["comments"].fillna(0)

# =============================
# 5) JOINS
# =============================
# Videos ↔ Cats
videos = videos.merge(
    cats[["category_id", "name"]],
    on="category_id",
    how="left"
).rename(columns={"name": "categorie"})

# Videos ↔ Chaines (avoid "title" conflict)
chaines_for_merge = chaines.rename(columns={"title": "chaine"})

videos = videos.merge(
    chaines_for_merge[["id", "chaine", "country", "subscribers", "engagement_rate_pct", "nb_videos"]],
    left_on="channel_id",
    right_on="id",
    how="left",
    suffixes=("", "_chaine")
)

# =============================
# SIDEBAR (filters)
# =============================
st.sidebar.markdown("## 🎯 Filtres Boost Me")
if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)

annees = st.sidebar.multiselect(
    "Année",
    sorted(videos["annee"].dropna().unique()),
    default=sorted(videos["annee"].dropna().unique())
)

categories = st.sidebar.multiselect(
    "Catégories",
    sorted(videos["categorie"].dropna().unique()),
    default=sorted(videos["categorie"].dropna().unique())
)

chaines_sel = st.sidebar.multiselect(
    "Chaînes",
    sorted(videos["chaine"].dropna().unique()),
    default=sorted(videos["chaine"].dropna().unique())
)

jours_sel = st.sidebar.multiselect(
    "Jour de publication",
    list(videos["jour_semaine"].cat.categories),
    default=list(videos["jour_semaine"].cat.categories)
)

heures = st.sidebar.slider("Heure de publication", 0, 23, (0, 23))

# Filtered df
df = videos[
    (videos["annee"].isin(annees)) &
    (videos["categorie"].isin(categories)) &
    (videos["chaine"].isin(chaines_sel)) &
    (videos["jour_semaine"].isin(jours_sel)) &
    (videos["heure_publication"].between(heures[0], heures[1]))
].copy()

# =============================
# HEADER
# =============================
show_header()

# =============================
# KPI CARDS (custom)
# =============================
def kpi_card(title: str, value: str, accent: str):
    st.markdown(
        f"""
        <div class="bm-card">
            <div class="bm-kpi-title">{title}</div>
            <div class="bm-kpi-value" style="color:{accent}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("📹 Vidéos analysées", f"{len(df):,}", BOOSTME["orange"])
with k2:
    v = f"{df['views'].mean():,.0f}" if len(df) else "0"
    kpi_card("👀 Vues moyennes / vidéo", v, BOOSTME["jaune"])
with k3:
    e = f"{df['taux_engagement_pct'].mean():.2f} %" if len(df) else "0"
    kpi_card("⚡ Engagement moyen", e, BOOSTME["rose"])
with k4:
    it = f"{df['engagement_total'].sum():,.0f}" if len(df) else "0"
    kpi_card("💬 Interactions totales", it, BOOSTME["violet"])

st.markdown('<div class="bm-divider"></div>', unsafe_allow_html=True)

# =============================
# CHARTS
# =============================

# A) Views by category
st.subheader("📊 Moyenne de vues par catégorie")
cat_views = (
    df.groupby("categorie", as_index=False)["views"]
    .mean()
    .sort_values("views", ascending=False)
)

fig_cat = px.bar(
    cat_views,
    x="categorie",
    y="views",
    title=None
)
fig_cat.update_traces(marker_color=BOOSTME["orange"])
fig_cat.update_layout(
    paper_bgcolor=BOOSTME["card"],
    plot_bgcolor=BOOSTME["card"],
    font_color=BOOSTME["text"],
    xaxis_title=None,
    yaxis_title="Vues moyennes",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_cat, use_container_width=True)

# B) Engagement by hour
st.subheader("⏰ Engagement moyen par heure")
hour_eng = (
    df.groupby("heure_publication", as_index=False)["taux_engagement_pct"]
    .mean()
    .sort_values("heure_publication")
)

fig_hour = px.line(
    hour_eng,
    x="heure_publication",
    y="taux_engagement_pct",
    markers=True,
    title=None
)
fig_hour.update_traces(line_color=BOOSTME["violet"])
fig_hour.update_layout(
    paper_bgcolor=BOOSTME["card"],
    plot_bgcolor=BOOSTME["card"],
    font_color=BOOSTME["text"],
    xaxis_title="Heure",
    yaxis_title="Taux d'engagement (%)",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_hour, use_container_width=True)

# C) Engagement by weekday
st.subheader("📅 Engagement moyen par jour")
day_eng = (
    df.groupby("jour_semaine", as_index=False)["taux_engagement_pct"]
    .mean()
    .sort_values("jour_semaine")
)

fig_day = px.line(
    day_eng,
    x="jour_semaine",
    y="taux_engagement_pct",
    markers=True,
    title=None
)
fig_day.update_traces(line_color=BOOSTME["rose"])
fig_day.update_layout(
    paper_bgcolor=BOOSTME["card"],
    plot_bgcolor=BOOSTME["card"],
    font_color=BOOSTME["text"],
    xaxis_title=None,
    yaxis_title="Taux d'engagement (%)",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_day, use_container_width=True)

# D) Top channels by interactions
st.subheader("🏆 Top chaînes (interactions)")
top_chaines = (
    df.groupby("chaine", as_index=False)["engagement_total"]
    .sum()
    .sort_values("engagement_total", ascending=False)
    .head(15)
)

fig_top = px.bar(
    top_chaines,
    x="engagement_total",
    y="chaine",
    orientation="h",
    title=None
)
fig_top.update_traces(marker_color=BOOSTME["jaune"])
fig_top.update_layout(
    paper_bgcolor=BOOSTME["card"],
    plot_bgcolor=BOOSTME["card"],
    font_color=BOOSTME["text"],
    xaxis_title="Interactions",
    yaxis_title=None,
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_top, use_container_width=True)

# =============================
# TABLE
# =============================
with st.expander("🔎 Explorer les données filtrées"):
    st.dataframe(df, use_container_width=True)

# =============================
# DEBUG (optional)
# =============================
with st.expander("🛠️ Debug (colonnes)"):
    st.write("Colonnes cats :", list(cats.columns))
    st.write("Colonnes chaines :", list(chaines.columns))
    st.write("Colonnes videos :", list(videos.columns))
    cols_preview = [c for c in ["title", "chaine", "categorie", "views", "taux_engagement_pct"] if c in videos.columns]
    st.dataframe(videos[cols_preview].head(10), use_container_width=True)

