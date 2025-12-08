from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import os


def long_image_to_a4_pdf(
        image_path,
        output_pdf_path,
        dpi=300,
        margin_left_cm=0,
        margin_right_cm=0,
        margin_top_cm=2.1,
        margin_bottom_cm=2.1,
        page_format="portrait"
):
    """
    将长图按 Word 普通页边距缩放并分页导出为 PDF

    参数:
        image_path: 输入图片路径
        output_pdf_path: 输出 PDF 路径
        dpi: 分辨率（默认 300，适合打印）
        margin_left_cm: 左边距（cm）
        margin_right_cm: 右边距（cm）
        margin_top_cm: 上边距（cm）
        margin_bottom_cm: 下边距（cm）
        page_format: 页面方向，"portrait"=纵向，"landscape"=横向
    """

    # ==================== 单位换算函数 ====================
    def mm_to_px(mm):
        return int(mm * dpi / 25.4)

    def cm_to_px(cm):
        return int(cm * dpi / 2.54)

    # ==================== 设置页面尺寸 ====================
    if page_format == "portrait":
        a4_width_mm = 210  # A4 宽度（纵向）
        a4_height_mm = 297  # A4 高度
    elif page_format == "landscape":
        a4_width_mm = 297  # A4 宽度（横向）
        a4_height_mm = 210  # A4 高度
    else:
        raise ValueError("page_format 必须是 'portrait' 或 'landscape'")

    a4_width_px = mm_to_px(a4_width_mm)
    a4_height_px = mm_to_px(a4_height_mm)

    # 转换边距为像素
    margin_left = cm_to_px(margin_left_cm)
    margin_right = cm_to_px(margin_right_cm)
    margin_top = cm_to_px(margin_top_cm)
    margin_bottom = cm_to_px(margin_bottom_cm)

    # 检查边距是否合理
    if margin_left + margin_right >= a4_width_px:
        raise ValueError("左右边距之和超过页面宽度！")
    if margin_top + margin_bottom >= a4_height_px:
        raise ValueError("上下边距之和超过页面高度！")

    # 可打印区域
    printable_width = a4_width_px - margin_left - margin_right
    printable_height = a4_height_px - margin_top - margin_bottom

    print(f"A4 尺寸 ({page_format}): {a4_width_px} x {a4_height_px} 像素 (@{dpi} DPI)")
    print(f"边距: 左={margin_left}px, 右={margin_right}px, 上={margin_top}px, 下={margin_bottom}px")
    print(f"可打印区域: {printable_width} x {printable_height} 像素")

    # ==================== 加载并缩放原图 ====================
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"未找到图片文件: {image_path}")

    image = Image.open(image_path)
    img_width, img_height = image.size
    print(f"原图尺寸: {img_width} x {img_height}")

    if img_width <= 0 or img_height <= 0:
        raise ValueError("无效的图片尺寸")

    # 计算缩放比例（按可打印宽度等比缩放）
    scale_factor = printable_width / img_width
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)

    print(f"缩放后尺寸: {new_width} x {new_height}")

    # 使用高质量重采样
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # ==================== 分页裁剪并生成 PDF 页面 ====================
    pages = []
    a4_canvas = Image.new('RGB', (a4_width_px, a4_height_px), 'white')  # 白色背景

    y_offset = 0
    page_index = 0

    while y_offset < new_height:
        # 裁剪当前页内容（高度不超过可打印区域）
        end_y = min(y_offset + printable_height, new_height)
        box = (0, y_offset, new_width, end_y)
        cropped = resized_image.crop(box)

        # 创建新页面
        page = a4_canvas.copy()

        # 将裁剪图粘贴到可打印区域（从 margin_left, margin_top 开始）
        paste_x = margin_left
        paste_y = margin_top
        page.paste(cropped, (paste_x, paste_y))

        pages.append(page)
        y_offset += printable_height
        page_index += 1

    # ==================== 保存为 PDF ====================
    if not pages:
        print("❌ 没有生成任何页面")
        return

    # 保存为多页 PDF
    pages[0].save(
        output_pdf_path,
        save_all=True,
        append_images=pages[1:],
        resolution=dpi,
        quality=95
    )

    print(f"✅ 成功生成 PDF: {output_pdf_path}")
    print(f"📄 共 {len(pages)} 页，每页 A4 ({'纵向' if page_format == 'portrait' else '横向'})")
    print(f"📎 提示: 可在 Word 中打印对比效果")


def add_cover_to_pdf(cover_pdf_path, content_pdf_path, output_pdf_path):
    """
    将一个单页 PDF 作为封面，插入到内容 PDF 的最前面

    参数:
        cover_pdf_path: 封面 PDF 路径（仅一页）
        content_pdf_path: 内容 PDF 路径（可多页）
        output_pdf_path: 输出合并后的 PDF 路径
    """
    # 检查文件是否存在
    if not os.path.exists(cover_pdf_path):
        raise FileNotFoundError(f"未找到封面文件: {cover_pdf_path}")
    if not os.path.exists(content_pdf_path):
        raise FileNotFoundError(f"未找到内容文件: {content_pdf_path}")

    # 创建 PDF 读取器
    cover_reader = PdfReader(cover_pdf_path)
    content_reader = PdfReader(content_pdf_path)

    # 创建写入器
    writer = PdfWriter()

    # 先添加封面（第一页）
    writer.add_page(cover_reader.pages[0])

    # 再添加内容的所有页
    for page in content_reader.pages:
        writer.add_page(page)

    # 保存最终 PDF
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    print(f"✅ 封面已添加，最终 PDF 已保存: {output_pdf_path}")
    print(f"📄 总页数: {len(writer.pages)} 页（封面 + {len(content_reader.pages)} 页内容）")


# =============== 使用示例 ===============
if __name__ == "__main__":
    # 输入输出路径
    input_image = "TECHNICAL_REPORT.png"  # 替换为你的图片路径
    content_pdf = "output_word_style.pdf"  # 输出 PDF 文件名

    # 执行转换（使用 Word 普通边距）
    long_image_to_a4_pdf(
        image_path=input_image,
        output_pdf_path=content_pdf,
        dpi=300,  # 高质量打印
        page_format="portrait"  # 可改为 "landscape" 横向
    )

    cover_pdf = "封面.pdf"  # 你的单页封面 PDF
    final_output = "final_document.pdf"

    add_cover_to_pdf(
        cover_pdf_path=cover_pdf,
        content_pdf_path=content_pdf,
        output_pdf_path=final_output
    )
