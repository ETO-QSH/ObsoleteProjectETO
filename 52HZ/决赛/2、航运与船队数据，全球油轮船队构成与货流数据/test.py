# import win32com.client as win32
#
# xl = win32.Dispatch('Excel.Application')
# xl.Visible = False
# wb = xl.Workbooks.Open(r'D:\Desktop\Desktop\52HZ\2、航运与船队数据，全球油轮船队构成与货流数据\2022-2024原油全球货流分析.xlsx')
# pt = wb.Sheets('装卸港流向').PivotTables(1)
#
# # 清空后看家底
# pt.ClearTable()
# print('当前透视表可用字段：')
# for f in pt.PivotFields():
#     print(f.Name)          # 把真实名字全打出来


# import json
# import csv
#
# with open("crude_oil_flow.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# exports = {}
# imports = {}
#
# for month, producers in data.items():
#     year = month.split("-")[0]
#     if year not in ("2022", "2023", "2024"):
#         continue
#     for producer, consumers in producers.items():
#         vol_sum = sum(consumers.values())
#         exports[producer] = exports.get(producer, 0) + vol_sum
#         for consumer, vol in consumers.items():
#             imports[consumer] = imports.get(consumer, 0) + vol
#
# total_export = sum(exports.values())
# total_import = sum(imports.values())
#
# all_countries = set(exports.keys()) | set(imports.keys())
#
# analysis = []
# for country in all_countries:
#     exp = exports.get(country, 0)
#     imp = imports.get(country, 0)
#     net = exp - imp
#     exp_pct = exp / total_export * 100 if total_export > 0 else 0
#     imp_pct = imp / total_import * 100 if total_import > 0 else 0
#     role = "出口国" if net > 0 else "进口国" if net < 0 else "平衡"
#     analysis.append((country, exp, exp_pct, imp, imp_pct, net, role))
#
# analysis.sort(key=lambda x: x[5], reverse=True)
# with open("country_flow_analysis_with_pct.csv", "w", encoding="utf-8", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow(["国家", "出口量", "出口占比(%)", "进口量", "进口占比(%)", "净流量", "角色"])
#     for row in analysis:
#         writer.writerow([row[0], row[1], round(row[2], 4), row[3], round(row[4], 4), row[5], row[6]])



