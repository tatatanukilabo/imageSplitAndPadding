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
    # IMG_PATH 内の画像ファイルを列挙
    return [
        filename
        for filename in os.listdir(IMG_PATH)
        if filename.split('.')[-1] in ['jpg', 'jpeg', 'png']
    ]

def list_zip():
    # IMG_PATH 内の画像ファイルを列挙
    return [
        filename
        for filename in os.listdir(IMG_PATH)
        if filename.split('.')[-1] in ['zip']
    ]

def imageSplitAndPadding(img, color, basename_without_ext):
    # 画像の幅と高さを取得
    width, height = img.size

    # 4分割するための各部分の幅と高さ
    new_width = width // 2
    new_height = height // 2

    # 4つの部分に分割
    top_left = img.crop((0, 0, new_width, new_height))
    top_right = img.crop((new_width, 0, width, new_height))
    bottom_left = img.crop((0, new_height, new_width, height))
    bottom_right = img.crop((new_width, new_height, width, height))

    # 4つの画像の上下に余白をつける
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

    # 分割した画像を保存
    top_left.save(f"{IMG_PATH}/{basename_without_ext} (1)左上.png")
    top_right.save(f"{IMG_PATH}/{basename_without_ext} (2)右上.png")
    bottom_left.save(f"{IMG_PATH}/{basename_without_ext} (3)左下.png")
    bottom_right.save(f"{IMG_PATH}/{basename_without_ext} (4)右下.png")

def crop_center(img):
    width, height = img.size
    original_ratio = width / height
    target_ratio = 16 / 9

    if original_ratio > target_ratio:
        # 幅が長い場合、中央部分を切り抜く
        new_width = int(height * target_ratio)
        new_height = height
    else:
        # 高さが長い場合、中央部分を切り抜く
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
        # 16:9にするために幅を拡張する
        new_width = int(height * target_ratio)
        new_height = height
        result = Image.new("RGB", (new_width, new_height), color)
        result.paste(img, ((new_width - width) // 2, 0))
    else:
        # すでに16:9以上の比率ならそのまま
        result = img

    return result

def is_aspect_ratio_16_9(img):
    width, height = img.size
    aspect_ratio = width / height
    target_ratio = 16 / 9
    return abs(aspect_ratio - target_ratio) < 0.01  # 小数点以下の誤差を許容


def do(img_path, color):
    # 画像を読み込む
    img = Image.open(img_path)
    basename_without_ext = os.path.splitext(os.path.basename(img_path))[0]

    flag_crop_center = False
    flag_add_padding_to_aspect_ratio = False

    if is_aspect_ratio_16_9(img) != True:
        img = add_padding_to_aspect_ratio(img, color)

    if flag_crop_center:
        # 画像を中央で切り抜いて16:9に変換
        img = crop_center(img)
    if flag_add_padding_to_aspect_ratio:
        img = add_padding_to_aspect_ratio(img, color)

    imageSplitAndPadding(img, color, basename_without_ext)


def download_files(img_path):
    basename_without_ext = os.path.splitext(os.path.basename(img_path))[0]
    # ダウンロードしたいファイルのリスト
    files = [
        f"{IMG_PATH}/{basename_without_ext} (1)左上.png",
        f"{IMG_PATH}/{basename_without_ext} (2)右上.png",
        f"{IMG_PATH}/{basename_without_ext} (3)左下.png",
        f"{IMG_PATH}/{basename_without_ext} (4)右下.png"
        ]

    # ZIPファイルのパス
    zip_path = f"{IMG_PATH}/{basename_without_ext}.zip"

    # ZIPファイルを作成
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
    st.write("#たぬきツール")
    st.markdown('# 画像を4分割するアプリ（for X）')
    file = st.file_uploader('画像をアップロードしてください.', type=['jpg', 'jpeg', 'png'])
    if file:
        st.markdown(f'{file.name} をアップロードしました.')
        img_path = os.path.join(IMG_PATH, file.name)
        # 画像を保存する
        with open(img_path, 'wb') as f:
            f.write(file.read())

        # 保存した画像を表示
        #img = Image.open(img_path)
        #st.image(img)

        color = st.color_picker('背景色を選択してください', "#000000")
        if st.button("画像4分割実行"):
            do(img_path, color)
            os.remove(img_path)

            download_files(img_path)

if __name__ == '__main__':
    main()
