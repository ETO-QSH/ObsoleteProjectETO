package com.dialogue.eto;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.util.TypedValue;
import android.widget.Button;
import android.widget.TextView;

import androidx.core.content.ContextCompat;
import androidx.core.content.res.ResourcesCompat;

public class DialogUtils {
    public static void setupCustomDialog(AlertDialog dialog, Context context) {
        // 设置标题
        TextView title = dialog.findViewById(R.id.alertTitle);
        if (title != null) {
            title.setTypeface(ResourcesCompat.getFont(context, R.font.lolita));
        }

        // 设置消息正文
        TextView message = dialog.findViewById(R.id.message);
        if (message != null) {
            message.setTypeface(ResourcesCompat.getFont(context, R.font.lolita));
        }

        // 设置按钮样式
        dialog.getWindow().getDecorView().post(() -> {
            Button positive = dialog.getButton(DialogInterface.BUTTON_POSITIVE);
            styleButton(positive, context);

            Button negative = dialog.getButton(DialogInterface.BUTTON_NEGATIVE);
            styleButton(negative, context);
        });
    }

    private static void styleButton(Button button, Context context) {
        if (button == null) return;

        button.setTypeface(ResourcesCompat.getFont(context, R.font.lolita));
        button.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        button.setLineSpacing(4f, 1f);
        button.setTextColor(ContextCompat.getColor(context, R.color.purple));
    }
}