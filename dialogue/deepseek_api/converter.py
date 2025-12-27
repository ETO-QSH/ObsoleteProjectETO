import os
import re
import json
from datetime import datetime, timedelta

class TimetableConverter:
    def __init__(self):
        self.cls = [
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
        self.week = "一二三四五六日"
        self.base_date = datetime.strptime("2025-02-23", "%Y-%m-%d").date()

    def convert_timetable(self, json_data):
        try:
            jsonArray = json_data.get("datas", [])
            classDict = []
            for item in jsonArray:
                if not item.get("classDateAndPlace"):
                    continue

                title = item.get("courseName", "")
                bodies = item.get("classDateAndPlace", "").split(";")
                for body in bodies:
                    self.process_time_block(body.strip(), title, classDict)
            return self.format_tap_json(classDict)
        except Exception as e:
            print(f"Error: {e}")
            return None

    def process_time_block(self, body, title, classDict):
        parts = body.split()
        if len(parts) < 4:
            return

        dayStr = parts[1][-1]
        day = self.week.index(dayStr) + 1

        weeks = parts[0][1:-1].split(",")
        class_matcher = re.search(r"第(\d+)-(\d+)节", parts[2])
        if not class_matcher:
            return
        a = int(class_matcher.group(1))
        b = int(class_matcher.group(2))
        classes = [
            self.cls[a - 1]["start"],
            self.cls[b - 1]["end"]
        ]

        locate = parts[3] if len(parts) > 3 else ""

        entry = {
            "title": title,
            "days": self.process_weeks(weeks, day),
            "classes": classes,
            "locate": locate
        }

        classDict.append(entry)

    def process_weeks(self, weeks, day):
        daysList = []
        for week in weeks:
            matcher = re.match(r"(\d+)-(\d+)周", week)
            if matcher:
                start = int(matcher.group(1)) - 1
                end = int(matcher.group(2))
                for x in range(start, end):
                    daysList.append(x * 7 + day)
            else:
                weekNum = int(re.sub("\\D", "", week))
                daysList.append((weekNum - 1) * 7 + day)
        return daysList

    def format_tap_json(self, data):
        root = {}
        entries = []
        tempList = []

        for item in data:
            title = item.get("title", "")
            classes = item.get("classes", [])
            locate = item.get("locate", "")
            days = item.get("days", [])

            for ds in days:
                entry = {
                    "title": title,
                    "start": classes[0],
                    "end": classes[1],
                    "day": (self.base_date + timedelta(days=ds)).strftime("%Y-%m-%d"),
                    "locate": locate
                }
                tempList.append(entry)

        tempList.sort(key=lambda x: (x["day"], x["start"]))
        for entry in tempList:
            entries.append(entry)

        root["courses"] = entries
        return json.dumps(root, ensure_ascii=False, indent=2)


def courses_courses_data(username, json_data):
    converter = TimetableConverter()
    result = converter.convert_timetable(json_data)
    os.makedirs(f"database/{username}", exist_ok=True)
    with open(f"database/{username}/courses.json", "w", encoding="utf-8") as f:
        f.write(result)

def convert_exams_data(username, json_data):
    notice_array = []
    for item in json_data['datas']:
        notice_item = {
            "name": item.get('courseName', ''),
            "type": item.get('examType', ''),
            "place": item.get('examPlace', ''),
            "date": item.get('examDate', '').split(' ')[0] if item.get('examDate') else '',
            "time": item.get('examTimeDescription', '').split(' ')[1] if item.get('examTimeDescription') else ''
        }
        notice_array.append(notice_item)
    result = json.dumps({"exams": notice_array}, ensure_ascii=False, indent=2)
    os.makedirs(f"database/{username}", exist_ok=True)
    with open(f"database/{username}/exams.json", "w", encoding="utf-8") as f:
        f.write(result)

def convert_grades_data(username, json_data):
    notice_array = []
    for item in json_data['datas']:
        notice_item = {
            "name": item.get('name', ''),
            "date": item.get('date', ''),
            "score": item.get('score', ''),
            "proportion" : item.get('proportion', '')
        }
        notice_array.append(notice_item)
    result = json.dumps({"grades": notice_array}, ensure_ascii=False, indent=2)
    os.makedirs(f"database/{username}", exist_ok=True)
    with open(f"database/{username}/grades.json", "w", encoding="utf-8") as f:
        f.write(result)

def convert_evaluates_data(username, json_data):
    grades = []
    for row in json_data['datas']["xscjcx"]["rows"]:
        grade = {
            "gpa": row.get("XFJD", ""),
            "credit": row.get("XF", ""),
            "name": row.get("XSKCM", ""),
            "time": row.get("SJKSRQ", ""),
            "passed": bool(int(row.get("SFJG", 0))),
            "first_score": row.get("SCTGCJMC", ""),
            "year_and_semester": row.get("XNXQDM", ""),
            "ultimately_score": row.get("XSZCJMC", ""),
            "score_type": row.get("XSDJCJLXDM_DISPLAY", ""),
        }
        grades.append(grade)
    result = json.dumps({"evaluates": grades}, ensure_ascii=False, indent=2)
    os.makedirs(f"database/{username}", exist_ok=True)
    with open(f"database/{username}/evaluates.json", "w", encoding="utf-8") as f:
        f.write(result)
