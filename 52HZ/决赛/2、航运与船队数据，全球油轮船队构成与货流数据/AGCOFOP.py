from collections import defaultdict
import win32com.client
import json, os


FILE_PATH = r"D:\Desktop\Desktop\52HZ\2、航运与船队数据，全球油轮船队构成与货流数据\2022-2024原油全球货流分析.xlsx"
OUTPUT_JSON = "crude_oil_flow.json"


def com_safe_dict(pt):
    res = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    row_fld_map = {rf.Name: idx + 1 for idx, rf in enumerate(pt.RowFields)}

    load_idx = row_fld_map["装货国家"]
    disc_idx = row_fld_map["卸货国家"]

    month_fld = pt.PivotFields("月份")
    for mi in month_fld.PivotItems():
        month_fld.CurrentPage = mi.Name
        data_area = pt.DataBodyRange
        if data_area is None:
            continue

        for cell in data_area.Cells:
            val = cell.Value
            pcl = cell.PivotCell

            if val is None:
                continue
            if pcl.RowItems.Count < max(load_idx, disc_idx):
                continue

            loading_country = pcl.RowItems(load_idx).Name
            discharging_country = pcl.RowItems(disc_idx).Name
            res[mi.Name][loading_country][discharging_country] += float(val)

    return {k: {kk: {kkk: vvv for kkk, vvv in vv.items()} for kk, vv in v.items()} for k, v in res.items()}


excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = False

wb = excel.Workbooks.Open(os.path.abspath(FILE_PATH))
pt = wb.Sheets("装卸港流向").PivotTables(1)
nested = com_safe_dict(pt)

wb.Close(SaveChanges=False)
excel.Quit()

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(nested, f, ensure_ascii=False, indent=2)