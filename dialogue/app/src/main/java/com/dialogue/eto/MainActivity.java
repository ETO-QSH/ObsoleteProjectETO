package com.dialogue.eto;

import static android.content.ContentValues.TAG;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.content.res.ResourcesCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private static final int LOGIN_TIMEOUT = 30000;
    private RecyclerView recyclerView;
    private EditText etInput;
    private List<Message> messageList = new ArrayList<>();
    private MessageAdapter adapter;
    private Handler uiHandler = new Handler(Looper.getMainLooper());
    private static final String TAG = "MainETO";
    private LoginTask loginTask;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initializeUI();
        attemptAutoLogin();
    }

    private void initializeUI() {
        recyclerView = findViewById(R.id.recyclerView);
        etInput = findViewById(R.id.etInput);

        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        recyclerView.setLayoutManager(layoutManager);
        adapter = new MessageAdapter(messageList);
        recyclerView.setAdapter(adapter);

        findViewById(R.id.btnSend).setOnClickListener(v -> sendMessage());

        loadSavedMessages();
    }

    private void attemptAutoLogin() {
        String[] credentials = PrefsHelper.getSavedCredentials(this);
        if (credentials != null) {
            performLogin(credentials[0], credentials[1]);
        }
    }

    private void performLogin(String username, String password) {
        cancelPendingLogin();

        loginTask = new LoginTask(username, password, (success, message, data) -> {
            handleLoginResult(success, message, username, password);
            if (success) {
                processQueryData(data);
            }
        });

        loginTask.execute();
        startLoginTimeout();
    }

    private void handleLoginResult(boolean success, String message, String username, String password) {
        uiHandler.post(() -> {
            if (success) {
                PrefsHelper.setLoggedIn(this, true, username);
                PrefsHelper.saveCredentials(this, username, password);
                Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
            } else {
                PrefsHelper.clearCredentials(this);
                Toast.makeText(this, message, Toast.LENGTH_LONG).show();
                showLoginDialog();
            }
        });
    }

    private void processQueryData(JSONObject data) {
        // 处理查询到的数据
        try {
            // 保存课程数据
            JSONObject coursesData = data.getJSONObject("courses");
            String coursesJson = coursesData.toString();
            JSONObject convertedCourses = GetConverter.handleResult(coursesJson);
            if (convertedCourses != null) {
                Log.i(TAG, "coursesData: " + convertedCourses);
                PrefsHelper.saveCourses(this, convertedCourses);
            } else {
                Log.e(TAG, "课程数据转换失败");
            }
            // 保存考试数据
            JSONObject examsData = data.getJSONObject("exams");
            JSONObject convertedExams = ExamConverter.convertExamData(examsData);
            Log.i(TAG, "examsData: " + convertedExams);
            PrefsHelper.saveExams(this, convertedExams);
            // 保存成绩数据
            JSONObject scoresData = data.getJSONObject("scores");
            Log.i(TAG, "scoresData: " + scoresData);
            PrefsHelper.saveScores(this, scoresData);
        } catch (Exception e) {
            Log.e(TAG, "数据处理失败: " + e.getMessage());
        }
    }

    private void startLoginTimeout() {
        uiHandler.postDelayed(this::handleLoginTimeout, LOGIN_TIMEOUT);
    }

    private void handleLoginTimeout() {
        if (loginTask != null && loginTask.getStatus() == AsyncTask.Status.RUNNING) {
            loginTask.cancel(true);
            Toast.makeText(this, "登录超时", Toast.LENGTH_SHORT).show();
        }
    }

    private void cancelPendingLogin() {
        if (loginTask != null && !loginTask.isCancelled()) {
            loginTask.cancel(true);
        }
    }

    private void sendMessage() {
        // 登录验证
        if (!PrefsHelper.isLoggedIn(this)) {
            Toast.makeText(this, "请先登录", Toast.LENGTH_SHORT).show();
            showLoginDialog();
            return;
        }

        String input = etInput.getText().toString().trim();
        if (!input.isEmpty()) {
            // 添加用户消息
            addUserMessage(input);

            // 模拟AI回复
            new Handler().postDelayed(() -> {
                addBotMessage("这是AI的回复");
                // 滚动到底部
                recyclerView.smoothScrollToPosition(messageList.size() - 1);
            }, 1000);

            etInput.setText("");
        }
    }

    private void addUserMessage(String text) {
        messageList.add(new Message(text, true));
        adapter.notifyItemInserted(messageList.size() - 1);
        saveMessages();
    }

    private void addBotMessage(String text) {
        messageList.add(new Message(text, false));
        adapter.notifyItemInserted(messageList.size() - 1);
        saveMessages();
    }

    // region 菜单功能
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_clear) {
            showClearConfirmationDialog();
            return true;
        } else if (id == R.id.action_account) {
            handleAccountAction();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
    // endregion

    // region 对话框相关
    private void showClearConfirmationDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        // 设置标题
        View titleView = LayoutInflater.from(this).inflate(R.layout.dialog_title_top, null);
        ((TextView)titleView.findViewById(R.id.alertTitle)).setText("清除记录");
        builder.setCustomTitle(titleView);

        // 设置自定义消息
        View messageView = LayoutInflater.from(this).inflate(R.layout.dialog_message_top, null);
        ((TextView)messageView.findViewById(R.id.message)).setText("确定要清除所有对话记录吗？");
        builder.setView(messageView);

        builder.setPositiveButton("确定", (dialog, which) -> {
            // 清除记录
            messageList.clear();
            adapter.notifyDataSetChanged();
            PrefsHelper.saveMessages(this, messageList); // 持久化空列表
            Toast.makeText(this, "对话已清空", Toast.LENGTH_SHORT).show();

            // 可选：滚动到顶部
            recyclerView.scrollToPosition(0);
        });

        builder.setNegativeButton("取消", null);

        AlertDialog dialog = builder.create();
        dialog.show();
        DialogUtils.setupCustomDialog(dialog, this);
    }

    private void handleAccountAction() {
        if (PrefsHelper.isLoggedIn(this)) {
            showLogoutDialog();
        } else {
            showLoginDialog();
        }
    }

    private void showLoginDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        // 自定义对话框布局
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_login, null);
        builder.setView(dialogView);

        // 自定义标题
        View titleView = LayoutInflater.from(this).inflate(R.layout.dialog_title, null);
        TextView titleText = titleView.findViewById(R.id.alertTitle);
        titleText.setText("统一身份验证");
        titleText.setTypeface(ResourcesCompat.getFont(this, R.font.lolita));
        builder.setCustomTitle(titleView);

        // 获取输入组件
        EditText etUsername = dialogView.findViewById(R.id.et_username);
        EditText etPassword = dialogView.findViewById(R.id.et_password);

        // 设置按钮
        builder.setPositiveButton("登录", (dialog, which) -> {
            String username = etUsername.getText().toString().trim();
            String password = etPassword.getText().toString().trim();

            if (username.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "账号密码不能为空", Toast.LENGTH_SHORT).show();
                return;
            }

            // 执行登录逻辑
            performLogin(username, password); // 调用 performLogin 方法
            // PrefsHelper.setLoggedIn(this, true, username);
            Toast.makeText(this, "登录中...", Toast.LENGTH_LONG).show();
        });

        builder.setNegativeButton("取消", (dialog, which) -> dialog.dismiss());

        AlertDialog dialog = builder.create();
        dialog.show();

        // 修改按钮样式
        dialog.getWindow().getDecorView().post(() -> {
            Button positiveButton = dialog.getButton(DialogInterface.BUTTON_POSITIVE);
            if (positiveButton != null) {
                positiveButton.setTypeface(ResourcesCompat.getFont(this, R.font.lolita));
                positiveButton.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
            }

            Button negativeButton = dialog.getButton(DialogInterface.BUTTON_NEGATIVE);
            if (negativeButton != null) {
                negativeButton.setTypeface(ResourcesCompat.getFont(this, R.font.lolita));
                negativeButton.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
            }
        });

        // 自动弹出键盘
        etUsername.postDelayed(() -> {
            InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.showSoftInput(etUsername, InputMethodManager.SHOW_IMPLICIT);
        }, 100);
    }

    private void showLogoutDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);

        // 设置标题
        View titleView = LayoutInflater.from(this).inflate(R.layout.dialog_title_top, null);
        ((TextView)titleView.findViewById(R.id.alertTitle)).setText("退出登录");
        builder.setCustomTitle(titleView);

        // 设置消息
        View messageView = LayoutInflater.from(this).inflate(R.layout.dialog_message_top, null);
        ((TextView)messageView.findViewById(R.id.message)).setText("确定要退出当前账号吗？");
        builder.setView(messageView);

        builder.setPositiveButton("退出", (dialog, which) -> {
            // 退出登录
            PrefsHelper.setLoggedIn(this, false, ""); // 清除登录状态
            Toast.makeText(this, "已退出登录", Toast.LENGTH_SHORT).show();

            // 可选：清除当前会话消息
            messageList.clear();
            adapter.notifyDataSetChanged();
        });

        builder.setNegativeButton("取消", null);

        AlertDialog dialog = builder.create();
        dialog.show();
        DialogUtils.setupCustomDialog(dialog, this);
    }
    // endregion

    // region 数据持久化
    private void saveMessages() {
        PrefsHelper.saveMessages(this, messageList);
    }

    private void loadSavedMessages() {
        messageList.clear();
        messageList.addAll(PrefsHelper.loadMessages(this));
        adapter.notifyDataSetChanged();
        if (!messageList.isEmpty()) {
            recyclerView.scrollToPosition(messageList.size() - 1);
        }
    }
}