import streamlit as st
import pandas as pd
import os
from PIL import Image

# 🟢 קונפיגורציה כללית לעמוד
st.set_page_config(page_title="🔗 קשרים בין ערים בישראל", layout="wide")

# 🔵 רקע / באנר עליון
st.markdown("""
    <div style='background-color:#EAF4FF;padding:30px;border-radius:10px;margin-bottom:30px;'>
        <h1 style='color:#003366;text-align:center;'>🔗 קשרים בין ערים בישראל</h1>
        <p style='text-align:center;font-size:18px;'>
            מערכת המלצות אינטראקטיבית: בחר קבוצת תיירים, רף תמיכה וביטחון, ועיר יעד - וקבל תובנות חכמות ומפה אינטראקטיבית.
        </p>
    </div>
""", unsafe_allow_html=True)

# 🟨 טופס בחירה בשלוש עמודות
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        age_group = st.selectbox("👤 קבוצת גיל התייר", ["הכל", "צעירים", "מבוגרים"])
    with col2:
        continent = st.selectbox("🌍 יבשת התייר", ["הכל", "אירופה", "אמריקה"])
    with col3:
        religion = st.selectbox("✡️ דת התייר", ["הכל", "יהודי", "נוצרי"])

# 🟦 הזנת אחוזי תמיכה וביטחון
st.markdown("#### 🎯 הגדרת פרמטרים")
col4, col5 = st.columns(2)
with col4:
    support_threshold = st.number_input("📊 אחוז תמיכה (Support)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
with col5:
    confidence_threshold = st.number_input("🔐 אחוז ביטחון (Confidence)", min_value=0.0, max_value=1.0, value=0.4, step=0.05)

# 🟧 בחירת קובץ
file_name = "directed_association_rules_cities.xlsx"
if age_group != "הכל":
    file_name = "directed_association_rules_young_cities.xlsx" if age_group == "צעירים" else "directed_association_rules_old_cities.xlsx"
elif continent != "הכל":
    file_name = "directed_association_rules_איורפה_cities.xlsx" if continent == "אירופה" else "directed_association_rules_אמריקה_cities.xlsx"
elif religion != "הכל":
    file_name = "directed_association_rules_יהודים_cities.xlsx" if religion == "יהודי" else "directed_association_rules_נוצרים_cities.xlsx"

# 🟩 טעינת הקובץ לפי המסלול
file_path = file_name  

try:
    df = pd.read_excel(file_path)
    st.success(f"✅ הקובץ נטען בהצלחה: {file_name}")
except FileNotFoundError:
    st.error(f"❌ שגיאה: הקובץ לא נמצא ({file_name})")
    st.stop()

# 🟫 בחירת עיר יעד (במקום עיר מוצא)
cities = sorted(df['To'].unique())
destination_city = st.selectbox("🏙️ עיר יעד (אופציונלי)", ["- אין בחירה -"] + cities)

# 🟪 סיכום הבחירה
st.markdown("---")
st.markdown("### 🧾 סיכום הבחירה שלך:")
st.markdown(f"• גיל: {age_group} | יבשת: {continent} | דת: {religion}")
st.markdown(f"• תמיכה: {support_threshold:.1%} | ביטחון: {confidence_threshold:.1%}")
st.markdown(f"• עיר יעד: {destination_city}" if destination_city != "- אין בחירה -" else "• עיר יעד לא נבחרה")

# 🧠 שמירת הנתונים
st.session_state.selected_data = {
    "df": df,
    "support_threshold": support_threshold,
    "confidence_threshold": confidence_threshold,
    "destination_city": None if destination_city == "- אין בחירה -" else destination_city
}

st.markdown("---")

# שלב 2+3
import plotly.graph_objects as go
import numpy as np

if "selected_data" not in st.session_state:
    st.error("המערכת לא טענה נתונים. חזור לשלב הבחירה קודם.")
    st.stop()

selected = st.session_state.selected_data
support_threshold = selected["support_threshold"]
confidence_threshold = selected["confidence_threshold"]
df = selected["df"]
destination_city = selected["destination_city"]

filtered_df = df[(df["Support"] >= support_threshold) & (df["Confidence"] >= confidence_threshold)]

if destination_city:
    filtered_df = filtered_df[filtered_df["To"] == destination_city]

if filtered_df.empty:
    st.warning("לא נמצאו קשרים התואמים את הקריטריונים שבחרת.")
    st.stop()

# הצגת טבלה בלי Intersection ו-Lift, ממוינת לפי Support
st.markdown("### טבלת חוקי אסוציאציה מסוננת")
table_to_show = filtered_df.drop(columns=["Intersection", "Lift"], errors='ignore')
table_to_show = table_to_show.sort_values(by="Support", ascending=False).reset_index(drop=True)
st.dataframe(table_to_show, use_container_width=True)

# מקרא צבעים
st.markdown("### מקרא צבעים לפי Confidence:")
st.markdown("""
<ul style='line-height: 2;'>
  <li><span style='color:#8B0000;'>⬤</span> Confidence ≥ 0.8 – בורדו כהה</li>
  <li><span style='color:#FF0000;'>⬤</span> 0.7–0.79 – אדום</li>
  <li><span style='color:#FFA500;'>⬤</span> 0.6–0.69 – כתום</li>
  <li><span style='color:#FFFF00;'>⬤</span> 0.5–0.59 – צהוב</li>
  <li><span style='color:#1E90FF;'>⬤</span> 0.4–0.49 – כחול</li>
  <li><span style='color:#A9A9A9;'>⬤</span> Confidence &lt; 0.4 – אפור</li>
</ul>
""", unsafe_allow_html=True)

# קואורדינטות
city_coords = {
    'אילת': (29.5581, 34.9482),
    'חיפה': (32.7940, 34.9896),
    'טבריה': (32.7922, 35.5312),
    'ים המלח': (31.5590, 35.4732),
    'ירושלים': (31.7683, 35.2137),
    'נצרת': (32.6996, 35.3035),
    'עכו': (32.9236, 35.0713),
    'קיסריה': (32.5000, 34.9100),
    'תל אביב יפו': (31.9853, 34.6718),
    'תמר': (31.1962, 35.3734)
}

def get_confidence_color(conf):
    if conf >= 0.8:
        return '#8B0000'
    elif conf >= 0.7:
        return '#FF0000'
    elif conf >= 0.6:
        return '#FFA500'
    elif conf >= 0.5:
        return '#FFFF00'
    elif conf >= 0.4:
        return '#1E90FF'
    else:
        return '#A9A9A9'

edges = []
for _, row in filtered_df.iterrows():
    city_from, city_to = row['From'], row['To']
    if city_from in city_coords and city_to in city_coords:
        lat0, lon0 = city_coords[city_from]
        lat1, lon1 = city_coords[city_to]
        conf = row['Confidence']
        support = row['Support']
        color = get_confidence_color(conf)
        width = 1 + 15 * support

        dx = lon1 - lon0
        dy = lat1 - lat0
        norm = np.sqrt(dx**2 + dy**2)
        dx, dy = dx / norm, dy / norm
        x_head = lon1 - dx * 0.1
        y_head = lat1 - dy * 0.1

        edges.append(go.Scattergeo(
            lon=[lon0, lon1],
            lat=[lat0, lat1],
            mode='lines',
            line=dict(width=width, color=color),
            hoverinfo='text',
            text=f"{city_from} → {city_to}<br>Support: {support:.3f}<br>Confidence: {conf:.3f}",
            showlegend=False
        ))

        edges.append(go.Scattergeo(
            lon=[x_head, lon1],
            lat=[y_head, lat1],
            mode='lines',
            line=dict(width=4, color=color),
            hoverinfo='skip',
            showlegend=False
        ))

city_trace = go.Scattergeo(
    lon=[lon for _, lon in city_coords.values()],
    lat=[lat for lat, _ in city_coords.values()],
    text=list(city_coords.keys()),
    mode='markers+text',
    marker=dict(size=8, color='black'),
    textposition='top center'
)

fig = go.Figure(data=edges + [city_trace])
fig.update_layout(
    title="מפת קשרים בין ערים בישראל",
    height=1500,
    geo=dict(
        scope='asia',
        projection_type='mercator',
        showland=True,
        landcolor="rgb(243, 243, 243)",
        countrycolor="rgb(204, 204, 204)",
        lonaxis=dict(range=[34.5, 35.6]),
        lataxis=dict(range=[29.0, 33.5]),
        fitbounds="locations"
    )
)
st.plotly_chart(fig, use_container_width=True)
