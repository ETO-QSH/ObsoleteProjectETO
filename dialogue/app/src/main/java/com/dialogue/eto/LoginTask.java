package com.dialogue.eto;

import android.os.AsyncTask;
import android.util.Base64;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.spec.X509EncodedKeySpec;
import java.util.ArrayList;
import java.util.List;

import javax.crypto.Cipher;

import okhttp3.Cookie;
import okhttp3.CookieJar;
import okhttp3.FormBody;
import okhttp3.Headers;
import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class LoginTask extends AsyncTask<Void, Void, String> {
    private static final String LOGIN_URL = "https://zhlgd.whut.edu.cn/tpass/login?service=https%3A%2F%2Fjwxt.whut.edu.cn%2Fjwapp%2Fsys%2Fhomeapp%2Findex.do%3FforceCas%3D1";
    private static final String RSA_URL = "https://zhlgd.whut.edu.cn/tpass/rsa?skipWechat=true";
    private static final String XNX_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/currentUser.do";
    private static final String KB_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/student/courses.do";
    private static final String KS_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/student/exams.do";
    private static final String CJ_URL = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/api/home/student/scores.do";
    private static final String TAG = "LoginTask";
    private final LoginCallback callback;
    private final OkHttpClient client;
    private final String username;
    private final String password;

    public interface LoginCallback {
        void onLoginComplete(boolean success, String message, JSONObject data);
    }

    public LoginTask(String username, String password, LoginCallback callback) {
        this.username = username;
        this.password = password;
        this.callback = callback;
        this.client = new OkHttpClient.Builder()
            .cookieJar(new CookieJar() {
                private final List<Cookie> allCookies = new ArrayList<>(); // 存储所有 Cookie

                @Override
                public void saveFromResponse(HttpUrl url, List<Cookie> cookies) {
                    allCookies.addAll(cookies); // 存储所有 Cookie，不区分域名
                }

                @Override
                public List<Cookie> loadForRequest(HttpUrl url) {
                    // 返回所有 Cookie，无论域名是否匹配
                    return new ArrayList<>(allCookies);
                }
            }).build();
    }

    @Override
    protected String doInBackground(Void... voids) {
        try {
            // Step 1: 获取登录页面并提取参数
            Request loginPageRequest = new Request.Builder()
                    .url(LOGIN_URL)
                    .build();
            Response loginPageResponse = client.newCall(loginPageRequest).execute();
            String html = loginPageResponse.body().string();
            Document doc = Jsoup.parse(html);
            Element ltElement = doc.selectFirst("input#lt");
            Element executionElement = doc.selectFirst("input[name=execution]");
            Element eventIdElement = doc.selectFirst("input[name=_eventId]");

            String lt = ltElement.attr("value");
            String execution = executionElement.attr("value");
            String eventId = eventIdElement.attr("value");

            // Step 2: RSA加密
            Request rsaRequest = new Request.Builder()
                    .url(RSA_URL)
                    .post(RequestBody.create("", null))
                    .build();
            Response rsaResponse = client.newCall(rsaRequest).execute();
            String rsaJson = rsaResponse.body().string();
            JSONObject rsaJsonObj = new JSONObject(rsaJson);
            String publicKeyStr = rsaJsonObj.getString("publicKey");

            if (isCancelled()) return "任务被取消";

            // Step 3: 处理公钥并加密
            byte[] publicKeyBytes = Base64.decode(publicKeyStr, Base64.DEFAULT);
            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(publicKeyBytes);
            PublicKey publicKey = KeyFactory.getInstance("RSA").generatePublic(keySpec);

            Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
            cipher.init(Cipher.ENCRYPT_MODE, publicKey);

            byte[] encryptedUsername = cipher.doFinal(username.getBytes(StandardCharsets.UTF_8));
            byte[] encryptedPassword = cipher.doFinal(password.getBytes(StandardCharsets.UTF_8));

            String ul = Base64.encodeToString(encryptedUsername, Base64.NO_WRAP);
            String pl = Base64.encodeToString(encryptedPassword, Base64.NO_WRAP);

            // Step 3: 提交登录
            FormBody formBody = new FormBody.Builder()
                    .add("rsa", "")
                    .add("ul", ul)
                    .add("pl", pl)
                    .add("lt", lt)
                    .add("execution", execution)
                    .add("_eventId", eventId)
                    .build();

            Headers headers = new Headers.Builder()
                    .add("Referer", LOGIN_URL)
                    .add("cache-control", "max-age=0")
                    .add("sec-ch-ua", "\"Not(A:Brand\";v=\"99\", \"Microsoft Edge\";v=\"133\", \"Chromium\";v=\"133\"")
                    .add("sec-ch-ua-mobile", "?0")
                    .add("sec-ch-ua-platform", "\"Windows\"")
                    .add("origin", "https://zhlgd.whut.edu.cn")
                    .add("content-type", "application/x-www-form-urlencoded")
                    .add("upgrade-insecure-requests", "1")
                    .add("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
                    .add("sec-fetch-site", "same-origin")
                    .add("sec-fetch-mode", "navigate")
                    .add("sec-fetch-user", "?1")
                    .add("sec-fetch-dest", "document")
                    .add("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6")
                    .add("priority", "u=0, i")
                    .add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0")
                    .build();

            Request loginRequest = new Request.Builder()
                    .url(LOGIN_URL)
                    .post(formBody)
                    .headers(headers)
                    .build();

            Response loginResponse = client.newCall(loginRequest).execute();
            String loginResponseHtml = new String(loginResponse.body().bytes(), StandardCharsets.UTF_8);

            Log.i(TAG, "loginResponse: " + loginResponseHtml);

            // Step 4: 获取学期代码
            Document docx = Jsoup.parse(loginResponseHtml);
            Elements scripts = docx.select("script");

            boolean href = false;
            String hrefValue = null;
            for (Element script : scripts) {
                String scriptContent = script.data(); // 获取 script 标签的内容
                if (scriptContent.contains("location.href")) {
                    // 使用正则表达式提取 location.href 的值
                    hrefValue = scriptContent.replaceAll(".*location\\.href\\s*=\\s*'([^']*)'.*", "$1");
                    href = true;
                }
            }

            if (hrefValue == null) {
                if (href) {
                    return "账号密码错误";
                }
                return "学校网站崩了";
            } else if (hrefValue.contains("+")) {
                return "尝试登录失败";
            }

            Headers commonHeaders = new Headers.Builder()
                    .add("referer", "https://jwxt.whut.edu.cn" + hrefValue.trim())
                    .add("sec-ch-ua", "\"Not(A:Brand\";v=\"99\", \"Microsoft Edge\";v=\"133\", \"Chromium\";v=\"133\"")
                    .add("sec-ch-ua-mobile", "?0")
                    .add("sec-ch-ua-platform", "\"Windows\"")
                    .add("upgrade-insecure-requests", "1")
                    .add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0")
                    .add("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
                    .add("sec-fetch-site", "none")
                    .add("sec-fetch-mode", "navigate")
                    .add("sec-fetch-user", "?1")
                    .add("sec-fetch-dest", "document")
                    .add("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6")
                    .add("priority", "u=0, i")
                    .build();

            HttpUrl xnxqHttpUrl = HttpUrl.parse(XNX_URL).newBuilder()
                    .build();

            Request xnxqRequest = new Request.Builder()
                    .url(xnxqHttpUrl)
                    .headers(commonHeaders)
                    .build();

            Response xnxqResponse = client.newCall(xnxqRequest).execute();
            String responseJson = xnxqResponse.body().string();

            Log.i(TAG, "responseJson: " + responseJson);

            // 获取 xnxqdm 的值
            JSONObject jsonResponse = new JSONObject(responseJson);
            JSONObject datas = jsonResponse.getJSONObject("datas");
            String xnxqdm = datas.getJSONObject("welcomeInfo").getString("xnxqdm");

            // Step 5: 同步查询所有数据
            JSONObject result = new JSONObject();
            result.put("courses", queryData(KB_URL, xnxqdm, commonHeaders));
            result.put("exams", queryData(KS_URL, xnxqdm, commonHeaders));
            result.put("scores", queryData(CJ_URL, xnxqdm, commonHeaders));

            String String_result = result.toString();
            Log.d(TAG, "JSON Object: " + String_result);
            return String_result;

        } catch (Exception e) {
            Log.e(TAG, "Login error: " + e.getMessage());
            return "发生未知错误";
        }
    }

    private JSONObject queryData(String url, String xnxqdm, Headers commonHeaders) throws Exception {
        HttpUrl httpUrl = HttpUrl.parse(url).newBuilder()
                .addQueryParameter("termCode", xnxqdm)
                .build();

        Request request = new Request.Builder()
                .url(httpUrl)
                .headers(commonHeaders)
                .build();

        Response response = client.newCall(request).execute();
        return new JSONObject(response.body().string());
    }

    @Override
    protected void onPostExecute(String result) {
        try {
            // 尝试将结果解析为 JSONObject
            JSONObject data = new JSONObject(result);
            // 如果解析成功，说明登录成功
            callback.onLoginComplete(true, "登录成功", data);
        } catch (JSONException e) {
            // 如果解析失败，说明登录失败，直接使用 result 作为错误消息
            callback.onLoginComplete(false, result, null);
        }
    }
}