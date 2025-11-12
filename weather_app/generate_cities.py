# generate_cities.py
# Downloads GeoNames SE.zip and extracts populated place names into sweden_cities.json
import requests, zipfile, io, json
from pathlib import Path

URL = "https://download.geonames.org/export/dump/SE.zip"
OUT_JSON = Path("sweden_cities.json")

def fetch_and_extract():
    print("Downloading SE.zip from GeoNames...")
    r = requests.get(URL, stream=True)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = set()
    with z.open("SE.txt") as fh:
        for raw in fh:
            try:
                line = raw.decode("utf-8")
            except:
                continue
            parts = line.split("\t")
            # GeoNames format: name is index 1, feature class index 6 (P=populated place)
            if len(parts) > 6:
                name = parts[1]
                fclass = parts[6]
                if fclass == "P":
                    names.add(name)
    names = sorted(names)
    print(f"Found {len(names)} populated places. Saving to {OUT_JSON} ...")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == '__main__':
    fetch_and_extract()