#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

#include <glbinding/gl/gl.h>
#include <glbinding/glbinding.h>
using namespace gl;

#include <spine/spine.h>
#include <spine-glfw.h>
using namespace spine;

#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <queue>
#include <map>

#define GLFW_EXPOSE_NATIVE_WIN32
#include "GLFW/glfw3native.h"
#include <winuser.h>

#include <glm/glm.hpp>
using namespace glm;
#include <algorithm>
using namespace std;

// ======================
// ANSI 转义序列颜色宏
// ======================

// 重置所有样式
#define CONSOLE_RESET          "\033[0m"

// 亮色前景色（90-97）                                // // 标准前景色（30-37）
#define CONSOLE_BRIGHT_BLACK   "\033[90m"          // #define CONSOLE_BLACK        "\033[30m"
#define CONSOLE_BRIGHT_RED     "\033[91m"          // #define CONSOLE_RED          "\033[31m"
#define CONSOLE_BRIGHT_GREEN   "\033[92m"          // #define CONSOLE_GREEN        "\033[32m"
#define CONSOLE_BRIGHT_YELLOW  "\033[93m"          // #define CONSOLE_YELLOW       "\033[33m"
#define CONSOLE_BRIGHT_BLUE    "\033[94m"          // #define CONSOLE_BLUE         "\033[34m"
#define CONSOLE_BRIGHT_MAGENTA "\033[95m"          // #define CONSOLE_MAGENTA      "\033[35m"
#define CONSOLE_BRIGHT_CYAN    "\033[96m"          // #define CONSOLE_CYAN         "\033[36m"
#define CONSOLE_BRIGHT_WHITE   "\033[97m"          // #define CONSOLE_WHITE        "\033[37m"

// 文字样式
#define CONSOLE_BOLD           "\033[1m"    // 粗体
#define CONSOLE_DIM            "\033[2m"    // 暗淡
#define CONSOLE_ITALIC         "\033[3m"    // 斜体
#define CONSOLE_UNDERLINE      "\033[4m"    // 下划线
#define CONSOLE_BLINK          "\033[5m"    // 闪烁
#define CONSOLE_REVERSE        "\033[7m"    // 反色
#define CONSOLE_HIDDEN         "\033[8m"    // 隐藏

// 高贵预定义
#define CONSOLE_256_FG(n)      "\033[38;5;" #n "m"                 // 256色模式（前景）
#define CONSOLE_RGB_FG(r,g,b)  "\033[38;2;" #r ";" #g ";" #b "m"   // RGB真彩色模式（前景）


GLFWwindow* init_glfw(int width, int height) {
    if (!glfwInit()) return nullptr;

    // 添加透明帧缓冲支持
    glfwWindowHint(GLFW_TRANSPARENT_FRAMEBUFFER, GLFW_TRUE);
    glfwWindowHint(GLFW_DECORATED, GLFW_FALSE);      // 无标题栏
    glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);      // 禁止调整大小
    glfwWindowHint(GLFW_FLOATING, GLFW_TRUE);        // 始终置顶

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(width, height, "Spine Example", nullptr, nullptr);
    if (!window) {
        glfwTerminate();
        return nullptr;
    }

    glfwMakeContextCurrent(window);
    glbinding::initialize(glfwGetProcAddress);
    return window;
}

class SpineAnimation {
public:
    struct AnimationInfo {
        bool valid = false;
        vector<pair<string, float>> animationsWithDuration; // 存储动画名称和时长
        SkeletonData* skeletonData = nullptr;
        Atlas* atlas = nullptr;
    };

    // 获取动画队列的拷贝
    vector<pair<string, float>> getAnimationQueue() const {
        vector<pair<string, float>> copy;
        queue<pair<string, float>> temp = animationQueue;
        while (!temp.empty()) {
            copy.push_back(temp.front());
            temp.pop();
        }
        return copy;
    }

    SpineAnimation(int width, int height)
        : windowWidth(width), windowHeight(height), defaultMixTime(0.2f) {
        currentInstance = this; // 设置当前实例指针

        // 初始化光标
        handCursor = glfwCreateStandardCursor(GLFW_HAND_CURSOR);
        arrowCursor = glfwCreateStandardCursor(GLFW_ARROW_CURSOR);
        currentInstance = this;
    }

    // 1. 加载动画文件
    static AnimationInfo loadFromJson(const string& atlasPath, const string& skeletonPath) {
        return loadImpl(atlasPath, skeletonPath, true);
    }

    static AnimationInfo loadFromBinary(const string& atlasPath, const string& skeletonPath) {
        return loadImpl(atlasPath, skeletonPath, false);
    }

    // 2. 设置全局混合时间
    void setGlobalMixTime(float delay) {
        if(animationStateData) {
            animationStateData->setDefaultMix(delay);
        }
    }

    // 3. 设置动画位置
    void setPosition(float pox_x, float pox_y) {
        if(skeleton) {
            skeleton->setX(pox_x);
            skeleton->setY(static_cast<float>(windowHeight) - pox_y);
            skeleton->updateWorldTransform(Physics_Update);
        }
    }

    // 4. 缩放和翻转控制
    void setFlip(bool newFlipX, bool newFlipY) {
        flipX = newFlipX;
        flipY = newFlipY;
        applyTransform();
    }

    void setScale(float scale) {
        this->scale = scale;
        applyTransform();
    }

    // 统一应用变换方法
    void applyTransform() {
        if(skeleton) {
            float actualScaleX = flipX ? -scale : scale;
            float actualScaleY = flipY ? -scale : scale;
            skeleton->setScaleX(actualScaleX);
            skeleton->setScaleY(actualScaleY);
            skeleton->updateWorldTransform(Physics_Update);
        }
    }

    // 5. 动画队列管理
    void enqueueAnimation(const string& name, float delay = 0.0f) {
        animationQueue.emplace(name, delay);
    }

    void clearQueue() {
        queue<pair<string, float>> empty;
        swap(animationQueue, empty);
    }

    string getCurrentAnimation() const {
        return currentTrackEntry ? currentTrackEntry->getAnimation()->getName().buffer() : "";
    }

    // 6. 临时播放动画
    void playTemp(const string& name, bool loop = false, float mixDuration = -1.0f) {
        if(animationState) {
            currentTrackEntry = animationState->setAnimation(0, name.c_str(), loop);
            if(mixDuration >= 0) {
                currentTrackEntry->setMixDuration(mixDuration);
            }
        }
    }

    // 7. 应用加载的数据
    void apply(const AnimationInfo& info) {
        if(info.valid) {
            reset();

            // 初始化动画时长映射
            animationDurations.clear();
            for(const auto& anim : info.animationsWithDuration) {
                animationDurations[anim.first] = anim.second;
            }

            skeleton = new Skeleton(info.skeletonData);
            animationStateData = new AnimationStateData(info.skeletonData);
            animationState = new AnimationState(animationStateData);

            // 设置事件监听器
            animationState->setListener(staticCallback);

            animationStateData->setDefaultMix(defaultMixTime);

            setPosition(static_cast<float>(windowWidth)/2, 0);
            setScale(1.0f);
        }
    }

    // 8. 设置默认动画
    void setDefaultAnimation(const string& name) {
        defaultAnimation = name;
    }

    // 更新逻辑
    void update(float deltaTime) {
        if(animationState && skeleton) {
            animationState->update(deltaTime);
            animationState->apply(*skeleton);

            handleAnimationQueue();
            handleDefaultAnimation();

            skeleton->update(deltaTime);
            skeleton->updateWorldTransform(Physics_Update);
        }

        // 速度平滑处理（120FPS）
        if (glfwGetTime() - lastUpdateTime >= 1.0/120.0) {
            smoothedVelocity = mix(smoothedVelocity, currentVelocity, 0.2f);
            lastUpdateTime = glfwGetTime();
        }
    }

    // 在类中添加新方法，正确设置窗口穿透属性
    static void setWindowClickThrough(GLFWwindow* window, bool through) {
        #ifdef _WIN32
                HWND hwnd = glfwGetWin32Window(window);
                LONG_PTR exStyle = GetWindowLongPtr(hwnd, GWL_EXSTYLE);
                if (through) {
                    exStyle |= WS_EX_TRANSPARENT;
                } else {
                    exStyle &= ~WS_EX_TRANSPARENT;
                }
                SetWindowLongPtr(hwnd, GWL_EXSTYLE, exStyle);
        #endif
        SetWindowPos(hwnd, nullptr, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED);
    }

    // 在update循环中动态更新穿透状态：
    void updateClickThroughState(GLFWwindow* window) {
        if (isDragging) {
            setWindowClickThrough(window, false);
            return;
        }
        double x, y;
        glfwGetCursorPos(window, &x, &y);
        bool shouldThrough = !isMouseOverOpaque(x, y);
        setWindowClickThrough(window, shouldThrough);
    }

    // 渲染
    void render(renderer_t* renderer) {
        if(skeleton && renderer) {
            renderer_draw(renderer, skeleton, true);
        }
    }

    ~SpineAnimation() {
        // 清理当前实例指针
        if (currentInstance == this) {
            currentInstance = nullptr;
        }

        if (handCursor) glfwDestroyCursor(handCursor);
        if (arrowCursor) glfwDestroyCursor(arrowCursor);

        reset();
    }

    bool positionChanged = false;

    GLFWcursor* handCursor = nullptr;
    GLFWcursor* arrowCursor = nullptr;
    bool cursorInOpaqueArea = false;

private:
    static SpineAnimation* currentInstance;

    // 静态回调函数
    static void staticCallback(AnimationState* state, EventType type, TrackEntry* entry, Event* event) {
        if (currentInstance) {
            handleEvent(state, type, entry, event);
        }
    }

    // 事件处理函数
    static void handleEvent(AnimationState* state, EventType type, TrackEntry* entry, Event* event) {
        if (!entry || !entry->getAnimation()) return;

        const string animationName = entry->getAnimation()->getName().buffer();
        switch (type) {
            case EventType_Start:
                cout << CONSOLE_BRIGHT_BLACK <<"[START] Animation: " << animationName << CONSOLE_RESET << endl;
            break;
            case EventType_Complete:
                cout << CONSOLE_BRIGHT_BLACK << "[COMPLETE] Animation: " << animationName << CONSOLE_RESET << endl;
            break;
            default:
                break;
        }
    }

    map<string, float> animationDurations; // 存储动画时长

    void reset() {
        delete skeleton;
        delete animationState;
        delete animationStateData;

        skeleton = nullptr;
        animationState = nullptr;
        animationStateData = nullptr;
        currentTrackEntry = nullptr;
    }

    void handleAnimationQueue() {
        if(!animationQueue.empty() && (!currentTrackEntry || currentTrackEntry->isComplete())) {
            auto& next = animationQueue.front();
            currentTrackEntry = animationState->setAnimation(0, next.first.c_str(), false);
            currentTrackEntry->setMixDuration(next.second);
            animationQueue.pop();
        }
    }

    void handleDefaultAnimation() {
        if(animationQueue.empty() && (!currentTrackEntry || currentTrackEntry->isComplete()) && !defaultAnimation.empty()) {
            currentTrackEntry = animationState->setAnimation(0, defaultAnimation.c_str(), true);
        }
    }

    static AnimationInfo loadImpl(const string& atlasPath, const string& skeletonPath, bool isJson) {
        AnimationInfo info;

        // 加载Atlas
        info.atlas = new Atlas(atlasPath.c_str(), new GlTextureLoader());
        if(info.atlas->getPages().size() == 0) {
            cout << CONSOLE_BRIGHT_RED << "Atlas load error: " << atlasPath << CONSOLE_RESET << endl;
            delete info.atlas;
            return info;
        }
        cout << CONSOLE_BRIGHT_GREEN << "Atlas load down!" << CONSOLE_RESET << endl;

        // 加载SkeletonData
        if(isJson) {
            SkeletonJson json(info.atlas);
            json.setScale(1.0f);
            info.skeletonData = json.readSkeletonDataFile(skeletonPath.c_str());
            if(!info.skeletonData) {
                cout << CONSOLE_BRIGHT_RED << "JSON load error: " << json.getError().buffer() << CONSOLE_RESET << endl;
            }
        } else {
            SkeletonBinary binary(info.atlas);
            binary.setScale(1.0f);
            info.skeletonData = binary.readSkeletonDataFile(skeletonPath.c_str());
            if(!info.skeletonData) {
                cout << CONSOLE_BRIGHT_RED << "Binary load error: " << binary.getError().buffer() << CONSOLE_RESET << endl;
            }
        }

        if(!info.skeletonData) {
            delete info.atlas;
            return info;
        }
        cout << CONSOLE_BRIGHT_GREEN << "Skeleton load down!" << CONSOLE_RESET << endl;

        // 收集动画列表+时长信息
        auto& anims = info.skeletonData->getAnimations();
        info.animationsWithDuration.reserve(anims.size());
        for(size_t i = 0; i < anims.size(); ++i) {
            auto* animation = anims[i];
            info.animationsWithDuration.emplace_back(
                animation->getName().buffer(),
                animation->getDuration()
            );
        }

        info.valid = true;
        return info;
    }

    // 成员变量
    int windowWidth;
    int windowHeight;
    float defaultMixTime;
    bool flipX = false;
    bool flipY = false;
    float scale = 1.0;

    Skeleton* skeleton = nullptr;
    AnimationState* animationState = nullptr;
    AnimationStateData* animationStateData = nullptr;
    TrackEntry* currentTrackEntry = nullptr;

    queue<pair<string, float>> animationQueue;
    string defaultAnimation;

public:
    float getAnimationDuration(const string& name) const {
        auto it = animationDurations.find(name);
        return it != animationDurations.end() ? it->second : 0.0f;
    }

    int minX, maxX, minY, maxY;

    // 工作区尺寸获取
    #ifdef _WIN32
        void updateWorkArea() {
            RECT workArea;
            SystemParametersInfo(SPI_GETWORKAREA, 0, &workArea, 0);
            minX = workArea.left;
            minY = workArea.top;
            maxX = workArea.right - windowWidth;
            maxY = workArea.bottom - windowHeight;

            cout << CONSOLE_BRIGHT_WHITE
                 << "Work Area: "
                 << "minX:" << minX << " "
                 << "maxX:" << maxX << " | "
                 << "minY:" << minY << " "
                 << "maxY:" << maxY
                 << CONSOLE_RESET << endl;
        }
    #endif

private:
    // 鼠标交互相关状态
    bool isDragging = false;
    vec2 dragStartPos{};
    vec2 windowClickOffset{};

    // Alpha检测阈值
    const uint8_t alphaThreshold = 128;

    vec2 windowDragOffset;         // 窗口拖动偏移量（鼠标在窗口内的位置）
    vec2 lastWindowPos;            // 上一次窗口位置
    vec2 currentVelocity;          // 当前速度向量
    vec2 smoothedVelocity;         // 平滑速度向量
    double lastMoveTime;           // 上次移动时间戳
    double lastUpdateTime = 0.0;   // 上次更新时间戳

    vec2 accumulatedDelta;         // 累积位移
    double accumulatedTime = 0.0;  // 累积时间

    // 任务栏位置判断
    #ifdef _WIN32
        struct TaskBarInfo {
            RECT rect{};
            enum Position { Unknown, Top, Bottom, Left, Right } position = Unknown;
            int thickness = 0;

            // 添加构造函数
            TaskBarInfo()
                : rect{0,0,0,0} {}
        };

        static TaskBarInfo getTaskBarInfo() {
            TaskBarInfo info;
            APPBARDATA abd = {};
            abd.cbSize = sizeof(abd);
            if (SHAppBarMessage(ABM_GETTASKBARPOS, &abd)) {
                info.rect = abd.rc;
                info.thickness = abd.rc.bottom - abd.rc.top;

                // 判断任务栏位置
                if (abd.rc.top == 0 && abd.rc.left == 0 && abd.rc.right > abd.rc.bottom) {
                    info.position = TaskBarInfo::Top;
                } else if (abd.rc.bottom == GetSystemMetrics(SM_CYSCREEN)) {
                    info.position = TaskBarInfo::Bottom;
                } else if (abd.rc.left == 0 && abd.rc.top > 0) {
                    info.position = TaskBarInfo::Left;
                } else {
                    info.position = TaskBarInfo::Right;
                }
            }
            return info;
        }
    #endif

    TaskBarInfo taskBar;
    int availableWidth = 0;
    int availableHeight = 0;

public:
    // 设置鼠标回调
    void setupMouseCallbacks(GLFWwindow* window) {
        glfwSetWindowUserPointer(window, this);

        // 鼠标按钮回调
        glfwSetMouseButtonCallback(window, [](GLFWwindow* w, int button, int action, int mods) {
            auto* self = static_cast<SpineAnimation*>(glfwGetWindowUserPointer(w));

            double xPos, yPos;
            glfwGetCursorPos(w, &xPos, &yPos); // 获取窗口内坐标

            // 转换为屏幕坐标
            int windowX, windowY;
            glfwGetWindowPos(w, &windowX, &windowY);
            double screenX = windowX + xPos;
            double screenY = windowY + yPos;

            // 转换为Spine坐标系检测透明度
            double ySpine = self->windowHeight - yPos;

            if (self->isMouseOverOpaque(xPos, ySpine)) {
                if (button == GLFW_MOUSE_BUTTON_LEFT) {
                    if (action == GLFW_PRESS) {
                        cout << CONSOLE_BRIGHT_CYAN << "[INTERACT] Left Pressed @ ("
                             << screenX << ", " << screenY << ")" << CONSOLE_RESET << endl;
                        self->isDragging = true;

                        // 记录窗口相对鼠标的偏移量
                        self->windowDragOffset.x = static_cast<float>(xPos);
                        self->windowDragOffset.y = static_cast<float>(yPos);

                        // 初始化速度计算
                        self->lastWindowPos = vec2(windowX, windowY);
                        self->lastMoveTime = glfwGetTime();
                        self->currentVelocity = vec2(0.0f, 0.0f);

                    } else if (action == GLFW_RELEASE) {
                        cout << CONSOLE_BRIGHT_CYAN << "[INTERACT] Left Relased @ ("
                             << screenX << ", " << screenY << ")" << CONSOLE_RESET << endl;
                        self->isDragging = false;
                    }
                } else if (button == GLFW_MOUSE_BUTTON_RIGHT && action == GLFW_PRESS) {
                    cout << CONSOLE_BRIGHT_CYAN << "[INTERACT] Right Clicked @ ("
                         << xPos << ", " << yPos << ")" << CONSOLE_RESET << endl;
                }
            }
        });

        // 修改鼠标移动回调
        glfwSetCursorPosCallback(window, [](GLFWwindow* w, double xPos, double yPos) {
            auto* self = static_cast<SpineAnimation*>(glfwGetWindowUserPointer(w));

            // 转换到Spine坐标系
            double ySpine = self->windowHeight - yPos;
            bool isOpaque = self->isMouseOverOpaque(xPos, ySpine);

            // 更新光标样式
            if (isOpaque != self->cursorInOpaqueArea) {
                glfwSetCursor(w, isOpaque ? self->handCursor : self->arrowCursor);
                self->cursorInOpaqueArea = isOpaque;
            }

            if (self->isDragging) {
                // 获取当前窗口位置
                int windowX, windowY;
                glfwGetWindowPos(w, &windowX, &windowY);

                // 计算屏幕坐标
                double screenX = windowX + xPos;
                double screenY = windowY + yPos;

                // 计算新窗口位置
                int newX = static_cast<int>(screenX - self->windowDragOffset.x);
                int newY = static_cast<int>(screenY - self->windowDragOffset.y);

                // 添加位置限制, 使用工作区尺寸进行clamp
                #ifdef _WIN32
                    newX = clamp(newX, self->minX, self->maxX);
                    newY = clamp(newY, self->minY, self->maxY);
                #endif

                // 计算时间差和位移差
                double currentTime = glfwGetTime();
                auto deltaTime = static_cast<float>(currentTime - self->lastMoveTime);
                vec2 currentPos(newX, newY);
                vec2 delta = currentPos - self->lastWindowPos;

                // 更新累积量
                self->accumulatedDelta += delta;
                self->accumulatedTime += deltaTime;
                self->lastWindowPos = currentPos;
                self->lastMoveTime = currentTime;

                // 每0.25秒更新速度
                if (self->accumulatedTime >= 0.25) {
                    self->currentVelocity = self->accumulatedDelta / static_cast<float>(self->accumulatedTime);

                    cout << CONSOLE_BRIGHT_BLUE << "[STATE] Move To (" << newX << ", " << newY << ")" << CONSOLE_RESET << endl;

                    // 转换为像素/秒
                    cout << CONSOLE_BRIGHT_YELLOW << "[STATE] Velocity (" << self->currentVelocity.x << ", "
                         << self->currentVelocity.y << ") px/s" << CONSOLE_RESET << endl;

                    // 重置累积量
                    self->accumulatedDelta = vec2(0.0f);
                    self->accumulatedTime = 0.0;
                }

                // 应用窗口位置变化
                glfwSetWindowPos(w, newX, newY);
            }

            self->positionChanged = true;
        });

        // 添加窗口刷新回调确保光标状态正确
        glfwSetWindowRefreshCallback(window, [](GLFWwindow* w) {
            auto* self = static_cast<SpineAnimation*>(glfwGetWindowUserPointer(w));
            double x, y;
            glfwGetCursorPos(w, &x, &y);
            bool isOpaque = self->isMouseOverOpaque(x, self->windowHeight - y);
            glfwSetCursor(w, isOpaque ? self->handCursor : self->arrowCursor);
        });
    }

private:
    // 检测鼠标位置是否在非透明区域
    bool isMouseOverOpaque(double x, double y) {
        if (!skeleton) return false;

        // 确保OpenGL状态正确
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0);
        glReadBuffer(GL_BACK);

        // 转换坐标并限制范围
        int glX = static_cast<int>(clamp(x, 0.0, static_cast<double>(windowWidth) - 1));
        int glY = windowHeight - static_cast<int>(clamp(y, 0.0, static_cast<double>(windowHeight) - 1)) - 1;

        // 读取像素数据
        GLubyte pixel[4];
        glReadPixels(glX, glY, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, &pixel);

        // 降低阈值提高灵敏度
        const uint8_t alphaThreshold = 64;
        return pixel[3] >= alphaThreshold;
    }
};


// 初始化静态成员
SpineAnimation* SpineAnimation::currentInstance = nullptr;

int main() {
    // Windows启用虚拟终端支持
    #ifdef _WIN32
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        if (hOut != INVALID_HANDLE_VALUE) {
            DWORD dwMode = 0;
            GetConsoleMode(hOut, &dwMode);
            dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
            SetConsoleMode(hOut, dwMode);
        }
    #endif

    system("chcp 65001");

    constexpr int WIDTH = 600;
    constexpr int HEIGHT = 480;

    // 初始化窗口
    GLFWwindow* window = init_glfw(WIDTH, HEIGHT);
    if (!window) return -1;

    // 创建渲染器
    renderer_t* renderer = renderer_create();
    renderer_set_viewport_size(renderer, WIDTH, HEIGHT);

    // 创建动画系统
    SpineAnimation animSystem(WIDTH, HEIGHT);

    // 手动更新工作区限制
    #ifdef _WIN32
        animSystem.updateWorkArea();
    #endif

    // 加载资源
    auto info = SpineAnimation::loadFromBinary(
        "data/official/spineboy-pma.atlas",
        "data/official/spineboy-pro.skel"
    );

    // "data/amiya/build_char_1037_amiya3_sale_13.atlas"
    // "data/amiya/build_char_1037_amiya3_sale_13.skel"

    cout << CONSOLE_BRIGHT_MAGENTA << "Animation Durations:" << CONSOLE_RESET << endl;
    for(const auto& anim : info.animationsWithDuration) {
        cout << CONSOLE_BRIGHT_MAGENTA << "- " << anim.first << ": " << anim.second << "s" << CONSOLE_RESET << endl;
    }

    // animSystem 操作区
    if(info.valid) {
        animSystem.apply(info);
        animSystem.setGlobalMixTime(0.2f);
        animSystem.setDefaultAnimation("idle");
        animSystem.enqueueAnimation("run", 0.2f);
        animSystem.enqueueAnimation("idle", 0.2f);
        animSystem.enqueueAnimation("run", 0.2f);
        animSystem.setScale(0.6);
        animSystem.setFlip(false, true);
        animSystem.setPosition(static_cast<float>(WIDTH)/2, 0.0);
        animSystem.playTemp("portal");
    }


    #ifdef _WIN32
        HWND hwnd = glfwGetWin32Window(window); // 设置窗口属性
        SetWindowLong(hwnd, GWL_EXSTYLE,
            GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED); // 启用分层窗口
        SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA); // 设置窗口透明度混合模式
    #endif

    // OpenGL混合设置
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glClearColor(0.0f, 0.0f, 0.0f, 0.0f); // 透明背景

    // 设置鼠标回调
    animSystem.setupMouseCallbacks(window);

    // 主循环
    double lastTime = glfwGetTime();
    while (!glfwWindowShouldClose(window)) {
        // 强制读取最新帧缓冲
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glClear(GL_COLOR_BUFFER_BIT);
        animSystem.render(renderer);
        glfwSwapBuffers(window);

        // 处理事件前确保渲染完成
        glFinish();

        // 处理事件
        glfwPollEvents();

        double currTime = glfwGetTime();
        auto delta = static_cast<float>(currTime - lastTime);
        lastTime = currTime;

        animSystem.update(delta);

        glClear(GL_COLOR_BUFFER_BIT);
        animSystem.render(renderer);

        glfwSwapBuffers(window);
        glfwPollEvents();

        if (animSystem.positionChanged) {
            glfwPollEvents(); // 更频繁处理事件
            animSystem.positionChanged = false;
        }

        animSystem.updateClickThroughState(window);
        glFinish();
    }

    // 清理资源
    renderer_dispose(renderer);
    glfwTerminate();
    return 0;
}
