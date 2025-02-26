import re, json
from datetime import timedelta, date

cls = [
    {"start": "08:00", "end": "08:45"},
    {"start": "08:50", "end": "09:35"},
    {"start": "09:55", "end": "10:40"},
    {"start": "10:45", "end": "11:30"},
    {"start": "11:35", "end": "12:20"},
    {"start": "14:00", "end": "14:45"},
    {"start": "14:50", "end": "15:35"},
    {"start": "15:40", "end": "16:25"},
    {"start": "16:45", "end": "17:30"},
    {"start": "17:35", "end": "18:20"},
    {"start": "19:00", "end": "19:45"},
    {"start": "19:50", "end": "20:35"},
    {"start": "20:40", "end": "21:25"}
]

def format_tap_json(day, Data, notice=30):
    res = []
    for item in Data:
        for ds in item['days']:
            it = {
                "title": item['title'],
                "start": item['classes'][0],
                "end": item['classes'][1],
                "day": str(day + timedelta(days=ds)),
                "gmt": "+8",
                "notice": notice,
                "color": "0xFFFFBFBF",
                "locate": item['locate'],
                "data": ""
            }
            res.append(it)
    return sorted(res, key=lambda x: (x['day'], x['start']))

with open("get.json", "r", encoding="utf-8") as file:
    data = json.load(file)["datas"]

Week = '一二三四五六日'
classDict = []

for item in data:
    if item["classDateAndPlace"]:
        title = item["courseName"]
        body = item["classDateAndPlace"].split(";")
        for i in body:
            it = i.split()
            day, week, locate = Week.index(it[1][-1])+1, it[0][1:-1].split(","), it[3]
            a, b = re.findall(r'\d+', it[2])
            classes = cls[int(a)-1]["start"], cls[int(b)-1]["end"]

            days = []
            for s in week:
                if '-' in s:
                    match = re.search(r"(\d+)-(\d+)周", s)
                    d = list(range(int(match.group(1)) - 1, int(match.group(2))))
                    days.extend([x * 7 + day for x in d])
                else:
                    days.append(day + int(s[:-1]) * 7)
            classDict.append({"title": title, "days": days, "classes": classes, "locate": locate})

classJson = format_tap_json(date(2025, 2, 23), classDict, notice=30)

with open('classJson.json', 'w', encoding='utf-8') as file:
    json.dump({"notice": classJson}, file, indent=4, ensure_ascii=False)
