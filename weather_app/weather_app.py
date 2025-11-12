import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
import requests, json, os
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITIES_FILE = "sweden_cities.json"
HISTORY_FILE = "search_history.json"

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": f"{city},se", "appid": API_KEY, "units": "metric", "lang": "en"}
    try:
        res = requests.get(url, params=params, timeout=8)
        res.raise_for_status()
        data = res.json()
        return {
            "city": data.get("name", city),
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"],
            "condition": data["weather"][0]["description"].capitalize(),
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
        }
    except (requests.RequestException, KeyError):
        return None

def load_cities():
    if not os.path.exists(CITIES_FILE):
        return []
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(entry):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []
    history.append(entry)
    history = history[-100:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except IOError:
        pass

def read_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# === GUI ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🇸🇪 Sweden Weather — Dark")
        self.geometry("520x520")
        self.resizable(False, False)

        top = ctk.CTkFrame(self, corner_radius=0)
        top.pack(fill="x", padx=16, pady=(12,6))

        title = ctk.CTkLabel(top, text="🌤️ Sweden Weather", font=("Helvetica", 20, "bold"))
        title.pack(side="left", padx=6, pady=8)

        history_btn = ctk.CTkButton(top, text="History", width=90, command=self.open_history)
        history_btn.pack(side="right", padx=6, pady=8)

        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        tk_label = ctk.CTkLabel(frame, text="Select a Swedish city:", anchor="w")
        tk_label.pack(fill="x", padx=12, pady=(12,6))

        self.cities = load_cities()
        self.var_city = ctk.StringVar()
        self.combo = ctk.CTkComboBox(frame, values=self.cities, command=self.fetch_weather)
        self.combo.pack(fill="x", padx=12)

        self.result_box = ctk.CTkTextbox(frame, width=460, height=350, corner_radius=8)
        self.result_box.pack(padx=12, pady=(6,12))
        self.result_box.configure(state="disabled")

    def fetch_weather(self, choice=None):
        city = self.var_city.get().strip()
        if not city:
            messagebox.showwarning("Input required", "Please select or type a city name.")
            return

        data = get_weather(city)
        if not data:
            messagebox.showerror("Error", "Failed to fetch weather data. Check your internet or city name.")
            return

        out = [
            f"📍 {data['city']} , Sweden\n",
            f"📝 Condition : {data['condition']}\n",
            f"🌡️ Temperature : {data['temp']} °C\n",
            f"💧 Humidity : {data['humidity']} %\n",
            f"💨 Wind Speed : {data['wind']} m/s\n",
            f"🌅 Sunrise : {data['sunrise']}   🌇 Sunset : {data['sunset']}\n",
            f"\n🕓 Retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        ]

        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "".join(out))
        self.result_box.configure(state="disabled")

        save_history({
            "city": data["city"],
            "temp": data["temp"],
            "condition": data["condition"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def open_history(self):
        history = read_history()
        popup = ctk.CTkToplevel(self)
        popup.title("Search History")
        popup.geometry("480x380")
        popup.resizable(False, False)

        lbl = ctk.CTkLabel(popup, text="Last searches (most recent first):", font=("Helvetica", 14, "bold"))
        lbl.pack(pady=(12,6), padx=12, anchor="w")

        container = ctk.CTkFrame(popup, corner_radius=8)
        container.pack(fill="both", expand=True, padx=12, pady=6)

        txt = ctk.CTkTextbox(container, width=440, height=260)
        txt.pack(padx=8, pady=8)
        txt.configure(state="normal")
        if not history:
            txt.insert("end", "No history yet.")
        else:
            for entry in reversed(history[-100:]):
                txt.insert("end", f"{entry['time']} — {entry['city']} — {entry['temp']}°C — {entry['condition']}\n")
        txt.configure(state="disabled")

        btn_clear = ctk.CTkButton(popup, text="Clear History", command=lambda: self.clear_history(popup, txt))
        btn_clear.pack(pady=8)

    def clear_history(self, popup, txt_widget):
        if messagebox.askyesno("Clear history", "Are you sure you want to clear the search history?"):
            try:
                if os.path.exists(HISTORY_FILE):
                    os.remove(HISTORY_FILE)
                txt_widget.configure(state="normal")
                txt_widget.delete("1.0", "end")
                txt_widget.insert("end", "No history yet.")
                txt_widget.configure(state="disabled")
            except (OSError, IOError) as e:
                messagebox.showerror("Error", f"Failed to clear history: {e}")

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
