import re
import json
import asyncio
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta


# --------------- 数据结构定义 ---------------
class CourseSchedule(BaseModel):
    title: str
    start: str
    end: str
    day: str
    locate: str


class ExamNotice(BaseModel):
    name: str
    type: str
    place: str
    date: str
    time: str


class GradeRecord(BaseModel):
    name: str
    date: str
    score: float
    proportion: float


class CourseFreshair(BaseModel):
    gpa: float
    credit: float
    name: str
    time: str
    passed: bool
    first_score: str
    year_and_semester: str
    ultimately_score: str
    score_type: str


# --------------- 数据管理类 ---------------
def fuzzy_match(source, target):
    """模糊匹配算法"""
    source = re.sub(r'\W+', '', source).lower()
    target = re.sub(r'\W+', '', target).lower()
    return target in source


async def safe_load(file_path, schema, data_key):
    """安全加载数据并验证"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data.get(data_key, [])  # 从指定键获取数据数组
            return [schema(**item) for item in items]
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 ({file_path}): {str(e)}")
        return []
    except KeyError as e:
        print(f"键缺失错误 ({file_path}): {str(e)}")
        return []
    except Exception as e:
        print(f"意外错误 ({file_path}): {str(e)}")
        return []


class AcademicDataManager:
    def __init__(self, user_info):
        self.courses: List[CourseSchedule] = []
        self.exams: List[ExamNotice] = []
        self.grades: List[GradeRecord] = []
        self.evaluates: List[CourseFreshair] = []
        self.user_info = user_info

    async def load_all_data(self):
        """异步加载所有数据"""
        base_path = f"database/{self.user_info}"
        self.courses, self.exams, self.grades, self.evaluates = await asyncio.gather(
            safe_load(f"{base_path}/courses.json", CourseSchedule, "courses"),
            safe_load(f"{base_path}/exams.json", ExamNotice, "exams"),
            safe_load(f"{base_path}/grades.json", GradeRecord, "grades"),
            safe_load(f"{base_path}/evaluates.json", CourseFreshair, "evaluates")
        )

        # 数据排序
        self.courses.sort(key=lambda x: (x.day, x.start))
        self.exams.sort(key=lambda x: x.date)
        self.grades.sort(key=lambda x: x.date)
        self.evaluates.sort(key=lambda x: x.time)

    # --------------- 查询方法 ---------------
    def search_courses(self, days=7, keyword=None):
        """查询本学期课程信息"""
        start_date = (datetime.now() + timedelta(days=days-3)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days+3)).strftime("%Y-%m-%d")
        filtered = [c for c in self.courses if start_date <= c.day <= end_date]
        if keyword:
            filtered = [c for c in filtered if fuzzy_match(c.title, keyword)]
        return filtered

    def search_exams(self, exam_type=None, keyword=None):
        """查询本学期考试信息"""
        filtered = self.exams
        if exam_type and exam_type.lower() != "all":
            filtered = [c for c in filtered if fuzzy_match(c.type, exam_type)]
        if keyword:
            filtered = [c for c in filtered if fuzzy_match(c.name, keyword)]
        return filtered

    def search_grades(self, course_name=None):
        """查询本学期考试成绩"""
        filtered = self.grades
        if course_name:
            filtered = [g for g in filtered if fuzzy_match(g.name, course_name)]
        return filtered

    def search_evaluates(self, course_name=None):
        """查询之前的期末总评成绩"""
        filtered = self.evaluates
        if course_name:
            filtered = [g for g in filtered if fuzzy_match(g.name, course_name)]
        return filtered


# --------------- 工具集成类 ---------------
def _format_response(data_type: str, results, **meta):
    """统一格式化响应"""
    if "error" in results:
        return results
    return {"status": "success", "data": {data_type: results, **meta}}


class AcademicQueryTools:
    def __init__(self):
        self.lock = asyncio.Lock()

    async def _dynamic_query(self, user_info, func_name, *args, **kwargs):
        """动态执行查询（每次新建实例）"""
        try:
            # 每次创建新实例
            manager = AcademicDataManager(user_info)
            await manager.load_all_data()

            # 执行查询方法
            method = getattr(manager, f"search_{func_name}")
            results = method(*args, **kwargs)

            return [item.dict() for item in results]

        except AttributeError as e:
            return {"status": "error", "message": "无效的查询类型 & 数据类型错误"}
        except Exception as e:
            return {"status": "error", "message": f"查询失败: {str(e)}"}
        finally:  # 确保资源释放
            if 'manager' in locals():
                del manager

# --------------- 对外查询接口 ---------------
    async def query_courses(self, user_info: str, days=7, keyword=None):
        results = await self._dynamic_query(user_info, "courses", days, keyword)
        return _format_response("courses", results, days=days, keyword=keyword)

    async def query_exams(self, user_info: str, exam_type=None, keyword=None):
        results = await self._dynamic_query(user_info, "exams", exam_type, keyword)
        return _format_response("exams", results, exam_type=exam_type, keyword=keyword)

    async def query_grades(self, user_info: str, course_name=None):
        results = await self._dynamic_query(user_info, "grades", course_name)
        return _format_response("grades", results, course=course_name)

    async def query_evaluates(self, user_info: str, course_name=None):
        results = await self._dynamic_query(user_info, "evaluates", course_name)
        return _format_response("evaluates", results, course=course_name)
