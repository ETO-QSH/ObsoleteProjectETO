package com.dialogue.eto;

public class Message {
    private String content;
    private boolean isUser;

    public Message(String content, boolean isUser) {
        this.content = content;
        this.isUser = isUser;
    }

    // Getter方法
    public String getContent() { return content; }
    public boolean isUser() { return isUser; }
}