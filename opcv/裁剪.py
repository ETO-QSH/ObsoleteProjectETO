
import cv2

# 读取图像
image = cv2.imread('pic\\screenshot_8.jpg')


x1, y1 = 120, 465  # 左上角坐标
x2, y2 = 250, 540  # 右下角坐标

# 裁剪图像
cropped_image = image[y1:y2, x1:x2]

# 保存裁剪后的图像
cv2.imwrite('cropped_image_run.jpg', cropped_image)

# 显示裁剪后的图像
cv2.imshow('Cropped Image', cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
