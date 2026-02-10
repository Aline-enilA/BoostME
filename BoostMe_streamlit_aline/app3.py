import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="BoostMe — Laboratoire d'influenceurs",
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
    "muted":  "rgba(255,255,255,0.70)",
}

# =============================
# PATHS (robustes Streamlit Cloud)
# =============================
BASE_DIR = Path(__file__).resolve().parent                 # BoostMe_streamlit_aline/
DATA_DIR = BASE_DIR / "data"
LOGO_PATH = BASE_DIR / "LOGO_BoostMe.png"
WALLPAPER_PATH = BASE_DIR / "wallpaper.png"


# =============================
# HELPERS
# =============================
def img_to_base64(path: Path) -> str:
    """Encode an image file as base64 for CSS background usage."""
    if not path.exists():
        return ""
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


def inject_css():
    # Wallpaper en background (si présent)
    wp_b64 = img_to_base64(WALLPAPER_PATH)
    if wp_b64:
        # png -> data uri
        wallpaper_css = f"""
        [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient(180deg, rgba(15,15,20,0.40) 0%, rgba(15,15,20,0.40) 100%),
                url("data:image/png;base64,{wp_b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        """
    else:
        wallpaper_css = f"""
        [data-testid="stAppViewContainer"] {{
            background-color: {BOOSTME["bg"]};
        }}
        """

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bungee&family=Inter:wght@400;600;800&display=swap');

        {wallpaper_css}

        /* Main paddings */
        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }}

        /* Cards */
        .bm-card {{
            background: rgba(23,23,36,0.40);
            border: 1px solid {BOOSTME["stroke"]};
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 10px 22px rgba(0,0,0,.20);
            backdrop-filter: blur(6px);
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

        /* Title styles */
        .bm-title {{
            font-family: "Bungee", system-ui, sans-serif;
            font-size: 2.35rem;
            margin: 0;
            line-height: 1.05;
            letter-spacing: 0.5px;
            color: {BOOSTME["text"]};
        }}
        .bm-subtitle {{
            font-family: "Inter", system-ui, sans-serif;
            color: {BOOSTME["muted"]};
            margin-top: 6px;
            font-size: 1.0rem;
        }}
        .bm-divider {{
            height: 1px;
            background: {BOOSTME["stroke"]};
            margin: 14px 0 18px 0;
        }}
        .bm-chip {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.80rem;
            border: 1px solid {BOOSTME["stroke"]};
            color: {BOOSTME["muted"]};
            margin-right: 6px;
            background: rgba(0,0,0,0.12);
            backdrop-filter: blur(6px);
        }}

        /* Plotly container look */
        .stPlotlyChart > div {{
            border-radius: 18px !important;
            border: 1px solid {BOOSTME["stroke"]};
            overflow: hidden;
            background: rgba(23,23,36,0.88);
            padding: 10px;
            backdrop-filter: blur(6px);
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            border-right: 1px solid {BOOSTME["stroke"]};
            background: rgba(15,15,20,0.70);
            backdrop-filter: blur(8px);
        }}

        /* Inputs rounding */
        .stButton>button {{
            border-radius: 12px;
        }}
        div[data-baseweb="select"] > div {{
            border-radius: 12px !important;
        }}

        /* 🔥 Multiselect compact: limite la hauteur de la zone des tags */
        div[data-baseweb="tag"] {{
            background: {BOOSTME["orange"]} !important;
            border: none !important;
            color: #111 !important;
            font-weight: 700 !important;
        }}
        /* zone qui contient les tags -> on limite hauteur + scroll */
        div[data-testid="stMultiSelect"] div {{
            max-height: 120px;
            overflow-y: auto;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


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


def show_header():
    # descend le header pour éviter la barre Streamlit
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 3], vertical_alignment="center")
    with left:
        st.markdown("<div style='padding-top:22px'></div>", unsafe_allow_html=True)
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=180)
        else:
            st.warning("Logo non trouvé : BoostMe_streamlit_aline/LOGO_BoostMe.png")
    with right:
        st.markdown(
            """
            <div style="padding-top:14px">
                <div class="bm-title">BoostMe</div>
                <div class="bm-subtitle">Laboratoire d’influenceurs</div>
                <div style="margin-top:10px">
                    <span class="bm-chip">🚀 Boost</span>
                    <span class="bm-chip">📈 Performance</span>
                    <span class="bm-chip">❤️ Engagement</span>
                    <span class="bm-chip">💬 Communauté</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('<div class="bm-divider"></div>', unsafe_allow_html=True)


@st.cache_data
def load_data():
    missing = [str(DATA_DIR / f) for f in ["cats.csv", "chaines.csv", "videos.csv"] if not (DATA_DIR / f).exists()]
    if missing:
        st.error("Fichiers CSV manquants :")
        for m in missing:
            st.write("—", m)
        st.stop()

    cats = pd.read_csv(DATA_DIR / "cats.csv")
    chaines = pd.read_csv(DATA_DIR / "chaines.csv")
    videos = pd.read_csv(DATA_DIR / "videos.csv")
    return cats, chaines, videos


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


def multiselect_with_all(label: str, options: list, default_all: bool = True, key: str = ""):
    """
    Menu déroulant multi-choix, avec boutons 'Tout' / 'Effacer' pour éviter la galère.
    Visuellement compact grâce au CSS.
    """
    if not options:
        return []

    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.button("Tout", key=f"{key}_all"):
            st.session_state[f"{key}_values"] = options
    with col2:
        if st.button("Effacer", key=f"{key}_none"):
            st.session_state[f"{key}_values"] = []

    # init state
    if f"{key}_values" not in st.session_state:
        st.session_state[f"{key}_values"] = options if default_all else []

    vals = st.sidebar.multiselect(
        label,
        options=options,
        default=st.session_state[f"{key}_values"],
        key=f"{key}_ms",
        placeholder=f"Choisir {label.lower()}…"
    )

    # keep state synced
    st.session_state[f"{key}_values"] = vals
    return vals


# =============================
# START APP
# =============================
inject_css()
show_header()

cats, chaines, videos = load_data()
cats = clean_columns(cats)
chaines = clean_columns(chaines)
videos = clean_columns(videos)

# -----------------------------
# Secure columns
# -----------------------------
# chaines engagement rate auto
cand = [c for c in chaines.columns if "engagement" in c and "rate" in c]
if not cand:
    st.error("Je ne trouve aucune colonne 'engagement' + 'rate' dans chaines.")
    st.write("Colonnes chaines :", list(chaines.columns))
    st.stop()
engagement_col = cand[0]
if engagement_col != "engagement_rate_pct":
    chaines.rename(columns={engagement_col: "engagement_rate_pct"}, inplace=True)
chaines["engagement_rate_pct"] = pd.to_numeric(chaines["engagement_rate_pct"], errors="coerce")

# videos taux engagement auto
eng_cand = [c for c in videos.columns if "taux" in c and "engagement" in c]
if not eng_cand:
    st.error("Je ne trouve pas la colonne de taux d'engagement dans videos.")
    st.write("Colonnes videos :", list(videos.columns))
    st.stop()
taux_eng_col = eng_cand[0]
if taux_eng_col != "taux_engagement_pct":
    videos.rename(columns={taux_eng_col: "taux_engagement_pct"}, inplace=True)
videos["taux_engagement_pct"] = pd.to_numeric(videos["taux_engagement_pct"], errors="coerce")

# -----------------------------
# Calculated columns
# -----------------------------
videos["published_at"] = pd.to_datetime(videos["published_at"], errors="coerce")
videos["heure_publication"] = videos["published_at"].dt.hour
videos["jour_semaine_num"] = videos["published_at"].dt.weekday
jours_map = {0:"Lundi",1:"Mardi",2:"Mercredi",3:"Jeudi",4:"Vendredi",5:"Samedi",6:"Dimanche"}
videos["jour_semaine"] = videos["jour_semaine_num"].map(jours_map)
ordre_jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
videos["jour_semaine"] = pd.Categorical(videos["jour_semaine"], categories=ordre_jours, ordered=True)
videos["annee"] = videos["published_at"].dt.year
videos["engagement_total"] = videos.get("likes", 0).fillna(0) + videos.get("comments", 0).fillna(0)

# -----------------------------
# Joins
# -----------------------------
videos = videos.merge(
    cats[["category_id", "name"]],
    on="category_id",
    how="left"
).rename(columns={"name": "categorie"})


chaines_for_merge = chaines.rename(columns={"title": "chaine"}) if "title" in chaines.columns else chaines.copy()
videos = videos.merge(
    chaines_for_merge[["id", "chaine", "country", "subscribers", "engagement_rate_pct", "nb_videos"]],
    left_on="channel_id",
    right_on="id",
    how="left",
    suffixes=("", "_chaine")
)

# =============================
# SIDEBAR FILTERS (Dropdown multi + compact)
# =============================
st.sidebar.markdown("## 🎛️ Filtres")

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)

annees_opts = sorted(videos["annee"].dropna().unique())
categories_opts = sorted(videos["categorie"].dropna().unique())
chaines_opts = sorted(videos["chaine"].dropna().unique())
jours_opts = list(videos["jour_semaine"].cat.categories)

annees = multiselect_with_all("Année", annees_opts, default_all=True, key="annees")
categories = multiselect_with_all("Catégories", categories_opts, default_all=True, key="categories")
chaines_sel = multiselect_with_all("Chaînes", chaines_opts, default_all=True, key="chaines")
jours_sel = multiselect_with_all("Jour de publication", jours_opts, default_all=True, key="jours")

heures = st.sidebar.slider("Heure de publication", 0, 23, (0, 23))

df = videos[
    (videos["annee"].isin(annees)) &
    (videos["categorie"].isin(categories)) &
    (videos["chaine"].isin(chaines_sel)) &
    (videos["jour_semaine"].isin(jours_sel)) &
    (videos["heure_publication"].between(heures[0], heures[1]))
].copy()

# =============================
# KPIs
# =============================
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("📹 Vidéos analysées", f"{len(df):,}", BOOSTME["orange"])
with k2:
    v = f"{df['views'].mean():,.0f}" if len(df) and "views" in df.columns else "0"
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
st.subheader("📊 Moyenne de vues par catégorie")
cat_views = (
    df.groupby("categorie", as_index=False)["views"]
    .mean()
    .sort_values("views", ascending=False)
) if len(df) and "categorie" in df.columns and "views" in df.columns else pd.DataFrame(columns=["categorie", "views"])

fig_cat = px.bar(cat_views, x="categorie", y="views", title=None)
fig_cat.update_traces(marker_color=BOOSTME["orange"])
fig_cat.update_layout(
    paper_bgcolor="rgba(23,23,36,0.88)",
    plot_bgcolor="rgba(23,23,36,0.88)",
    font_color=BOOSTME["text"],
    xaxis_title=None,
    yaxis_title="Vues moyennes",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_cat, use_container_width=True)

st.subheader("⏰ Engagement moyen par heure")
hour_eng = (
    df.groupby("heure_publication", as_index=False)["taux_engagement_pct"]
    .mean()
    .sort_values("heure_publication")
) if len(df) else pd.DataFrame(columns=["heure_publication", "taux_engagement_pct"])

fig_hour = px.line(hour_eng, x="heure_publication", y="taux_engagement_pct", markers=True, title=None)
fig_hour.update_traces(line_color=BOOSTME["violet"])
fig_hour.update_layout(
    paper_bgcolor="rgba(23,23,36,0.88)",
    plot_bgcolor="rgba(23,23,36,0.88)",
    font_color=BOOSTME["text"],
    xaxis_title="Heure",
    yaxis_title="Taux d'engagement (%)",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_hour, use_container_width=True)

st.subheader("📅 Engagement moyen par jour")
day_eng = (
    df.groupby("jour_semaine", as_index=False)["taux_engagement_pct"]
    .mean()
    .sort_values("jour_semaine")
) if len(df) else pd.DataFrame(columns=["jour_semaine", "taux_engagement_pct"])

fig_day = px.line(day_eng, x="jour_semaine", y="taux_engagement_pct", markers=True, title=None)
fig_day.update_traces(line_color=BOOSTME["rose"])
fig_day.update_layout(
    paper_bgcolor="rgba(23,23,36,0.88)",
    plot_bgcolor="rgba(23,23,36,0.88)",
    font_color=BOOSTME["text"],
    xaxis_title=None,
    yaxis_title="Taux d'engagement (%)",
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_day, use_container_width=True)

st.subheader("🏆 Top chaînes (interactions)")
top_chaines = (
    df.groupby("chaine", as_index=False)["engagement_total"]
    .sum()
    .sort_values("engagement_total", ascending=False)
    .head(15)
) if len(df) else pd.DataFrame(columns=["chaine", "engagement_total"])

fig_top = px.bar(top_chaines, x="engagement_total", y="chaine", orientation="h", title=None)
fig_top.update_traces(marker_color=BOOSTME["jaune"])
fig_top.update_layout(
    paper_bgcolor="rgba(23,23,36,0.88)",
    plot_bgcolor="rgba(23,23,36,0.88)",
    font_color=BOOSTME["text"],
    xaxis_title="Interactions",
    yaxis_title=None,
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_top, use_container_width=True)

# =============================
# TABLE + DEBUG
# =============================
with st.expander("🔎 Explorer les données filtrées"):
    st.dataframe(df, use_container_width=True)

with st.expander("🛠️ Debug (paths)"):
    st.write("BASE_DIR :", str(BASE_DIR))
    st.write("DATA_DIR :", str(DATA_DIR))
    st.write("WALLPAPER exists:", WALLPAPER_PATH.exists())
    st.write("LOGO exists:", LOGO_PATH.exists())
    st.write("CSV détectés :", [p.name for p in DATA_DIR.glob("*.csv")] if DATA_DIR.exists() else "DATA_DIR introuvable")
