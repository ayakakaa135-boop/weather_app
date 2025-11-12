# Sweden Weather App (Dark GUI) — Updated

A dark-mode weather application for Swedish cities using **CustomTkinter** and **OpenWeatherMap API**, updated with best practices.

## Contents
- `weather_app.py` — Main app with dark interface, search history, CTkComboBox, and API key protection.  
- `generate_cities.py` — Downloads all Swedish cities from GeoNames and generates `sweden_cities.json`.  
- `sweden_cities.json` — Starter list of Swedish cities.  
- `requirements.txt` — Required packages (`customtkinter`, `requests`, `python-dotenv`).  
- `.gitignore` — Excludes `.env` and `search_history.json`.  
- `.env` — Stores your API key locally (do not push to GitHub).

---

## Installation
1. Extract the files to any folder on your computer.  
2. Install dependencies:
```bash
pip install -r requirements.txt
