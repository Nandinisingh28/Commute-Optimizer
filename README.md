# 🎓Commute Optimizer — CHRIST University

A real-time smart geo application built with Python and Streamlit for CHRIST University students to optimize their daily commute and find carpool partners.

🌐 **Live App:** [commute-optimizer.streamlit.app](https://commute-optimizer.streamlit.app)

---

## 📦 Project Structure

```
Commute-Optimizer/
│
├── app.py              ← Main Streamlit application
├── students.csv        ← Student data (auto-generated + pre-seeded)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🚀 How to Run Locally

### Step 1 — Clone the repository

```bash
git clone https://github.com/Nandinisingh28/Commute-Optimizer.git
cd Commute-Optimizer
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## ☁️ Deployed On Streamlit Cloud

This app is live and publicly accessible at:

> 🔗 **[https://commute-optimizer.streamlit.app](https://commute-optimizer.streamlit.app)**

Deployed via [Streamlit Community Cloud](https://share.streamlit.io) — free hosting directly from this GitHub repository.

---

## 🧩 Modules

| Module | Description |
|--------|-------------|
| 🏠 Home | Overview and CHRIST location map |
| 📋 Register My Commute | Student registration form with instant commute stats |
| 🗺️ Route Visualizer | Interactive Folium map — home to campus routes |
| ⏱️ Commute Estimator | Compare Metro/Bus/Bike/Car times from any locality |
| 🤝 Carpool Matcher | KMeans clustering to group nearby students + CO₂ savings |
| 📊 Campus Dashboard | Live Plotly charts — mode distribution, heatmaps, stress scores |

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| `streamlit` | Web app UI |
| `folium` + `streamlit-folium` | Interactive maps |
| `geopy` | Distance calculation (geodesic) |
| `scikit-learn` | KMeans clustering |
| `plotly` | Interactive charts |
| `pandas` | Data management |

---

## 📚 Assignment Details

- **Course:** Advanced Python Programming (MCA519-3)
- **Component:** 3 — Smart Application Development
- **Type:** Geo Application
- **University:** CHRIST University, Bangalore

---

## 💡 Key Features

- 🗺️ Real Bangalore locality geocoordinates (no paid API)
- 🤝 KMeans carpool clustering with visual group map
- 🔥 Student density heatmap
- 🌱 CO₂ savings calculator
- 📊 Live dashboard updates as students register
- ✅ Pre-seeded with 35 dummy students for demo readiness
