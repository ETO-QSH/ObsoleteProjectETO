
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
