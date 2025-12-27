package com.dialogue.eto;

import org.json.JSONArray;
import org.json.JSONObject;

public class ExamConverter {
    public static JSONObject convertExamData(JSONObject rawData) throws Exception {
        if (!rawData.has("datas")) {
            throw new Exception("Invalid input format");
        }

        JSONArray datas = rawData.getJSONArray("datas");
        JSONArray noticeArray = new JSONArray();

        for (int i = 0; i < datas.length(); i++) {
            JSONObject item = datas.getJSONObject(i);
            JSONObject noticeItem = new JSONObject();

            noticeItem.put("name", item.optString("courseName", ""));
            noticeItem.put("type", item.optString("examType", ""));
            noticeItem.put("place", item.optString("examPlace", ""));
            String examDate = item.optString("examDate", "");
            String examTimeDescription = item.optString("examTimeDescription", "");

            // 处理日期和时间
            String date = examDate.split(" ")[0];
            String time = examTimeDescription.split(" ")[1];

            noticeItem.put("date", date);
            noticeItem.put("time", time);

            noticeArray.put(noticeItem);
        }

        JSONObject result = new JSONObject();
        result.put("notice", noticeArray);

        return result;
    }
}