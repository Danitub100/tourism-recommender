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
            מערכת המלצות אינטראקטיבית: בחר קבוצת תיירים, רף תמיכה וביטחון, ועיר מוצא - וקבל תובנות חכמות ומפה אינטראקטיבית.
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

# 🟧 לוגיקת בחירת קובץ לפי סינון (רק אחד אמור להיות שונה מהכל)
file_name = "directed_association_rules_cities.xlsx"
if age_group != "הכל":
    file_name = "directed_association_rules_young_cities.xlsx" if age_group == "צעירים" else "directed_association_rules_old_cities.xlsx"
elif continent != "הכל":
    file_name = "directed_association_rules_איורפה_cities.xlsx" if continent == "אירופה" else "directed_association_rules_אמריקה_cities.xlsx"
elif religion != "הכל":
    file_name = "directed_association_rules_יהודים_cities.xlsx" if religion == "יהודי" else "directed_association_rules_נוצרים_cities.xlsx"

# 🟩 טעינת הקובץ לפי המסלול
folder = r"C:\Users\daniel\Desktop\אסוסיאיישן רולס קבוצות"  # שנה בהתאם למחשב שלך
file_path = os.path.join(folder, file_name)

try:
    df = pd.read_excel(file_path)
    st.success(f"✅ הקובץ נטען בהצלחה: {file_name}")
except FileNotFoundError:
    st.error(f"❌ שגיאה: הקובץ לא נמצא ({file_name})")
    st.stop()

# 🟫 בחירת עיר מוצא
cities = sorted(df['From'].unique())
origin_city = st.selectbox("🏙️ עיר מוצא (אופציונלי)", ["- אין בחירה -"] + cities)

# 🟪 הצגת תקציר הבחירה בצורה ברורה
st.markdown("---")
st.markdown("### 🧾 סיכום הבחירה שלך:")
st.markdown(f"• גיל: `{age_group}` | יבשת: `{continent}` | דת: `{religion}`")
st.markdown(f"• תמיכה: `{support_threshold:.1%}` | ביטחון: `{confidence_threshold:.1%}`")
st.markdown(f"• עיר מוצא: `{origin_city}`" if origin_city != "- אין בחירה -" else "• עיר מוצא לא נבחרה")

# 🧠 שמירת הנתונים לשימוש בשלב הבא
st.session_state.selected_data = {
    "df": df,
    "support_threshold": support_threshold,
    "confidence_threshold": confidence_threshold,
    "origin_city": None if origin_city == "- אין בחירה -" else origin_city
}

# 🖼️ תצוגת תמונת רקע או קישוט ויזואלי (אופציונלי)
# אפשר גם להוסיף תמונות של ערים ישראליות בעתיד או באנר עליון
# image = Image.open("background_israel.jpg")
# st.image(image, use_column_width=True)

st.markdown("---")






# שלב 2+3: סינון נתונים והצגת טבלת חוקים + מפת קשרים אינטראקטיבית
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# טען נתונים משלב 1
if "selected_data" not in st.session_state:
    st.error("המערכת לא טענה נתונים. חזור לשלב הבחירה קודם.")
    st.stop()

# חילוץ הנתונים
selected = st.session_state.selected_data
support_threshold = selected["support_threshold"]
confidence_threshold = selected["confidence_threshold"]
df = selected["df"]
origin_city = selected["origin_city"]

# סינון לפי ספים
filtered_df = df[(df["Support"] >= support_threshold) & (df["Confidence"] >= confidence_threshold)]

# סינון לפי עיר מוצא אם נבחרה
if origin_city:
    filtered_df = filtered_df[filtered_df["From"] == origin_city]

# הצגת טבלה
if filtered_df.empty:
    st.warning("לא נמצאו קשרים התואמים את הקריטריונים שבחרת.")
    st.stop()

st.markdown("### טבלת חוקי אסוציאציה מסוננת")
st.dataframe(filtered_df.sort_values(by="Lift", ascending=False).reset_index(drop=True), use_container_width=True)

# מקרא צבעים לפי Confidence
st.markdown("### מקרא צבעים לפי Confidence:")
st.markdown("""
<ul style='line-height: 2;'>
  <li><span style='color:#8B0000;'>⬤</span> Confidence ≥ 0.8 – בורדו כהה</li>
  <li><span style='color:#FF0000;'>⬤</span> 0.7–0.79 – אדום</li>
  <li><span style='color:#FFA500;'>⬤</span> 0.6–0.69 – כתום</li>
  <li><span style='color:#FFFF00;'>⬤</span> 0.5–0.59 – צהוב</li>
  <li><span style='color:#1E90FF;'>⬤</span> 0.4–0.49 – כחול</li>
</ul>
""", unsafe_allow_html=True)

# קואורדינטות ערים
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

# פונקציית צבע לפי Confidence
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

# יצירת קווים עם חיצים
edges = []
for _, row in filtered_df.iterrows():
    city_from, city_to = row['From'], row['To']
    if city_from in city_coords and city_to in city_coords:
        lat0, lon0 = city_coords[city_from]
        lat1, lon1 = city_coords[city_to]
        conf = row['Confidence']
        support = row['Support']
        lift = row['Lift']
        color = get_confidence_color(conf)
        width = 1 + 15 * support

        dx = lon1 - lon0
        dy = lat1 - lat0
        norm = np.sqrt(dx**2 + dy**2)
        dx, dy = dx / norm, dy / norm
        x_head = lon1 - dx * 0.1
        y_head = lat1 - dy * 0.1

        # קו ראשי בין הערים
        edges.append(go.Scattergeo(
            lon=[lon0, lon1],
            lat=[lat0, lat1],
            mode='lines',
            line=dict(width=width, color=color),
            hoverinfo='text',
            text=f"{city_from} → {city_to}<br>Support: {support:.3f}<br>Confidence: {conf:.3f}<br>Lift: {lift:.3f}",
            showlegend=False
        ))

        # ראש חץ
        edges.append(go.Scattergeo(
            lon=[x_head, lon1],
            lat=[y_head, lat1],
            mode='lines',
            line=dict(width=4, color=color),
            hoverinfo='skip',
            showlegend=False
        ))

# ציור הערים
city_trace = go.Scattergeo(
    lon=[lon for _, lon in city_coords.values()],
    lat=[lat for lat, _ in city_coords.values()],
    text=list(city_coords.keys()),
    mode='markers+text',
    marker=dict(size=8, color='black'),
    textposition='top center'
)

# תיחום גאוגרפי מדויק לישראל
fig = go.Figure(data=edges + [city_trace])
fig.update_layout(
    title="מפת קשרים בין ערים בישראל",
    height=1500,  # הגדלת גובה המפה
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
