import customtkinter as ctk
from tkinter import ttk, messagebox
import requests, json, os
from datetime import datetime

# ------------------ Configuration ------------------
API_KEY = "43cc0509a8c7ee85344e896f52f66547"
CITIES_FILE = "sweden_cities.json"
HISTORY_FILE = "search_history.json"

# ------------------ Helpers ------------------
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
    except requests.RequestException as e:
        return None

def load_cities():
    if not os.path.exists(CITIES_FILE):
        return []
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(entry):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []
    history.append(entry)
    # keep last 100 entries max
    history = history[-100:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def read_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

# ------------------ GUI ------------------
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("blue")

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🇸🇪 Sweden Weather — Dark")
        self.geometry("520x520")
        self.resizable(False, False)

        # top frame
        top = ctk.CTkFrame(self, corner_radius=0)
        top.pack(fill="x", padx=16, pady=(12,6))

        title = ctk.CTkLabel(top, text="🌤️ Sweden Weather", font=("Helvetica", 20, "bold"))
        title.pack(side="left", padx=6, pady=8)

        history_btn = ctk.CTkButton(top, text="History", width=90, command=self.open_history)
        history_btn.pack(side="right", padx=6, pady=8)

        # main frame
        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        # city selector
        tk_label = ctk.CTkLabel(frame, text="Select a Swedish city:", anchor="w")
        tk_label.pack(fill="x", padx=12, pady=(12,6))

        self.cities = load_cities()
        # Use ttk Combobox for large lists
        self.var_city = ctk.StringVar()
        combo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        combo_frame.pack(fill="x", padx=12)
        self.combobox = ttk.Combobox(combo_frame, values=self.cities, textvariable=self.var_city)
        self.combobox.bind("<Return>", lambda e: self.fetch_weather())
        self.combobox.pack(fill="x")

        # buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=10)
        self.btn_get = ctk.CTkButton(btn_frame, text="Get Weather", command=self.fetch_weather)
        self.btn_get.pack(side="left", padx=(0,8))
        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear", command=self.clear_display)
        self.btn_clear.pack(side="left")

        # result area
        self.result_box = ctk.CTkTextbox(frame, width=460, height=300, corner_radius=8)
        self.result_box.pack(padx=12, pady=(6,12))
        self.result_box.configure(state="disabled")

        # footer
        footer = ctk.CTkLabel(self, text="Built with ❤️ — Data from OpenWeatherMap", font=("Helvetica", 9))
        footer.pack(side="bottom", pady=6)

    def fetch_weather(self):
        city = self.var_city.get().strip()
        if not city:
            messagebox.showwarning("Input required", "Please select or type a city name.")
            return
        self.btn_get.configure(state="disabled")
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", f"🔎 Fetching weather for {city}...\n")
        self.result_box.configure(state="disabled")
        self.update()

        data = get_weather(city)
        if not data:
            messagebox.showerror("Error", "Failed to fetch weather data. Check your internet or city name.")
            self.btn_get.configure(state="normal")
            return

        # display nicely
        out = []
        out.append(f"📍 {data['city']} , Sweden\n")
        out.append(f"📝 Condition : {data['condition']}\n")
        out.append(f"🌡️ Temperature : {data['temp']} °C\n")
        out.append(f"💧 Humidity : {data['humidity']} %\n")
        out.append(f"💨 Wind Speed : {data['wind']} m/s\n")
        out.append(f"🌅 Sunrise : {data['sunrise']}   🌇 Sunset : {data['sunset']}\n")
        out.append(f"\n🕓 Retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "".join(out))
        self.result_box.configure(state="disabled")

        # save to history
        save_history({
            "city": data["city"],
            "temp": data["temp"],
            "condition": data["condition"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        self.btn_get.configure(state="normal")

    def clear_display(self):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.configure(state="disabled")

    def open_history(self):
        history = read_history()
        popup = ctk.CTkToplevel(self)
        popup.title("Search History")
        popup.geometry("480x380")
        popup.resizable(False, False)

        lbl = ctk.CTkLabel(popup, text="Last searches (most recent first):", font=("Helvetica", 14, "bold"))
        lbl.pack(pady=(12,6), padx=12, anchor="w")

        # frame with scrollbar and list
        container = ctk.CTkFrame(popup, corner_radius=8)
        container.pack(fill="both", expand=True, padx=12, pady=6)

        # use a standard Text for flexible formatting
        txt = ctk.CTkTextbox(container, width=440, height=260)
        txt.pack(padx=8, pady=8)
        txt.configure(state="normal")
        if not history:
            txt.insert("end", "No history yet.")
        else:
            # show most recent first
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
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {e}")

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()