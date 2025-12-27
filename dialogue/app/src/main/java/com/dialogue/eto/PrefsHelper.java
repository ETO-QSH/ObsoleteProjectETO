package com.dialogue.eto;

import android.content.Context;
import android.content.SharedPreferences;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import org.json.JSONObject;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;

public class PrefsHelper {
    private static final String PREFS_NAME = "chat_prefs";
    private static final String KEY_MESSAGES = "messages";
    private static final String KEY_IS_LOGGED_IN = "is_logged_in";
    private static final String KEY_USERNAME = "username";
    private static final String KEY_SAVED_USERNAME = "saved_username";
    private static final String KEY_SAVED_PASSWORD = "saved_password";

    // 添加以下常量
    private static final String KEY_COURSES = "courses";
    private static final String KEY_EXAMS = "exams";
    private static final String KEY_SCORES = "scores";

    public static void saveCourses(Context context, JSONObject data) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .putString(KEY_COURSES, data.toString())
                .apply();
    }

    public static void saveExams(Context context, JSONObject data) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .putString(KEY_EXAMS, data.toString())
                .apply();
    }

    public static void saveScores(Context context, JSONObject data) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .putString(KEY_SCORES, data.toString())
                .apply();
    }

    public static void saveMessages(Context context, List<Message> messages) {
        Gson gson = new Gson();
        String json = gson.toJson(messages);
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .putString(KEY_MESSAGES, json)
                .apply();
    }

    public static List<Message> loadMessages(Context context) {
        String json = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .getString(KEY_MESSAGES, "");
        if (json.isEmpty()) return new ArrayList<>();

        Type type = new TypeToken<List<Message>>(){}.getType();
        return new Gson().fromJson(json, type);
    }

    public static void setLoggedIn(Context context, boolean isLoggedIn, String username) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .putBoolean(KEY_IS_LOGGED_IN, isLoggedIn)
                .putString(KEY_USERNAME, username)
                .apply();
    }

    public static boolean isLoggedIn(Context context) {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .getBoolean(KEY_IS_LOGGED_IN, false);
    }

    // 新增保存凭证方法
    public static void saveCredentials(Context context, String username, String password) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .putString(KEY_SAVED_USERNAME, username)
                .putString(KEY_SAVED_PASSWORD, password)
                .apply();
    }

    // 新增获取凭证方法
    public static String[] getSavedCredentials(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        String username = prefs.getString(KEY_SAVED_USERNAME, "");
        String password = prefs.getString(KEY_SAVED_PASSWORD, "");
        if (!username.isEmpty() && !password.isEmpty()) {
            return new String[]{username, password};
        }
        return null;
    }

    // 新增清除凭证方法
    public static void clearCredentials(Context context) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                .edit()
                .remove(KEY_SAVED_USERNAME)
                .remove(KEY_SAVED_PASSWORD)
                .apply();
    }
}