#include <stdio.h>

int main() {
    int heightSize = 16;
    int height[] = {4, 6, 1, 4, 6, 5, 1, 4, 1, 2, 6, 5, 6, 1, 4, 2};

    int leftMax = 0, rightMax = 0; // 分别记录左侧和右侧的最大高度
    int left = 0, right = heightSize - 1; // 左指针和右指针
    int result = 0; // 用于存储结果

    do {
        if (height[left] < height[right]) { // 如果左侧的高度小于右侧的高度
            if (height[left] >= leftMax) { // 更新左侧的最大高度
                leftMax = height[left];
            } else { // 左侧结算
                result += leftMax - height[left];
            }
            left++; // 左指针右移
        } else { // 如果左侧的高度大于等于右侧的高度
            if (height[right] >= rightMax) { // 更新右侧的最大高度
                rightMax = height[right];
            } else { // 右侧结算
                result += rightMax - height[right];
            }
            right--; // 右指针左移
        }
    } while (left < right); // 当左指针小于等于右指针时，继续循环

    printf("Trapped water: %d\n", result);
    return 0;
}