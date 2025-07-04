import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import collections
import ast
import folium
from streamlit_folium import st_folium


# Configuration de la page
st.set_page_config(page_title="Dashboard Tourisme Maroc", layout="wide")

# Dictionnaire des thèmes touristiques et mots-clés associés
tourism_terms = {
      'Attractions Naturelles': [
        'desert', 'sahara', 'dunes', 'oasis', 'valley',
        'atlas', 'anti-atlas', 'mountains', 'high atlas', 'middle atlas',
        'beach', 'coast', 'sea', 'ocean', 'waterfall', 'agafay', 'palm grove',
        'nature', 'canyon', 'gorge'
    ],

    'Sites Culturels': [
        'medina', 'kasbah', 'kasbahs', 'mosque', 'koutoubia', 'palace', 'bahia',
        'el badi', 'madrasa', 'museum', 'souk', 'bazaar', 'market', 'hammam',
        'fortress', 'ramparts', 'ruins', 'old town', 'unesco site', 'architecture'
    ],

    'Activités': [
        'tour', 'trip', 'visit', 'guide', 'guided tour', 'excursion',
        'trekking', 'hiking', 'quad', 'camel ride', 'camel trekking', 'camping',
        'shopping', 'exploring', 'photography','hammam',
        'surfing', 'spa', 'wellness', 'cooking class', 'henna', 'yoga','gnawa'
    ],

    'Hébergement': [
        'hotel', 'riad', 'hostel', 'guesthouse', 'accommodation', 'stay',
        'room', 'suite', 'lodge', 'camp', 'tent', 'resort', 'airbnb',
        'booking', 'check-in', 'check out', 'reception'
    ],

    'Nourriture & Boissons': [
        'food', 'restaurant', 'cuisine', 'gastronomy', 'tajine', 'tagine',
        'couscous', 'mint tea', 'mint', 'tea', 'coffee', 'street food',
        'bread', 'mechoui', 'pastilla', 'sweets', 'pastry', 'breakfast',
        'dinner', 'meal', 'snack', 'drink', 'orange juice'
    ],

    'Transport': [
        'airport', 'flight', 'train', 'bus', 'taxi', 'car', 'car rental',
        'driving', 'tgv', 'ctm', 'supratours', 'petit taxi', 'grand taxi',
        'motorbike', 'scooter', 'road trip', 'transport', 'public transport'
    ],
    
    'Sécurité': [
        'safety', 'police', 'emergency', 'scam', 'pickpocket', 'theft',
        'travel advisory', 'security check', 'border control', 'visa',
        'passport', 'travel insurance', 'health', 'vaccination', 'covid',
        'first aid', 'local laws', 'customs', 'authorities', 'crime',
        'safe areas', 'unsafe areas', 'night safety', 'solo travel',
        'female travel', 'child safety', 'crowds', 'protest', 'demonstration'
    ]
}

# Fonction de filtrage par thème (si 'themes' est une liste)
def match_selected_themes(theme_list, selected_themes):
    return any(theme in theme_list for theme in selected_themes)

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("./Data/maroc_villes.csv")
    df["content"] = df["content"].fillna("").astype(str)
    
    # Convertir les chaînes de listes en vraies listes (si nécessaire)
    if df["themes"].apply(lambda x: isinstance(x, str)).all():
        df["themes"] = df["themes"].apply(ast.literal_eval)
    
    return df

df = load_data()

# Titre principal
st.title("Dashboard Interactif - Tourisme au Maroc (Reddit Data)")

# Statistiques générales
st.subheader("📌 Statistiques générales")
col1, col2, col3 = st.columns(3)
col1.metric("Messages touristiques", f"{len(df):,}")
col2.metric("Villes uniques", df[df['lieu_type'] == 'Ville']['city'].nunique())
col3.metric("Villages uniques", df[df['lieu_type'] == 'Village']['city'].nunique())

# Filtres
st.sidebar.header("🔍 Filtres")
lieu_type = st.sidebar.multiselect("Filtrer par type de lieu :", ["Ville", "Village"])

# Adapter dynamiquement les villes à filtrer selon le type de lieu sélectionné
filtered_df_villes = df[df['lieu_type'].isin(lieu_type)] if lieu_type else df
villes_possibles = sorted(filtered_df_villes['city'].unique())
villes = st.sidebar.multiselect("Filtrer par ville :", villes_possibles)

themes = st.sidebar.multiselect("Filtrer par thème touristique :", list(tourism_terms.keys()))
sentiments = st.sidebar.multiselect("Filtrer par sentiment :", ["Positif", "Neutre", "Négatif"])

# Application des filtres
filtered_df = df.copy()
if lieu_type:
    filtered_df = filtered_df[filtered_df["lieu_type"].isin(lieu_type)]
if villes:
    filtered_df = filtered_df[filtered_df["city"].isin(villes)]
if themes:
    filtered_df = filtered_df[filtered_df["themes"].apply(lambda x: match_selected_themes(x, themes))]
if sentiments:
    filtered_df = filtered_df[filtered_df["sentiment"].isin(sentiments)]

# Graphique : Top 10 villes
st.subheader("🏙️ Nombre d'avis par ville")
top_cities = filtered_df["city"].value_counts().head(10)
fig1, ax1 = plt.subplots()
sns.barplot(x=top_cities.values, y=top_cities.index, palette="Blues_d", ax=ax1)
ax1.set_xlabel("Nombre d'avis")
ax1.set_ylabel("Ville")
st.pyplot(fig1)

# Graphique : Répartition des thèmes
st.subheader("🎯 Répartition des thèmes touristiques")
theme_counts = filtered_df["themes"].explode().value_counts()
fig2, ax2 = plt.subplots()
theme_counts.plot(kind='bar', color='mediumseagreen', ax=ax2)
ax2.set_title("Nombre d'avis par thème")
ax2.set_xlabel("Thème")
ax2.set_ylabel("Nombre d'avis")
st.pyplot(fig2)

# Graphique : Répartition des sentiments
st.subheader("📈 Répartition des sentiments")
sentiment_counts = filtered_df["sentiment"].value_counts()
fig3, ax3 = plt.subplots()
sentiment_counts.plot(kind='bar', color=['green', 'gray', 'red'], ax=ax3)
ax3.set_title("Distribution des sentiments des avis")
ax3.set_xlabel("Sentiment")
ax3.set_ylabel("Nombre de messages")
st.pyplot(fig3)

# Top 10 mots-clés dans les thèmes sélectionnés
if themes:
    st.subheader("🔑 Top 10 mots-clés dans les thèmes sélectionnés")
    
    keyword_counts = collections.Counter()
    for theme in themes:
        keywords = tourism_terms.get(theme, [])
        for kw in keywords:
            count = filtered_df['content'].str.lower().str.contains(kw).sum()
            if count > 0:
                keyword_counts[kw] += count

    top_keywords = keyword_counts.most_common(10)
    
    if top_keywords:
        kw_labels, kw_values = zip(*top_keywords)
        fig_kw, ax_kw = plt.subplots()
        sns.barplot(x=list(kw_values), y=list(kw_labels), ax=ax_kw, palette="viridis")
        ax_kw.set_xlabel("Occurrences")
        ax_kw.set_ylabel("Mot-clé")
        ax_kw.set_title("Top 10 mots-clés dans les thèmes sélectionnés")
        st.pyplot(fig_kw)
    else:
        st.info("Aucun mot-clé trouvé pour les thèmes sélectionnés.")


# map

# Carte interactive avec Folium
st.subheader("🗺️ Carte des lieux touristiques mentionnés")

# Regrouper les messages par ville avec coordonnées
map_df = (
    filtered_df.dropna(subset=["latitude", "longitude"])
    .groupby(["city", "latitude", "longitude"])
    .size()
    .reset_index(name="message_count")
)

if not map_df.empty:
    # Créer la carte centrée sur le Maroc
    m = folium.Map(location=[31.5, -6.0], zoom_start=5)

    for _, row in map_df.iterrows():
        popup_html = f"""
        <strong>{row['city']}</strong><br>
        {row['message_count']} avis
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup_html,
            tooltip=row["city"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st_folium(m, width=700, height=500)
else:
    st.info("Aucun lieu avec coordonnées à afficher.")

# Aperçu des messages touristiques
st.subheader("📝 Aperçu des avis touristiques")
num_rows = st.slider("Nombre d'avis à afficher :", 1, 20, 5)
for i, row in filtered_df.head(num_rows).iterrows():
    st.markdown(f"**📍 {row['city']} | 🎯 {', '.join(row['themes'])} | 😊 {row['sentiment']}**")
    st.write(row['content'].replace("\\n", "\n"))
    st.markdown("---")
