import os
from PIL import Image, ImageDraw

# 設定棋盤大小
BOARD_WIDTH = 9
BOARD_HEIGHT = 10
CELL_SIZE = 60
IMG_WIDTH = BOARD_WIDTH * CELL_SIZE
IMG_HEIGHT = BOARD_HEIGHT * CELL_SIZE

TILE_DIR = "tiles_bg"
os.makedirs(TILE_DIR, exist_ok=True)

def draw_empty_board():
    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), "burlywood")
    draw = ImageDraw.Draw(img)

    # 畫垂直線
    for i in range(BOARD_WIDTH):
        x = i * CELL_SIZE + CELL_SIZE // 2
        draw.line([(x, CELL_SIZE // 2), (x, IMG_HEIGHT - CELL_SIZE // 2)], fill="black", width=1)

    # 畫水平線（跳過中間河界部分）
    for j in range(BOARD_HEIGHT):
        y = j * CELL_SIZE + CELL_SIZE // 2
        if j == 4 or j == 5:
            # 河界兩邊
            draw.line([(CELL_SIZE // 2, y), (CELL_SIZE * 4 + CELL_SIZE // 2, y)], fill="black", width=1)
            draw.line([(CELL_SIZE * 5 + CELL_SIZE // 2, y), (IMG_WIDTH - CELL_SIZE // 2, y)], fill="black", width=1)
        else:
            draw.line([(CELL_SIZE // 2, y), (IMG_WIDTH - CELL_SIZE // 2, y)], fill="black", width=1)

    # 畫九宮斜線（紅方）
    draw.line([(3 * CELL_SIZE + CELL_SIZE // 2, 0 + CELL_SIZE // 2), (5 * CELL_SIZE + CELL_SIZE // 2, 2 * CELL_SIZE + CELL_SIZE // 2)], fill="black", width=1)
    draw.line([(5 * CELL_SIZE + CELL_SIZE // 2, 0 + CELL_SIZE // 2), (3 * CELL_SIZE + CELL_SIZE // 2, 2 * CELL_SIZE + CELL_SIZE // 2)], fill="black", width=1)

    # 九宮斜線（黑方）
    draw.line([(3 * CELL_SIZE + CELL_SIZE // 2, 7 * CELL_SIZE + CELL_SIZE // 2), (5 * CELL_SIZE + CELL_SIZE // 2, 9 * CELL_SIZE + CELL_SIZE // 2)], fill="black", width=1)
    draw.line([(5 * CELL_SIZE + CELL_SIZE // 2, 7 * CELL_SIZE + CELL_SIZE // 2), (3 * CELL_SIZE + CELL_SIZE // 2, 9 * CELL_SIZE + CELL_SIZE // 2)], fill="black", width=1)

    return img

def save_tiles(img):
    for row in range(BOARD_HEIGHT):
        for col in range(BOARD_WIDTH):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            tile = img.crop((x, y, x + CELL_SIZE, y + CELL_SIZE))
            pos = f"{chr(ord('a') + col)}{row + 1}"
            tile.save(os.path.join(TILE_DIR, f"{pos}.png"))

    print(f"✅ 已輸出 90 張 tile 到 `{TILE_DIR}/` 資料夾")

if __name__ == "__main__":
    board_img = draw_empty_board()
    board_img.save("images/board_empty.png")
    print("✅ 已產生 images/board_empty.png")
    save_tiles(board_img)
