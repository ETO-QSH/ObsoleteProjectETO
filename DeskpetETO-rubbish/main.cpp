#include <windows.h>
#include <gl/GL.h>
#include <spine/spine.h>
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

using namespace spine;

// 自定义纹理加载器（使用stb_image）
class Win32TextureLoader : public TextureLoader {
public:
    void load(AtlasPage& page, const String& path) override {
        int width, height, channels;
        stbi_set_flip_vertically_on_load(true);
        unsigned char* data = stbi_load(path.buffer(), &width, &height, &channels, 4);

        if (!data) {
            printf("Failed to load texture: %s\n", path.buffer());
            return;
        }

        printf("Loaded texture: %s, size: %dx%d\n", path.buffer(), width, height);

        GLuint textureID;
        glGenTextures(1, &textureID);
        glBindTexture(GL_TEXTURE_2D, textureID);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

        stbi_image_free(data);

        printf("Texture ID: %u\n", textureID);

        page.texture = reinterpret_cast<void*>(textureID);
        page.width = width;
        page.height = height;
    }

    void unload(void* texture) override {
        auto textureID = static_cast<GLuint>(reinterpret_cast<uintptr_t>(texture));
        glDeleteTextures(1, &textureID);
    }
};

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    switch (message) {
        case WM_DESTROY:
            PostQuitMessage(0);
            break;
        default:
            return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // 窗口初始化
    WNDCLASS wc = {};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = GetModuleHandle(nullptr);
    wc.lpszClassName = "SpineWindowClass";
    wc.style = CS_OWNDC;
    RegisterClass(&wc);

    HWND hWnd = CreateWindow(
        "SpineWindowClass",
        "Spine Demo",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT,
        800, 600,
        nullptr, nullptr, hInstance, nullptr
    );

    // OpenGL上下文初始化
    HDC hDC = GetDC(hWnd);
    PIXELFORMATDESCRIPTOR pfd = {
        sizeof(PIXELFORMATDESCRIPTOR),
        1,
        PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
        PFD_TYPE_RGBA,
        32,
        0, 0, 0, 0, 0, 0,
        0,
        0,
        0,
        0, 0, 0, 0,
        24,  // Depth buffer
        0,
        0,
        PFD_MAIN_PLANE,
        0,
        0, 0, 0
    };
    int pixelFormat = ChoosePixelFormat(hDC, &pfd);
    SetPixelFormat(hDC, pixelFormat, &pfd);
    HGLRC hRC = wglCreateContext(hDC);
    wglMakeCurrent(hDC, hRC);

    printf("OpenGL context created successfully.\n");

    // Spine资源加载
    Win32TextureLoader textureLoader;
    auto* atlas = new Atlas("D:/Work Files/DesmosETO-cpp/assets/spine/spineboy/spineboy-pma.atlas", &textureLoader);
    if (atlas->getPages().size() == 0) {
        MessageBox(hWnd, TEXT("Failed to load atlas"), TEXT("Error"), MB_OK);
        return 1;
    } else {
        printf("Atlas data loaded successfully.\n");
    }

    SkeletonJson json(new AtlasAttachmentLoader(atlas));
    json.setScale(0.5f); // 设置缩放比例

    SkeletonData* skeletonData = json.readSkeletonDataFile("D:/Work Files/DesmosETO-cpp/assets/spine/spineboy/spineboy-pro.json");
    if (!skeletonData) {
        MessageBoxA(hWnd, json.getError().buffer(), "Error", MB_OK);
        return 1;
    } else {
        printf("Skeleton data loaded successfully.\n");
    }

    auto* skeleton = new Skeleton(skeletonData);
    skeleton->setPosition(400, 100); // 设置初始位置

    auto* stateData = new AnimationStateData(skeletonData);
    auto* state = new AnimationState(stateData);
    state->setAnimation(0, "walk", true);

    // stateData->setDefaultMix(0.2f);
    // stateData->setMix("walk", "jump", 0.4f);

    // 视口设置
    glViewport(0, 0, 800, 600);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, 800, 0, 600, -1, 1);
    glMatrixMode(GL_MODELVIEW);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    // 主循环
    MSG msg = {};
    LARGE_INTEGER freq, start, end;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&start);

    ShowWindow(hWnd, nCmdShow);
    printf("The window comes out.\n");

    while (true) {
        if (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
            if (msg.message == WM_QUIT) break;
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }

        // 计算deltaTime
        QueryPerformanceCounter(&end);
        float delta = (end.QuadPart - start.QuadPart) / (float)freq.QuadPart;
        start = end;

        // 更新动画状态
        state->update(delta);
        state->apply(*skeleton);
        skeleton->setPosition(400, 100); // 设置骨架位置
        skeleton->updateWorldTransform(Physics_Update);

        // 渲染
        glClearColor(0.15f, 0.15f, 0.2f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        printf("Get ready to start rendering.\n");

        // 渲染附件
        for (unsigned i = 0; i < skeleton->getSlots().size(); ++i) {
            Slot* slot = skeleton->getSlots()[i];
            Attachment* attachment = slot->getAttachment();

            if (!attachment) {
                printf("Slot %u: No attachment\n", i);
                continue;
            }

            // 手动判断附件类型
            if (auto region = dynamic_cast<RegionAttachment*>(attachment)) {
                float vertices[8];
                region->computeWorldVertices(*slot, vertices, 0, 2);

                printf("Slot %u: Attachment type: RegionAttachment\n", i);
                printf("Vertices: ");
                for (float vertice : vertices) {
                    printf("%f ", vertice);
                }
                printf("\n");

                // 获取纹理
                auto* atlasRegion = (AtlasRegion*)region->getRegion();
                if (!atlasRegion) {
                    printf("AtlasRegion is null.\n");
                    continue;
                }

                auto* texturePage = atlasRegion->page;
                if (!texturePage) {
                    printf("TexturePage is null.\n");
                    continue;
                }

                auto texturePtr = reinterpret_cast<uintptr_t>(texturePage->texture);
                auto texture = static_cast<GLuint>(texturePtr);

                printf("Texture ID: %u\n", texture); // 打印纹理 ID

                // 渲染逻辑
                glBindTexture(GL_TEXTURE_2D, texture);
                glBegin(GL_TRIANGLE_STRIP);
                for (int v = 0; v < 4; ++v) {
                    glTexCoord2f(region->getUVs()[v*2], region->getUVs()[v*2+1]);
                    glVertex2f(vertices[v*2] + skeleton->getX(), vertices[v*2+1] + skeleton->getY());
                }
                glEnd();

                GLenum error = glGetError();
                if (error != GL_NO_ERROR) {
                    printf("OpenGL error: %d\n", error);
                }
            } else if (auto mesh = dynamic_cast<MeshAttachment*>(attachment)) {
                printf("Slot %u: Attachment type: MeshAttachment\n", i);
                // 添加处理 MeshAttachment 的逻辑
            } else if (auto boundingBox = dynamic_cast<BoundingBoxAttachment*>(attachment)) {
                printf("Slot %u: Attachment type: BoundingBoxAttachment\n", i);
                // 添加处理 BoundingBoxAttachment 的逻辑
            } else if (auto path = dynamic_cast<PathAttachment*>(attachment)) {
                printf("Slot %u: Attachment type: PathAttachment\n", i);
                // 添加处理 PathAttachment 的逻辑
            } else {
                printf("Slot %u: Unknown attachment type\n", i);
            }
        }

        SwapBuffers(hDC);
    }

    // 清理资源
    delete state;
    delete stateData;
    delete skeleton;
    delete skeletonData;
    delete atlas;

    wglDeleteContext(hRC);
    ReleaseDC(hWnd, hDC);
    return 0;
}