import streamlit as st
import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

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

    # 每两个二维码合并为一张图片
    total_width = qr_images[0][1].width * 2 + 10  # 两个二维码的宽度加间距
    max_height = max(img[1].height for img in qr_images)

    # 遍历二维码列表，每两个二维码合并为一张图片
    combined_images = []
    for i in range(0, len(qr_images), 2):
        img1_code_id, img1 = qr_images[i]
        img2_code_id, img2 = qr_images[i + 1] if i + 1 < len(qr_images) else (None, None)

        # 创建一个新的图像，容纳两个二维码
        combined_img = Image.new('RGB', (total_width, max_height), 'white')

        # 将第一个二维码放在左边
        combined_img.paste(img1, (0, 0))

        # 将第二个二维码放在右边，间距为 1mm
        if img2:
            combined_img.paste(img2, (img1.width + 10, 0))

        # 将合并后的二维码图像转换为可以在 Streamlit 中显示的格式
        combined_images.append(combined_img)

    # 显示合并后的二维码图像
    for i, combined_img in enumerate(combined_images):
        st.image(combined_img, caption=f"二维码组合 {i + 1}", use_column_width=True)

        # 提供下载链接
        combined_img_path = f"combined_qrcode_{i + 1}.png"
        combined_img.save(combined_img_path)

        with open(combined_img_path, "rb") as file:
            st.download_button(
                label=f"下载二维码组合 {i + 1}",
                data=file,
                file_name=combined_img_path,
                mime="image/png"
            )
