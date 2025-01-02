
from PIL import Image
import os

def combine2Pdf(folderPath, pdfFilePath):
    files = os.listdir(folderPath); pngFiles = []; sources = []; firstImageProcessed = False; output = None
    [(pngFiles.append(os.path.join(folderPath, file)) if 'png' in file else 0) for file in files]
    pngFiles.sort()
    for file in pngFiles:
        pngFile = Image.open(file)
        if pngFile.mode == "RGBA":
            pngFile.load()
            background = Image.new("RGB", pngFile.size, (255, 255, 255))
            background.paste(pngFile, mask=pngFile.split()[3])
            if not firstImageProcessed:
                output = background.copy()
                firstImageProcessed = True
            else:
                sources.append(background)
        else:
            if not firstImageProcessed:
                output = pngFile.copy()
                firstImageProcessed = True
            else:
                sources.append(pngFile)
    output.save(pdfFilePath, "PDF", save_all=True, append_images=sources)

if __name__ == "__main__":
    folder = "神的随波逐流//简谱//"
    pdfFile = "神的随波逐流//简谱//contract.pdf"
    combine2Pdf(folder, pdfFile)


# from PyPDF2 import PdfReader, PdfWriter
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# from io import BytesIO
# from PIL import Image
# 
# # 读取PDF文件
# input_pdf_path = '内容.pdf'  # 替换为你的PDF文件路径
# reader = PdfReader(input_pdf_path)
# writer = PdfWriter()
# 
# # 获取原始PDF第一页的尺寸
# first_page = reader.pages[0]
# media_box = first_page.mediabox  # 这是一个四元组 (x1, y1, x2, y2)
# width = media_box[2] - media_box[0]
# height = media_box[3] - media_box[1]
# 
# # 创建一个包含图片的临时PDF
# image_path = '封面-前.png'  # 替换为你的图片文件路径
# image = Image.open(image_path)
# image_width, image_height = image.size
# 
# # 计算图片缩放比例
# aspect_ratio = min(width / image_width, height / image_height)
# new_image_width = int(image_width * aspect_ratio)
# new_image_height = int(image_height * aspect_ratio)
# 
# # 将图片缩放到第一页的尺寸
# image = image.resize((new_image_width, new_image_height),
#                      Image.Resampling.LANCZOS)
# 
# # 创建一个包含图片的PDF页面
# image_buffer = BytesIO()
# c = canvas.Canvas(image_buffer, pagesize=(width, height))
# x = int((width - new_image_width) / 2)
# y = int((height - new_image_height) / 2)
# 
# c.drawImage(image_path, x, y, width=new_image_width, height=new_image_height)
# c.save()
# 
# # 将图片添加到PDF的首页
# image_buffer.seek(0)
# image_pdf_reader = PdfReader(image_buffer)
# first_page_with_image = image_pdf_reader.pages[0]
# writer.add_page(first_page_with_image)
# 
# # 将原始PDF的页面添加到新PDF中（除了第一页）
# for i, page in enumerate(reader.pages):
#     if i == 0:
#         continue
#     writer.add_page(page)
# 
# # 保存新的PDF文件
# output_pdf_path = 'qq.pdf'  # 输出PDF文件的路径
# with open(output_pdf_path, 'wb') as output_pdf:
#     writer.write(output_pdf)
# 
# print(f'PDF with image inserted successfully saved as {output_pdf_path}')



# from PyPDF2 import PdfFileReader, PdfFileWriter
# 
# 
# def split_single_pdf(read_file, start_page, end_page, pdf_file):
#     fp_read_file = open(read_file, 'rb')
#     pdf_input = PdfFileReader(fp_read_file)
#     pdf_output = PdfFileWriter()
#     for i in range(start_page, end_page):
#         pdf_output.addPage(pdf_input.getPage(i))
#     with open(pdf_file, 'wb') as pdf_out:
#         pdf_output.write(pdf_out)
#     print(f'{read_file}分割{start_page}页-{end_page}页完成，保存为{pdf_file}!')
# 
# 
# if __name__ == '__main__':
#     in_pdf_name = "专业2021版本科培养方案.pdf"
#     out_pdf_name = '内容.pdf'
#     start = 43
#     end = 58
#     split_single_pdf(in_pdf_name, start, end, out_pdf_name)




