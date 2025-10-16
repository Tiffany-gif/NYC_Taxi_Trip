# NYC Taxi Trip Mobility Dashboard

## Overview

The **NYC Taxi Trip Mobility Dashboard** is a fullstack data-driven web application designed to explore, analyze, and visualize urban mobility patterns in New York City.  
It leverages the official **NYC Taxi Trip Dataset**, which contains detailed trip records including timestamps, distances, fares, and coordinates.

The system was built to demonstrate data engineering, backend API development, and frontend visualization capabilities — offering an interactive platform for users to understand how the city moves.

---

## Project Structure

```
NYC_Taxi_Trip/
│
├── backend/
│   ├── api/
│   │   ├── trip_endpoints.py
│   │   ├── insights_endpoints.py
│   ├── data/
│   │   ├── cleaned/
│   │         ├── cleaned_trips.csv
│   │         ├── feautured_trips.csv
│   │   ├── logs/
│   │         └──  excluded_records.log
│   │   ├── raw/
│   │         └── train.csv
│   │   ├── db_insert.py
│   ├── utils/
│   │   ├── feature_engineering.py
│   │   ├── anomaly_detection.py
│   │   ├── data_cleaning.py
│   │   ├── db_test.py
│   │   └── db_insert.py
│   ├── config/
│   │   ├── db_connection.py
│   │   └── db_config.py
│   ├── app.py
│   ├── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── script.js/
│   ├── styles.css/
│
├── docs/
│   ├── ERD.png
│   ├── report.pdf
│
├── scripts/
│   ├── ingest_csv.py
│
├── README.md
├── .gitattributes
└── .gitignore
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Tiffany-gif/NYC_Taxi_Trip.git
cd NYC_Taxi_Trip
```

---

### 2. Backend Setup

#### Create a Virtual Environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # (On Windows: .venv\Scripts\activate)
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure the Database

Edit your database credentials in:
```
backend/config/db_config.py
```

Make sure your database (e.g. MySQL or PostgreSQL) is running and that you’ve executed your schema file (e.g. `database_setup.sql`):

```sql
CREATE DATABASE trip_data;
USE trip_data;
```

---

### 3. Load and Process the Dataset

Place your raw CSV file in:
```
data/raw/train.csv
```

Run the cleaning and feature engineering scripts:

```bash
cd backend/utils
python3 data_cleaning.py
```

This will:
- Clean the raw dataset
- Create derived features (e.g., speed, fare per km, estimated fare)
- Log removed or invalid records to `/data/logs/excluded_records.log`
- Save the final dataset to `/data/cleaned/featured_trips.csv`

---

### 4. Start the Backend Server (Flask)

From the `backend` directory:

```bash
python3 app.py
```

If successful, you’ll see something like:

```
 * Running on http://127.0.0.1:5000
```

Your API endpoints (examples):
- `/api/trips` — Fetch filtered or all trip data  
- `/api/insights` — Get analytics summaries (average duration, busiest times, etc.)

---

### 5. Frontend Setup

Open a new terminal and navigate to the `frontend` folder:

```bash
cd frontend
```

If using vanilla HTML/CSS/JS:
Just open `index.html` in your browser.

If using React or a framework:
```bash
npm install
npm start
```

The frontend will connect to your Flask backend via API calls.

---

## 📊 Example Features and Insights

- **Trip Efficiency Algorithm** — Custom ranking of trip speeds and durations  
- **Anomaly Detection** — Detect outlier trips using a hand-coded logic (no external ML libs)  
- **Data Visualization** — Charts and maps displaying patterns in pickup density, trip speeds, and fares

---

## 🧠 Custom Algorithm

A manually implemented efficiency ranking algorithm was created to evaluate trip performance without relying on libraries like `heapq` or `sort_values`.

**Logic:** Sort trips by their average speed (distance/time) and flag outliers for review.  
**Complexity:** O(n log n) for sorting; O(n) for filtering.

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Python (Flask), SQL (MySQL) |
| Frontend | HTML, CSS, JS |
| Database | MySQL |

---

## Contributors

| Name | Role |
|------|------|
| Emma Tiffany Umwari | Backend & Data Processing |
| Julius Kate Lorna Iriza| Frontend & Documentation |
| Keyla Bineza Nyacyesa | Database Design & Integration |

---

## Future Improvements

- Implement advanced anomaly detection (e.g. clustering)
- Add user authentication for personalized dashboards
- Integrate live traffic data for prediction
- Deploy to cloud (AWS / GCP)

---

## License

This project is licensed under the MIT License — feel free to use and adapt it for educational or research purposes.

---

© 2025 NYC Mobility Team — All Rights Reserved.
