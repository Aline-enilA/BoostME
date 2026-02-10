import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Boost Me – Labo d'influence",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------
# 1) Chargement des données
# -----------------------------
@st.cache_data
def load_data():
    cats = pd.read_csv("data/cats.csv")
    chaines = pd.read_csv("data/chaines.csv")
    videos = pd.read_csv("data/videos.csv", parse_dates=["published_at"])
    return cats, chaines, videos

cats, chaines, videos = load_data()

# -----------------------------
# 2) Nettoyage des colonnes
# -----------------------------
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

# --- Sécuriser la colonne taux d'engagement dans videos ---
eng_candidates = [c for c in videos.columns if "taux" in c and "engagement" in c]
if len(eng_candidates) == 0:
    st.error("Je ne trouve pas la colonne de taux d'engagement dans videos.")
    st.write("Colonnes videos :", list(videos.columns))
    st.stop()

taux_eng_col = eng_candidates[0]

# Normaliser le nom pour la suite du code
if taux_eng_col != "taux_engagement_pct":
    videos.rename(columns={taux_eng_col: "taux_engagement_pct"}, inplace=True)

# (optionnel) s'assurer que c'est bien numérique
videos["taux_engagement_pct"] = pd.to_numeric(videos["taux_engagement_pct"], errors="coerce")


# -----------------------------
# 3) Sécuriser la colonne engagement_rate dans chaines (auto)
# -----------------------------
# On cherche une colonne qui contient "engagement" et "rate"
candidates = [c for c in chaines.columns if "engagement" in c and "rate" in c]

if len(candidates) == 0:
    st.error("Je ne trouve aucune colonne 'engagement' + 'rate' dans la table chaines.")
    st.write("Colonnes chaines :", list(chaines.columns))
    st.stop()

engagement_col = candidates[0]  # on prend la 1ère trouvée

# (optionnel) normaliser le nom dans chaines pour simplifier la suite
if engagement_col != "engagement_rate_pct":
    chaines.rename(columns={engagement_col: "engagement_rate_pct"}, inplace=True)

# -----------------------------
# 4) Colonnes calculées à partir de published_at
# -----------------------------
videos["published_at"] = pd.to_datetime(videos["published_at"], errors="coerce")

videos["heure_publication"] = videos["published_at"].dt.hour
videos["jour_semaine_num"] = videos["published_at"].dt.weekday

jours_map = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche"
}
videos["jour_semaine"] = videos["jour_semaine_num"].map(jours_map)

ordre_jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
videos["jour_semaine"] = pd.Categorical(videos["jour_semaine"], categories=ordre_jours, ordered=True)

videos["annee"] = videos["published_at"].dt.year

videos["engagement_total"] = videos["likes"].fillna(0) + videos["comments"].fillna(0)

# -----------------------------
# 5) Jointures
# -----------------------------

# Vidéos ↔ Catégories
# (dans cats, la clé est souvent category_id et pas id)
videos = videos.merge(
    cats[["category_id", "name"]],
    on="category_id",
    how="left"
).rename(columns={"name": "categorie"})

# Vidéos ↔ Chaînes
# Préparer une table chaines pour la jointure (on évite le conflit sur "title")
chaines_for_merge = chaines.rename(columns={"title": "chaine"})

videos = videos.merge(
    chaines_for_merge[["id", "chaine", "country", "subscribers", "engagement_rate_pct", "nb_videos"]],
    left_on="channel_id",
    right_on="id",
    how="left",
    suffixes=("", "_chaine")
)

# Sidebar (filtres) + KPIs + 1ers graphiques
st.sidebar.title("🎯 Filtres Boost Me")

# Filtres
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

heures = st.sidebar.slider(
    "Heure de publication",
    0, 23, (0, 23)
)

# Data filtrée (la base de tout le dashboard)
df = videos[
    (videos["annee"].isin(annees)) &
    (videos["categorie"].isin(categories)) &
    (videos["chaine"].isin(chaines_sel)) &
    (videos["jour_semaine"].isin(jours_sel)) &
    (videos["heure_publication"].between(heures[0], heures[1]))
].copy()

# kpi clé en haut 
st.title("🚀 Boost Me — Analyse des tendances YouTube")

k1, k2, k3, k4 = st.columns(4)

k1.metric("📹 Vidéos analysées", f"{len(df):,}")
k2.metric("👀 Vues moyennes / vidéo", f"{df['views'].mean():,.0f}" if len(df) else "0")
k3.metric("⚡ Engagement moyen", f"{df['taux_engagementpct'].mean():.2f} %" if len(df) else "0")
k4.metric("💬 Interactions totales", f"{df['engagement_total'].sum():,.0f}" if len(df) else "0")

# graphique
st.subheader("📊 Moyenne de vues par catégorie")

cat_views = (
    df.groupby("categorie", as_index=False)["views"]
    .mean()
    .sort_values("views", ascending=False)
)

fig_cat = px.bar(
    cat_views,
    x="categorie",
    y="views"
)

st.plotly_chart(fig_cat, use_container_width=True)

# engagement par heure de publication
st.subheader("⏰ Engagement moyen par heure")

hour_eng = (
    df.groupby("heure_publication", as_index=False)["taux_engagementpct"]
    .mean()
    .sort_values("heure_publication")
)

fig_hour = px.line(
    hour_eng,
    x="heure_publication",
    y="taux_engagementpct",
    markers=True
)

st.plotly_chart(fig_hour, use_container_width=True)

# engagement par jour de la semaine
st.subheader("📅 Engagement moyen par jour")

day_eng = (
    df.groupby("jour_semaine", as_index=False)["taux_engagementpct"]
    .mean()
    .sort_values("jour_semaine")
)

fig_day = px.line(
    day_eng,
    x="jour_semaine",
    y="taux_engagementpct",
    markers=True
)

st.plotly_chart(fig_day, use_container_width=True)

# top chaine/influenceur par intéraction
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
    orientation="h"
)

st.plotly_chart(fig_top, use_container_width=True)
                              
# table exploratoire
with st.expander("🔎 Explorer les données filtrées"):
    st.dataframe(df, use_container_width=True)



# -----------------------------
# 6) Debug / vérification
# -----------------------------
st.write("Colonnes videos :", list(videos.columns))
st.dataframe(videos[["title", "chaine", "categorie", "views"]].head(10))


