import os
import time
import requests
import pandas as pd


API_KEY = "******"

OUTPUT_DIR = "./data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

START_DATE = "2025-01-01"
END_DATE = "2026-12-31"
BASE_URL = "https://api.eia.gov/v2/"

DATASETS = {
    "Brent_daily": {
        "url": "petroleum/pri/spt/data/",
        "series": "RBRTE",
        "frequency": "daily",
        "file": "Brent_daily.csv"
    },
    "WTI_daily": {
        "url": "petroleum/pri/spt/data/",
        "series": "RWTC",
        "frequency": "daily",
        "file": "WTI_daily.csv"
    },
    "HenryHub_daily": {
        "url": "natural-gas/pri/fut/data/",
        "series": "RNGWHHD",
        "frequency": "daily",
        "file": "HenryHub_daily.csv"
    },
    "CrudeExport_weekly": {
        "url": "petroleum/sum/sndw/data/",
        "series": "WCESTUS1",
        "frequency": "weekly",
        "file": "CrudeExport_weekly.csv"
    },
    "CrudeProduction_weekly": {
        "url": "petroleum/sum/sndw/data/",
        "series": "WCRFPUS2",
        "frequency": "weekly",
        "file": "CrudeProduction_weekly.csv"
    },
    "RefineryInput_weekly": {
        "url": "petroleum/sum/sndw/data/",
        "series": "WCRRIUS2",
        "frequency": "weekly",
        "file": "RefineryInput_weekly.csv"
    }
}


def download_eia(name, cfg):
    print("\n" + "=" * 65)
    print("Downloading:", name)

    url = BASE_URL + cfg["url"]
    rows = []
    offset = 0

    while True:
        params = {
            "api_key": API_KEY,
            "frequency": cfg["frequency"],
            "data[0]": "value",
            "facets[series][]": cfg["series"],
            "start": START_DATE,
            "end": END_DATE,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": 5000
        }

        try:
            r = requests.get(url, params=params, timeout=30)

            if r.status_code != 200:
                print("HTTP ERROR:", r.status_code)
                print(r.text[:500])
                return

            js = r.json()

            if "response" not in js:
                print(js)
                return

            data = js["response"]["data"]

            if len(data) == 0:
                break

            rows.extend(data)

            if len(data) < 5000:
                break

            offset += 5000
            time.sleep(1)

        except Exception as e:
            print("ERROR:", e)
            return

    if len(rows) == 0:
        print("EMPTY DATA")
        return

    df = pd.DataFrame(rows)

    if "period" in df.columns:
        df = df.sort_values("period")

    output = os.path.join(OUTPUT_DIR, cfg["file"])
    df.to_csv(output, index=False, encoding="utf-8-sig")

    print("Saved:", output)
    print("Rows:", len(df))
    print(df[["period", "value", "units"]].head())


if __name__ == "__main__":
    print("EIA ENERGY DATA DOWNLOADER")
    for name, cfg in DATASETS.items():
        download_eia(name, cfg)
        time.sleep(1)
    print("\nALL FINISHED")
