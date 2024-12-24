import os
import streamlit as st
import zipfile
from PIL import Image


IMG_PATH = 'image'

def delete_files():
    for filename in list_imgs():
        os.remove(f"./{IMG_PATH}/{filename}")
    for filename in list_zip():
        os.remove(f"./{IMG_PATH}/{filename}")

def list_imgs():
    return [
        filename
        for filename in os.listdir(IMG_PATH)
        if filename.split('.')[-1] in ['jpg', 'jpeg', 'png']
    ]

def list_zip():
    return [
        filename
        for filename in os.listdir(IMG_PATH)
        if filename.split('.')[-1] in ['zip']
    ]

def imageSplitAndPadding(img, color, basename_without_ext):
    width, height = img.size

    new_width = width // 2
    new_height = height // 2

    top_left = img.crop((0, 0, new_width, new_height))
    top_right = img.crop((new_width, 0, width, new_height))
    bottom_left = img.crop((0, new_height, new_width, height))
    bottom_right = img.crop((new_width, new_height, width, height))

    top_padding = height // 2
    bottom_padding = height // 2
    new_width = top_left.width
    new_height = (height // 2) + top_padding + bottom_padding
    new_img = Image.new("RGB", (new_width, new_height), color)
    new_img.paste(top_left, (0, top_padding))
    top_left = new_img

    new_img = Image.new("RGB", (new_width, new_height), color)
    new_img.paste(top_right, (0, top_padding))
    top_right = new_img

    new_img = Image.new("RGB", (new_width, new_height), color)
    new_img.paste(bottom_left, (0, top_padding))
    bottom_left = new_img

    new_img = Image.new("RGB", (new_width, new_height), color)
    new_img.paste(bottom_right, (0, top_padding))
    bottom_right = new_img

    top_left.save(f"{IMG_PATH}/{basename_without_ext} (1)左上.png")
    top_right.save(f"{IMG_PATH}/{basename_without_ext} (2)右上.png")
    bottom_left.save(f"{IMG_PATH}/{basename_without_ext} (3)左下.png")
    bottom_right.save(f"{IMG_PATH}/{basename_without_ext} (4)右下.png")

def crop_center(img):
    width, height = img.size
    original_ratio = width / height
    target_ratio = 16 / 9

    if original_ratio > target_ratio:
        new_width = int(height * target_ratio)
        new_height = height
    else:
        new_width = width
        new_height = int(width / target_ratio)

    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = (width + new_width) // 2
    bottom = (height + new_height) // 2

    return img.crop((left, top, right, bottom))

def add_padding_to_aspect_ratio(img, color):
    width, height = img.size
    original_ratio = width / height
    target_ratio = 16 / 9

    if original_ratio < target_ratio:
        new_width = int(height * target_ratio)
        new_height = height
        result = Image.new("RGB", (new_width, new_height), color)
        result.paste(img, ((new_width - width) // 2, 0))
    else:
        result = img

    return result

def is_aspect_ratio_16_9(img):
    width, height = img.size
    aspect_ratio = width / height
    target_ratio = 16 / 9
    return abs(aspect_ratio - target_ratio) < 0.01  # 小数点以下の誤差を許容


def do(img_path, color):
    img = Image.open(img_path)
    basename_without_ext = os.path.splitext(os.path.basename(img_path))[0]

    flag_crop_center = False
    flag_add_padding_to_aspect_ratio = False

    if is_aspect_ratio_16_9(img) != True:
        img = add_padding_to_aspect_ratio(img, color)

    if flag_crop_center:
        img = crop_center(img)
    if flag_add_padding_to_aspect_ratio:
        img = add_padding_to_aspect_ratio(img, color)

    imageSplitAndPadding(img, color, basename_without_ext)


def download_files(img_path):
    basename_without_ext = os.path.splitext(os.path.basename(img_path))[0]
    files = [
        f"{IMG_PATH}/{basename_without_ext} (1)左上.png",
        f"{IMG_PATH}/{basename_without_ext} (2)右上.png",
        f"{IMG_PATH}/{basename_without_ext} (3)左下.png",
        f"{IMG_PATH}/{basename_without_ext} (4)右下.png"
        ]

    zip_path = f"{IMG_PATH}/{basename_without_ext}.zip"

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file)

    # ZIPファイルの読み込み
    with open(zip_path, 'rb') as zip_file:
        st.download_button(
            label='Download ZIP',
            data=zip_file,
            file_name=zip_path,
            mime='application/zip'
        )
    os.remove(zip_path)

def main():
    delete_files()
    st.subheader('画像を4分割するアプリ（for X）ver.0.1')
    st.markdown('- たぬきがせっせと画像を4分割して上下に余白を付けます')
    file = st.file_uploader('画像をアップロードしてください.', type=['jpg', 'jpeg', 'png'])
    if file:
        st.markdown(f'{file.name} をアップロードしました.')
        img_path = os.path.join(IMG_PATH, file.name)
        with open(img_path, 'wb') as f:
            f.write(file.read())

        #img = Image.open(img_path)
        #st.image(img)

        color = st.color_picker('背景色を選択してください', "#000000")
        if st.button("画像4分割実行"):
            do(img_path, color)
            os.remove(img_path)

            download_files(img_path)
            
    url = "https://x.com/ta_ta_ta_nu_ki"
    st.write("Copyright © 2024 [たたたぬき](%s) #たぬきツール" % url)

if __name__ == '__main__':
    main()
