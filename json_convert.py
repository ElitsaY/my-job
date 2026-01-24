import pandas as pd

def csv_to_json(csv_path: str, json_path: str):
    df = pd.read_csv(csv_path)
    df.to_json(json_path, orient="records", indent=2)

if __name__ == "__main__":
    csv_to_json("google_internships.csv", "google_internships.json")
