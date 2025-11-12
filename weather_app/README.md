
# Sweden Weather App (Dark GUI)

This is a dark-mode GUI weather application focused on Sweden. It uses OpenWeatherMap API to fetch live weather for Swedish cities.

## Contents
- `weather_app.py` — Main GUI application (CustomTkinter)
- `generate_cities.py` — Use this to download a complete list of Swedish populated places from GeoNames and generate `sweden_cities.json`
- `sweden_cities.json` — Starter list of common Swedish cities
- `requirements.txt` — Required packages

## How to use
1. Install dependencies:
```
pip install -r requirements.txt
```
2. (Optional) Generate the full city list (recommended for full coverage):
```
python generate_cities.py
```
This will download data from GeoNames and create `sweden_cities.json` with many Swedish place names.

3. Run the app:
```
python weather_app.py
```

The app saves search history to `search_history.json` and you can view it using the "History" button in the app.

---
Note: The bundled starter `sweden_cities.json` contains common cities so you can run the app immediately.
