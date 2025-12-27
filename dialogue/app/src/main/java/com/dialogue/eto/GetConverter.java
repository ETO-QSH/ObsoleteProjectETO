package com.dialogue.eto;

import android.os.Build;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class GetConverter {
    private static final List<Map<String, String>> CLS = Arrays.asList(
            createTime("08:00", "08:45"),
            createTime("08:50", "09:35"),
            createTime("09:55", "10:40"),
            createTime("10:45", "11:30"),
            createTime("11:35", "12:20"),
            createTime("14:00", "14:45"),
            createTime("14:50", "15:35"),
            createTime("15:40", "16:25"),
            createTime("16:45", "17:30"),
            createTime("17:35", "18:20"),
            createTime("19:00", "19:45"),
            createTime("19:50", "20:35"),
            createTime("20:40", "21:25")
    );

    private static final String WEEK = "一二三四五六日";
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE;
    private static final Pattern RANGE_PATTERN = Pattern.compile("(\\d+)-(\\d+)周");
    private static final Pattern CLASS_PATTERN = Pattern.compile("第(\\d+)-(\\d+)节");

    private static Map<String, String> createTime(String start, String end) {
        Map<String, String> map = new HashMap<>();
        map.put("start", start);
        map.put("end", end);
        return map;
    }

    public static JSONObject convertTimetable(String jsonData) throws JSONException {
         JsonArray jsonArray = JsonParser.parseString(jsonData)
                 .getAsJsonObject()
                 .getAsJsonArray("datas");

         List<Map<String, Object>> classDict = new ArrayList<>();
         for (JsonElement item : jsonArray) {
             JsonObject entry = item.getAsJsonObject();
             if (!entry.has("classDateAndPlace") || entry.get("classDateAndPlace").isJsonNull())  continue;

             String title = entry.get("courseName").getAsString();
             String[] bodies = entry.get("classDateAndPlace").getAsString().split(";");
             for (String body : bodies) {
                 processTimeBlock(body.trim(), title, classDict);
             }
         }
         return formatTapJson(classDict);
    }

    private static void processTimeBlock(String body, String title, List<Map<String, Object>> classDict) {

        String[] parts = body.split("\\s+");
        if (parts.length < 4) return;

        // 解析星期
        String dayStr = parts[1].substring(parts[1].length() - 1);
        int day = WEEK.indexOf(dayStr) + 1;

        // 解析周次
        String[] weeks = parts[0].substring(1, parts[0].length() - 1).split(",");

        // 解析节次
        Matcher classMatcher = CLASS_PATTERN.matcher(parts[2]);
        if (!classMatcher.find()) return;
        int a = Integer.parseInt(classMatcher.group(1));
        int b = Integer.parseInt(classMatcher.group(2));
        String[] classes = {
                CLS.get(a - 1).get("start"),
                CLS.get(b - 1).get("end")
        };

        // 解析地点
        String locate = parts[3];

        Map<String, Object> entry = new HashMap<>();
        entry.put("title", title);
        entry.put("days", processWeeks(weeks, day));
        entry.put("classes", classes);
        entry.put("locate", locate);

        classDict.add(entry);
    }

    private static List<Integer> processWeeks(String[] weeks, int day) {
        List<Integer> daysList = new ArrayList<>();
        for (String week : weeks) {
            Matcher matcher = RANGE_PATTERN.matcher(week);
            if (matcher.find()) {
                int start = Integer.parseInt(matcher.group(1)) - 1;
                int end = Integer.parseInt(matcher.group(2));
                for (int x = start; x < end; x++) {
                    daysList.add(x * 7 + day);
                }
            } else {
                int weekNum = Integer.parseInt(week.replaceAll("\\D", ""));
                daysList.add((weekNum - 1) * 7 + day);
            }
        }
        return daysList;
    }

    private static JSONObject formatTapJson(List<Map<String, Object>> data) throws JSONException {
        JSONObject root = new JSONObject();
        JSONArray entries = new JSONArray();
        LocalDate baseDate = null;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            baseDate = LocalDate.of(2025, 2, 23);
        }

        List<JSONObject> tempList = new ArrayList<>();
        for (Map<String, Object> item : data) {
            String title = (String) item.get("title");
            String[] classes = (String[]) item.get("classes");
            String locate = (String) item.get("locate");
            List<Integer> days = (List<Integer>) item.get("days");

            for (int ds : days) {
                JSONObject entry = new JSONObject();
                entry.put("title", title);
                entry.put("start", classes[0]);
                entry.put("end", classes[1]);
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    entry.put("day", baseDate.plusDays(ds).format(DATE_FORMATTER));
                }
                entry.put("locate", locate);
                tempList.add(entry);
            }
        }

        // 排序逻辑
        tempList.sort((o1, o2) -> {
            try {
                int dateCompare = o1.getString("day").compareTo(o2.getString("day"));
                return dateCompare != 0 ? dateCompare : o1.getString("start").compareTo(o2.getString("start"));
            } catch (JSONException e) {
                return 0;
            }
        });

        for (JSONObject entry : tempList) {
            entries.put(entry);
        }
        root.put("courses", entries);
        return root;
    }

    public static JSONObject handleResult(String jsonData) {
        try {
            return convertTimetable(jsonData);
        } catch (Exception e) {
            return null;
        }
    }
}