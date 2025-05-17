import streamlit as st
import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
import io

# 生成二维码并返回图像
def generate_qrcode_with_text(sample_name, code_id, dpi=500, width_mm=12, height_mm=12):
    mm_to_inch = 25.4  # 1 英寸 = 25.4mm
    desired_width_pixels = int((width_mm / mm_to_inch) * dpi)
    desired_height_pixels = int((height_mm / mm_to_inch) * dpi)
    
    # 创建二维码对象
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小，1为最小，越大二维码越复杂
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 错误纠正级别
        box_size=desired_width_pixels // 33,  # 计算 box_size
        border=4,  # 边框宽度
    )

    # 设置二维码内容为 Sample Name
    qr.add_data(sample_name)
    qr.make(fit=True)

    # 创建二维码图像
    img = qr.make_image(fill='black', back_color='white')

    # 获取二维码图像的宽度和高度
    img = img.resize((desired_width_pixels, desired_height_pixels))  # 调整二维码大小

    # 创建一个新的图像，包含二维码和文本
    new_img = Image.new('RGB', (img.width, img.height + 50), 'white')  # 新图像高度增加50px
    new_img.paste(img, (0, 0))

    # 在二维码下方添加 Code_ID 文本
    draw = ImageDraw.Draw(new_img)
    
    # 使用大字体（这里可以调整字体大小）
    try:
        font = ImageFont.truetype("arial.ttf", 24)  # 使用字体 Arial，大小为24
    except IOError:
        font = ImageFont.load_default()  # 如果 Arial 字体不可用，使用默认字体

    # 使用 textbbox 来获取文本的宽度和高度
    text_bbox = draw.textbbox((0, 0), code_id, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # 将文本居中并调整为靠近二维码
    text_position = ((img.width - text_width) // 2, img.height + 5)  # 更靠近二维码
    draw.text(text_position, code_id, font=font, fill='black')

    return new_img

# Streamlit 上传 CSV 文件
st.title('样本二维码生成器')

# 上传样本信息 CSV 文件
uploaded_file = st.file_uploader("上传样本信息文件", type=["csv"])

if uploaded_file is not None:
    # 读取 CSV 文件
    data = pd.read_csv(uploaded_file)
    
    # 显示 CSV 数据
    st.write("上传的样本信息：")
    st.dataframe(data)
    
    # 生成二维码
    qr_images = []
    for index, row in data.iterrows():
        sample_name = row['Sample Name']
        code_id = row['Code_ID']
        
        # 生成二维码
        qr_img = generate_qrcode_with_text(sample_name, code_id)
        
        # 将二维码图像保存到列表
        qr_images.append((code_id, qr_img))

    # 只展示前四个二维码
    display_images = qr_images[:4]

    # 显示前四个二维码
    for i, (code_id, img) in enumerate(display_images):
        st.image(img, caption=f"二维码 {i + 1} - {code_id}", use_column_width=True)

    # 创建一个 ZIP 文件以供一键下载所有二维码
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, (code_id, img) in enumerate(qr_images):
            img_name = f"qrcode_{code_id}.png"
            img_path = os.path.join("/tmp", img_name)
            img.save(img_path)
            zip_file.write(img_path, arcname=img_name)

    zip_buffer.seek(0)

    # 提供下载所有二维码的 ZIP 文件
    st.download_button(
        label="下载所有二维码 (ZIP)",
        data=zip_buffer,
        file_name="qrcodes.zip",
        mime="application/zip"
    )
