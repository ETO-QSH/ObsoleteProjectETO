import pandas as pd
import json
import os

def parse_database(file_path):
    print(f"Loading {file_path} ...")
    xls = pd.ExcelFile(file_path)
    print("Sheets found:", xls.sheet_names)
    
    # Analyze each sheet
    summary = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, nrows=5) # preview 5 rows
        
        preview_list = []
        for rec in df.to_dict(orient='records'):
            clean_rec = {}
            for k, v in rec.items():
                if pd.isna(v):
                    clean_rec[k] = None
                else:
                    clean_rec[k] = str(v)
            preview_list.append(clean_rec)
                    
        info = {
            "columns": list(df.columns),
            "rows_preview": preview_list
        }
        summary[sheet] = info
        
    output_path = os.path.join("d:/Desktop/Desktop/数学建模/tc_project/document/data_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)
        
    print(f"Data summary saved to {output_path}")

if __name__ == "__main__":
    file_path = "d:/Desktop/Desktop/数学建模/tc_project/data/raw/database.xlsx"
    parse_database(file_path)