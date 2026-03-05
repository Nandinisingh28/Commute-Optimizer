import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from geopy.distance import geodesic
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings("ignore")

# ── Constants ────────────────────────────────────────────────────────────────
CHRIST_LAT = 12.9344041
CHRIST_LNG = 77.6061810
CHRIST_NAME = "CHRIST University, Central Campus"
DATA_FILE = "students.csv"

BANGALORE_LOCALITIES = [
    "Whitefield", "Marathahalli", "Electronic City", "Koramangala",
    "BTM Layout", "HSR Layout", "Indiranagar", "Jayanagar",
    "Banashankari", "Yelahanka", "Hebbal", "Rajajinagar",
    "Malleshwaram", "Nagarbhavi", "JP Nagar", "Bannerghatta Road",
    "Bommanahalli", "Bellandur", "Sarjapur Road", "KR Puram"
]

LOCALITY_COORDS = {
    "Whitefield":        (12.9698, 77.7500),
    "Marathahalli":      (12.9591, 77.7011),
    "Electronic City":   (12.8458, 77.6603),
    "Koramangala":       (12.9352, 77.6245),
    "BTM Layout":        (12.9166, 77.6101),
    "HSR Layout":        (12.9116, 77.6389),
    "Indiranagar":       (12.9784, 77.6408),
    "Jayanagar":         (12.9259, 77.5937),
    "Banashankari":      (12.9252, 77.5644),
    "Yelahanka":         (13.1007, 77.5963),
    "Hebbal":            (13.0359, 77.5970),
    "Rajajinagar":       (12.9914, 77.5556),
    "Malleshwaram":      (13.0035, 77.5704),
    "Nagarbhavi":        (12.9548, 77.5027),
    "JP Nagar":          (12.9102, 77.5900),
    "Bannerghatta Road": (12.8777, 77.5966),
    "Bommanahalli":      (12.8975, 77.6434),
    "Bellandur":         (12.9341, 77.6735),
    "Sarjapur Road":     (12.9129, 77.6853),
    "KR Puram":          (13.0089, 77.6952),
}

SPEED_KMPH = {
    "Metro": 35,
    "Bus":   18,
    "Bike":  22,
    "Car":   20,
}

CLUSTER_COLORS = [
    "red", "blue", "green", "purple", "orange",
    "darkred", "darkblue", "darkgreen", "cadetblue", "pink"
]


# ── SVG Icons ────────────────────────────────────────────────────────────────
SVG_ICONS = {
    "Metro": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"'
        ' viewBox="0 0 24 24" fill="none" stroke="#1a73e8" stroke-width="2"'
        ' stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="3" width="18" height="14" rx="3"/>'
        '<circle cx="8" cy="17" r="2"/>'
        '<circle cx="16" cy="17" r="2"/>'
        '<line x1="8" y1="15" x2="8" y2="17"/>'
        '<line x1="16" y1="15" x2="16" y2="17"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
        '<line x1="9" y1="3" x2="9" y2="10"/>'
        '<line x1="15" y1="3" x2="15" y2="10"/>'
        '</svg>'
    ),
    "Bus": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"'
        ' viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2"'
        ' stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="4" width="20" height="14" rx="2"/>'
        '<circle cx="7" cy="18" r="2"/>'
        '<circle cx="17" cy="18" r="2"/>'
        '<line x1="7" y1="16" x2="7" y2="18"/>'
        '<line x1="17" y1="16" x2="17" y2="18"/>'
        '<line x1="2" y1="11" x2="22" y2="11"/>'
        '<line x1="8" y1="4" x2="8" y2="11"/>'
        '<line x1="16" y1="4" x2="16" y2="11"/>'
        '</svg>'
    ),
    "Bike": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"'
        ' viewBox="0 0 24 24" fill="none" stroke="#e65100" stroke-width="2"'
        ' stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="5.5" cy="17.5" r="3.5"/>'
        '<circle cx="18.5" cy="17.5" r="3.5"/>'
        '<polyline points="6.5,8 12,8 16,14 18.5,14"/>'
        '<polyline points="12,8 10,14 6.5,14"/>'
        '<path d="M14,4 h3 l1.5,4"/>'
        '<line x1="14" y1="4" x2="10" y2="14"/>'
        '</svg>'
    ),
    "Car": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"'
        ' viewBox="0 0 24 24" fill="none" stroke="#6a1b9a" stroke-width="2"'
        ' stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 17H3a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h16'
        'a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-2"/>'
        '<rect x="7" y="14" width="10" height="6" rx="1"/>'
        '<path d="M5 7l2-4h10l2 4"/>'
        '<circle cx="8" cy="17" r="1.5"/>'
        '<circle cx="16" cy="17" r="1.5"/>'
        '</svg>'
    ),
}

# Leaf SVG for environmental section
LEAF_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"'
    ' viewBox="0 0 24 24" fill="#388e3c">'
    '<path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3'
    'A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2-8 2'
    ' 1-1 5-2 5-2S17 8 8 10"/>'
    '</svg>'
)

MODE_BG    = {"Metro": "#e3f0fb", "Bus": "#e8f5e9", "Bike": "#fff3e0", "Car": "#f3e5f5"}
MODE_COLOR = {"Metro": "#1a73e8", "Bus": "#2e7d32", "Bike": "#e65100", "Car": "#6a1b9a"}


def mode_badge(mode: str) -> str:
    """Returns an inline HTML badge with SVG icon for a transport mode."""
    bg    = MODE_BG.get(mode, "#f5f5f5")
    color = MODE_COLOR.get(mode, "#333")
    svg   = SVG_ICONS.get(mode, "")
    return (
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'background:{bg};color:{color};padding:3px 10px;border-radius:12px;'
        f'font-size:13px;font-weight:600;">{svg} {mode}</span>'
    )


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        # Rename legacy USN column so old CSV files keep working
        # Handle all legacy column name variants
        df.rename(columns={"USN": "Register No.", "Registration No.": "Register No."}, inplace=True)
        # Re-cast coordinate columns to float
        for col in ["Lat", "Lng"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    return pd.DataFrame(
        columns=["Name", "Register No.", "Locality", "Lat", "Lng", "Mode", "Departure", "Phone"]
    )


def save_student(row: dict):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


def estimate_commute(lat, lng, mode):
    dist_km  = geodesic((lat, lng), (CHRIST_LAT, CHRIST_LNG)).km
    speed    = SPEED_KMPH.get(mode, 20)
    time_min = (dist_km / speed) * 60
    stress   = min(100, int((dist_km / 30) * 50 + (time_min / 90) * 50))
    return round(dist_km, 2), round(time_min, 1), stress


def stress_label(score):
    if score < 35:
        return "Low Stress",      "#2e7d32"
    elif score < 65:
        return "Moderate Stress", "#e65100"
    else:
        return "High Stress",     "#c62828"


def co2_saved(dist_km, n_members):
    return round(0.21 * dist_km * (n_members - 1), 2)


# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CHRIST Commute Optimizer",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image("logo.png", width=90)
st.sidebar.title("CHRIST Commute Optimizer")
st.sidebar.markdown("*Smart commute planning for CHRIST University students*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to",
    [
        "Home",
        "Register My Commute",
        "Route Visualizer",
        "Commute Estimator",
        "Carpool Matcher",
        "Campus Dashboard",
    ],
)

st.sidebar.markdown("---")
df = load_data()
st.sidebar.metric("Students Registered", len(df))
st.sidebar.metric("Localities Covered",  df["Locality"].nunique() if len(df) > 0 else 0)


# ═══════════════════════════════════════════════════════════════════
# PAGE 0 — HOME
# ═══════════════════════════════════════════════════════════════════
if page == "Home":
    st.title("Smart Commute Optimizer")
    st.subheader("CHRIST University, Bangalore — Student Commute Intelligence Platform")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered Students", len(df))
    col2.metric("Localities Covered",  df["Locality"].nunique() if len(df) else 0)
    col3.metric("Metro Users",         len(df[df["Mode"] == "Metro"]) if len(df) else 0)
    col4.metric("Bus Commuters",       len(df[df["Mode"] == "Bus"])   if len(df) else 0)

    st.markdown("---")
    st.markdown("#### Transport Modes Supported")
    st.markdown(
        " &nbsp;&nbsp; ".join(mode_badge(m) for m in ["Metro", "Bus", "Bike", "Car"]),
        unsafe_allow_html=True
    )
    st.markdown("")

    st.markdown("""
### What This App Does

**Smart Commute Optimizer** helps CHRIST University students plan their daily commute
intelligently and find carpool partners who live nearby.

| Module | Description |
|--------|-------------|
| Register My Commute | Add your home locality, transport mode, and departure time |
| Route Visualizer    | See your home-to-campus route on an interactive Bangalore map |
| Commute Estimator   | Get estimated travel time, distance and stress score for any locality |
| Carpool Matcher     | Find students near you using KMeans clustering — save money and CO2 |
| Campus Dashboard    | Live analytics on how the entire campus commutes |

---
### How to Use
1. Start by registering your commute in **Register My Commute**
2. Visualize your route in **Route Visualizer**
3. Find your carpool group in **Carpool Matcher**
4. Explore campus trends in **Campus Dashboard**
""")

    st.markdown("### CHRIST University — Campus Location")
    m = folium.Map(location=[CHRIST_LAT, CHRIST_LNG], zoom_start=15)
    folium.Marker(
        [CHRIST_LAT, CHRIST_LNG],
        popup=CHRIST_NAME,
        tooltip="CHRIST University — Central Campus",
        icon=folium.Icon(color="red", icon="graduation-cap", prefix="fa"),
    ).add_to(m)
    st_folium(m, width=700, height=350)


# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — REGISTER
# ═══════════════════════════════════════════════════════════════════
elif page == "Register My Commute":
    st.title("Register My Commute")
    st.markdown("Fill in your details to join the CHRIST Commute Network.")
    st.markdown("---")

    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            name        = st.text_input("Full Name *")
            register_no = st.text_input("Register No. *")
            phone       = st.text_input("Phone Number (optional)")
        with col2:
            locality  = st.selectbox("Home Locality *", BANGALORE_LOCALITIES)
            mode      = st.selectbox("Transport Mode *", ["Metro", "Bus", "Bike", "Car"])
            departure = st.selectbox("Usual Departure Time *", [
                "06:30 AM", "07:00 AM", "07:30 AM", "08:00 AM",
                "08:30 AM", "09:00 AM", "09:30 AM", "10:00 AM"
            ])

        submitted = st.form_submit_button("Register", use_container_width=True)

        if submitted:
            if not name or not register_no:
                st.error("Please fill in Name and Register No.")
            elif register_no in df["Register No."].astype(str).values:
                st.warning(f"Register No. **{register_no}** is already registered.")
            else:
                lat, lng = LOCALITY_COORDS.get(locality, (CHRIST_LAT, CHRIST_LNG))
                save_student({
                    "Name": name, "Register No.": register_no, "Locality": locality,
                    "Lat": lat, "Lng": lng, "Mode": mode,
                    "Departure": departure, "Phone": phone
                })
                dist, time_min, stress = estimate_commute(lat, lng, mode)
                label, _ = stress_label(stress)
                st.success(f"Welcome to the network, **{name}**!")
                c1, c2, c3 = st.columns(3)
                c1.metric("Distance",     f"{dist} km")
                c2.metric("Est. Time",    f"{time_min} min")
                c3.metric("Stress Score", f"{stress}/100  —  {label}")
                st.balloons()

    st.markdown("---")
    st.markdown("### Currently Registered Students")
    df = load_data()
    if len(df):
        # ✅ FIX: was "register_no" (wrong) — corrected to "Register No." (actual column name)
        st.dataframe(
            df[["Name", "Register No.", "Locality", "Mode", "Departure"]].reset_index(drop=True),
            use_container_width=True
        )
    else:
        st.info("No students registered yet. Be the first!")


# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — ROUTE VISUALIZER
# ═══════════════════════════════════════════════════════════════════
elif page == "Route Visualizer":
    st.title("Route Visualizer")
    st.markdown("Visualize any student's home-to-CHRIST route on an interactive map.")
    st.markdown("---")

    df = load_data()

    col1, col2 = st.columns([1, 2])
    with col1:
        view_mode = st.radio(
            "Select View",
            ["View My Route", "View a Specific Student", "View All Students"]
        )
        if view_mode == "View a Specific Student" and len(df):
            selected_name = st.selectbox("Select Student", df["Name"].tolist())
            student = df[df["Name"] == selected_name].iloc[0]
        elif view_mode == "View My Route":
            locality = st.selectbox("Your Locality",       BANGALORE_LOCALITIES)
            mode     = st.selectbox("Your Transport Mode", ["Metro", "Bus", "Bike", "Car"])
            lat, lng = LOCALITY_COORDS[locality]
            student  = {"Name": "You", "Locality": locality,
                        "Lat": lat, "Lng": lng, "Mode": mode}
        else:
            student = None

        st.markdown("<br><strong>Map colour key</strong>", unsafe_allow_html=True)
        for m_name in ["Metro", "Bus", "Bike", "Car"]:
            st.markdown(mode_badge(m_name) + "<br>", unsafe_allow_html=True)

    with col2:
        m = folium.Map(location=[12.9500, 77.6200], zoom_start=12)
        folium.Marker(
            [CHRIST_LAT, CHRIST_LNG],
            popup=CHRIST_NAME,
            tooltip="CHRIST University",
            icon=folium.Icon(color="red", icon="star"),
        ).add_to(m)

        mode_color = {"Metro": "blue", "Bus": "green", "Bike": "orange", "Car": "purple"}

        if view_mode == "View All Students" and len(df):
            for _, row in df.iterrows():
                color = mode_color.get(row["Mode"], "gray")
                folium.Marker(
                    [row["Lat"], row["Lng"]],
                    popup=f"{row['Name']} — {row['Locality']} ({row['Mode']})",
                    tooltip=row["Name"],
                    icon=folium.Icon(color=color, icon="home"),
                ).add_to(m)
                folium.PolyLine(
                    [[row["Lat"], row["Lng"]], [CHRIST_LAT, CHRIST_LNG]],
                    color=color, weight=1.5, opacity=0.5
                ).add_to(m)

        elif student:
            lat, lng = float(student["Lat"]), float(student["Lng"])
            color    = mode_color.get(student["Mode"], "gray")
            folium.Marker(
                [lat, lng],
                popup=f"{student['Name']} — {student['Locality']}",
                tooltip=f"{student['Name']}'s Home",
                icon=folium.Icon(color=color, icon="home"),
            ).add_to(m)
            folium.PolyLine(
                [[lat, lng], [CHRIST_LAT, CHRIST_LNG]],
                color=color, weight=3, opacity=0.8, dash_array="5"
            ).add_to(m)
            dist, time_min, _ = estimate_commute(lat, lng, student["Mode"])
            folium.Marker(
                [(lat + CHRIST_LAT) / 2, (lng + CHRIST_LNG) / 2],
                icon=folium.DivIcon(
                    html=(
                        f'<div style="font-size:11px;background:white;padding:3px 6px;'
                        f'border-radius:4px;border:1px solid #888;">'
                        f'{dist} km | {time_min} min</div>'
                    )
                )
            ).add_to(m)

        st_folium(m, width=700, height=480)

    if student and view_mode != "View All Students":
        lat, lng               = float(student["Lat"]), float(student["Lng"])
        dist, time_min, stress = estimate_commute(lat, lng, student["Mode"])
        label, _               = stress_label(stress)
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Distance",      f"{dist} km")
        c2.metric("Travel Time",   f"{time_min} min")
        c3.metric("Stress Score",  f"{stress}/100")
        c4.metric("Commute Level", label)


# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — COMMUTE ESTIMATOR
# ═══════════════════════════════════════════════════════════════════
elif page == "Commute Estimator":
    st.title("Commute Time Estimator")
    st.markdown("Compare commute times across all transport modes for any Bangalore locality.")
    st.markdown("---")

    locality = st.selectbox("Select Your Home Locality", BANGALORE_LOCALITIES)
    lat, lng = LOCALITY_COORDS[locality]

    results = []
    for mode, speed in SPEED_KMPH.items():
        dist, time_min, stress = estimate_commute(lat, lng, mode)
        label, _ = stress_label(stress)
        results.append({
            "Mode":             mode,
            "Distance (km)":    dist,
            "Est. Time (min)":  time_min,
            "Avg Speed (km/h)": speed,
            "Stress Score":     stress,
            "Stress Level":     label,
        })

    res_df = pd.DataFrame(results)

    st.markdown(f"### Commute from **{locality}** to CHRIST University")

    th_style = (
        "text-align:left;padding:9px 14px;border-bottom:2px solid #ddd;"
        "background:#f5f5f5;font-size:13px;"
    )
    td_style = "padding:9px 14px;border-bottom:1px solid #eee;font-size:13px;"
    cols     = ["Mode", "Distance (km)", "Est. Time (min)", "Avg Speed (km/h)",
                "Stress Score", "Stress Level"]

    table  = "<table style='width:100%;border-collapse:collapse;'><thead><tr>"
    table += "".join(f"<th style='{th_style}'>{c}</th>" for c in cols)
    table += "</tr></thead><tbody>"
    for _, row in res_df.iterrows():
        table += "<tr>"
        for c in cols:
            val = mode_badge(row[c]) if c == "Mode" else str(row[c])
            table += f"<td style='{td_style}'>{val}</td>"
        table += "</tr>"
    table += "</tbody></table>"
    st.markdown(table, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(
            res_df, x="Mode", y="Est. Time (min)",
            color="Est. Time (min)", color_continuous_scale="RdYlGn_r",
            title="Estimated Travel Time by Mode",
            labels={"Est. Time (min)": "Time (min)"}
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            res_df, x="Mode", y="Stress Score",
            color="Stress Score", color_continuous_scale="RdYlGn_r",
            title="Commute Stress Score by Mode",
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    best = res_df.loc[res_df["Est. Time (min)"].idxmin()]
    st.success(f"Best Mode: {best['Mode']} — {best['Est. Time (min)']} minutes to campus")

    st.markdown("---")
    st.markdown("### All Localities — Bus Commute Comparison")
    all_results = []
    for loc in BANGALORE_LOCALITIES:
        la, ln = LOCALITY_COORDS[loc]
        dist, time_min, stress = estimate_commute(la, ln, "Bus")
        all_results.append({"Locality": loc, "Distance (km)": dist,
                             "Bus Time (min)": time_min, "Stress": stress})
    all_df = pd.DataFrame(all_results).sort_values("Distance (km)", ascending=True)
    fig3 = px.bar(
        all_df, x="Locality", y="Bus Time (min)",
        color="Stress", color_continuous_scale="RdYlGn_r",
        title="Bus Commute Time from All Localities to CHRIST"
    )
    fig3.update_xaxes(tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — CARPOOL MATCHER
# ═══════════════════════════════════════════════════════════════════
elif page == "Carpool Matcher":
    st.title("Carpool Cluster Matcher")
    st.markdown("Find students near you using KMeans geographic clustering.")
    st.markdown("---")

    df = load_data()

    if len(df) < 4:
        st.warning(
            "At least 4 students need to be registered for clustering to work. "
            "Please register more students first."
        )
        st.stop()

    max_k      = min(10, len(df) - 1)
    n_clusters = st.slider(
        "Number of Carpool Groups (K)",
        min_value=2, max_value=max_k, value=min(5, max_k)
    )

    coords = df[["Lat", "Lng"]].values
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["Carpool_Group"] = kmeans.fit_predict(coords)

    st.markdown("### Find Your Carpool Group")
    my_name = st.selectbox("Select Your Name", ["-- Select --"] + df["Name"].tolist())

    if my_name != "-- Select --":
        my_row     = df[df["Name"] == my_name].iloc[0]
        my_group   = my_row["Carpool_Group"]
        groupmates = df[df["Carpool_Group"] == my_group].copy()
        others     = groupmates[groupmates["Name"] != my_name]

        st.markdown(f"### You are in **Carpool Group {my_group + 1}**")
        st.markdown(
            f"**{len(groupmates)} students** in your group &nbsp;|&nbsp; "
            f"**{len(others)} potential carpool partners**",
            unsafe_allow_html=True
        )

        dist_km, _, _ = estimate_commute(
            float(my_row["Lat"]), float(my_row["Lng"]), my_row["Mode"]
        )
        saved = co2_saved(dist_km, len(groupmates))
        st.markdown(
            f'<div style="background:#e8f5e9;padding:12px 16px;border-radius:8px;'
            f'border-left:4px solid #388e3c;display:flex;align-items:center;gap:8px;">'
            f'{LEAF_SVG}'
            f'<span>If your group carpools together, you collectively save '
            f'<strong>{saved} kg of CO2</strong> per day.</span></div>',
            unsafe_allow_html=True
        )
        st.markdown("")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("#### Your Carpool Partners")
            for _, partner in others.iterrows():
                with st.expander(f"{partner['Name']} — {partner['Locality']}"):
                    st.markdown(
                        f"**Mode:** {mode_badge(partner['Mode'])}",
                        unsafe_allow_html=True
                    )
                    st.write(f"**Departure:** {partner['Departure']}")
                    if partner["Phone"]:
                        st.write(f"**Phone:** {partner['Phone']}")

        with col2:
            st.markdown("#### Group Map")
            gm = folium.Map(location=[float(my_row["Lat"]), float(my_row["Lng"])],
                            zoom_start=12)
            folium.Marker(
                [CHRIST_LAT, CHRIST_LNG],
                tooltip="CHRIST University",
                icon=folium.Icon(color="red", icon="star")
            ).add_to(gm)
            for _, row in groupmates.iterrows():
                is_me = row["Name"] == my_name
                folium.Marker(
                    [row["Lat"], row["Lng"]],
                    popup=f"{'[You] ' if is_me else ''}{row['Name']} — {row['Locality']}",
                    tooltip=row["Name"],
                    icon=folium.Icon(
                        color="red" if is_me else "blue",
                        icon="user"  if is_me else "home", prefix="fa"
                    )
                ).add_to(gm)
                folium.PolyLine(
                    [[row["Lat"], row["Lng"]], [CHRIST_LAT, CHRIST_LNG]],
                    color="blue", weight=2, opacity=0.5
                ).add_to(gm)
            st_folium(gm, width=500, height=400)

    st.markdown("---")
    st.markdown("### Full Campus Cluster Map")
    st.markdown("Every registered student, coloured by their carpool group.")

    m2 = folium.Map(location=[12.9500, 77.6200], zoom_start=11)
    folium.Marker(
        [CHRIST_LAT, CHRIST_LNG],
        tooltip="CHRIST University",
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m2)

    for _, row in df.iterrows():
        color = CLUSTER_COLORS[int(row["Carpool_Group"]) % len(CLUSTER_COLORS)]
        folium.CircleMarker(
            location=[row["Lat"], row["Lng"]],
            radius=8,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=f"Group {int(row['Carpool_Group'])+1} — {row['Name']} ({row['Locality']})",
            tooltip=f"{row['Name']} | Group {int(row['Carpool_Group'])+1}"
        ).add_to(m2)

    for i, center in enumerate(kmeans.cluster_centers_):
        folium.Marker(
            center,
            tooltip=f"Group {i+1} Centre",
            icon=folium.DivIcon(
                html=(
                    f'<div style="font-size:12px;font-weight:bold;color:white;'
                    f'background:{CLUSTER_COLORS[i % len(CLUSTER_COLORS)]};'
                    f'padding:2px 8px;border-radius:10px;">G{i+1}</div>'
                )
            )
        ).add_to(m2)

    st_folium(m2, width=750, height=480)

    st.markdown("### Student Density Heatmap")
    m3 = folium.Map(location=[12.9500, 77.6200], zoom_start=11)
    HeatMap(df[["Lat", "Lng"]].values.tolist(),
            radius=30, blur=20, min_opacity=0.4).add_to(m3)
    folium.Marker(
        [CHRIST_LAT, CHRIST_LNG],
        tooltip="CHRIST University",
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m3)
    st_folium(m3, width=750, height=400)


# ═══════════════════════════════════════════════════════════════════
# PAGE 5 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════
elif page == "Campus Dashboard":
    st.title("Campus Commute Dashboard")
    st.markdown("Live analytics of how CHRIST students commute every day.")
    st.markdown("---")

    df = load_data()

    if len(df) == 0:
        st.info("No data yet. Register some students first!")
        st.stop()

    total        = len(df)
    avg_dist     = round(df.apply(
        lambda r: geodesic((r["Lat"], r["Lng"]), (CHRIST_LAT, CHRIST_LNG)).km, axis=1
    ).mean(), 2)
    avg_time     = round(df.apply(
        lambda r: geodesic((r["Lat"], r["Lng"]), (CHRIST_LAT, CHRIST_LNG)).km
                  / SPEED_KMPH.get(r["Mode"], 20) * 60, axis=1
    ).mean(), 1)
    top_locality = df["Locality"].value_counts().idxmax()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students",   total)
    c2.metric("Avg Distance",     f"{avg_dist} km")
    c3.metric("Avg Commute Time", f"{avg_time} min")
    c4.metric("Top Locality",     top_locality)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        mode_counts = df["Mode"].value_counts().reset_index()
        mode_counts.columns = ["Mode", "Count"]
        fig_pie = px.pie(
            mode_counts, values="Count", names="Mode",
            title="Transport Mode Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        loc_counts = df["Locality"].value_counts().head(10).reset_index()
        loc_counts.columns = ["Locality", "Count"]
        fig_bar = px.bar(
            loc_counts, x="Count", y="Locality", orientation="h",
            title="Top 10 Student Localities",
            color="Count", color_continuous_scale="Blues"
        )
        fig_bar.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bar, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        dep_counts = df["Departure"].value_counts().sort_index().reset_index()
        dep_counts.columns = ["Time", "Count"]
        fig_dep = px.bar(
            dep_counts, x="Time", y="Count",
            title="Departure Time Distribution",
            color="Count", color_continuous_scale="Oranges"
        )
        fig_dep.update_xaxes(tickangle=45)
        st.plotly_chart(fig_dep, use_container_width=True)

    with col4:
        df["Stress"] = df.apply(
            lambda r: estimate_commute(r["Lat"], r["Lng"], r["Mode"])[2], axis=1
        )
        fig_stress = px.histogram(
            df, x="Stress", nbins=10,
            title="Commute Stress Score Distribution",
            color_discrete_sequence=["#EF553B"]
        )
        fig_stress.add_vline(x=35, line_dash="dash", line_color="green",
                             annotation_text="Low / Medium")
        fig_stress.add_vline(x=65, line_dash="dash", line_color="red",
                             annotation_text="Medium / High")
        st.plotly_chart(fig_stress, use_container_width=True)

    st.markdown("---")
    st.markdown(
        f'<h3 style="display:flex;align-items:center;gap:8px;">'
        f'{LEAF_SVG} Environmental Impact</h3>',
        unsafe_allow_html=True
    )

    total_dist  = df.apply(
        lambda r: geodesic((r["Lat"], r["Lng"]), (CHRIST_LAT, CHRIST_LNG)).km, axis=1
    ).sum()
    co2_solo    = round(0.21 * total_dist, 2)
    co2_carpool = round(0.21 * total_dist / 2.5, 2)
    saved_total = round(co2_solo - co2_carpool, 2)

    e1, e2, e3 = st.columns(3)
    e1.metric("CO2 — All Drive Solo",    f"{co2_solo} kg/day")
    e2.metric("CO2 — With Carpooling",   f"{co2_carpool} kg/day")
    e3.metric("Potential Daily Savings", f"{saved_total} kg CO2")

    st.markdown("---")
    st.markdown("### Full Student Data")
    display_df = df[["Name", "Register No.", "Locality", "Mode", "Departure"]].copy()
    display_df.index += 1
    st.dataframe(display_df, use_container_width=True)
