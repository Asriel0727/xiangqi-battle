import os
import json
from PIL import Image, ImageDraw

# 模擬環境變數，不用 GitHub Token
ISSUE_TITLE = "xiangqi|move|a1-a2|game001"
ISSUE_NUMBER = 1

REPO_NAME = "Asriel0727/xiangqi-battle"
BOARD_FILE = "data/board.json"
README_FILE = "README.md"
BOARD_IMAGE = "images/board.png"

BOARD_WIDTH = 9
BOARD_HEIGHT = 10
CELL_SIZE = 60
IMG_WIDTH = BOARD_WIDTH * CELL_SIZE
IMG_HEIGHT = BOARD_HEIGHT * CELL_SIZE

# 取得當前腳本檔案所在資料夾
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 項目根目錄（xiangqi-battle）
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
PIECE_IMG_DIR = os.path.join(PROJECT_ROOT, "images", "pieces")

def parse_move(issue_title):
    try:
        _, _, move, game_id = issue_title.strip().split('|')
        return move.strip(), game_id.strip()
    except:
        return None, None

def load_board():
    if not os.path.exists(BOARD_FILE):
        print(f"⚠️ {BOARD_FILE} 不存在，使用預設初始棋盤")
        return {
            "turn": "red",
            "board": {
                "a1": "red_rook",
                "b1": "red_knight",
                "c1": "red_elephant",
                "d1": "red_mandarin",
                "e1": "red_king",
                "f1": "red_mandarin",
                "g1": "red_elephant",
                "h1": "red_knight",
                "i1": "red_rook",
                "b3": "red_cannon",
                "h3": "red_cannon",
                "a4": "red_pawn",
                "c4": "red_pawn",
                "e4": "red_pawn",
                "g4": "red_pawn",
                "i4": "red_pawn",
                "a10": "black_rook",
                "b10": "black_knight",
                "c10": "black_elephant",
                "d10": "black_mandarin",
                "e10": "black_king",
                "f10": "black_mandarin",
                "g10": "black_elephant",
                "h10": "black_knight",
                "i10": "black_rook",
                "b8": "black_cannon",
                "h8": "black_cannon",
                "a7": "black_pawn",
                "c7": "black_pawn",
                "e7": "black_pawn",
                "g7": "black_pawn",
                "i7": "black_pawn"
            }
        }
    with open(BOARD_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"✅ 從 {BOARD_FILE} 載入棋盤資料")
        # 若讀取的資料裡沒有 "board" 這層，就包成一層
        if "board" not in data:
            print("⚠️ 載入的資料缺少 'board'，自動包裝中...")
            data = {
                "turn": "red",
                "board": data
            }
        return data


def save_board(data):
    os.makedirs("data", exist_ok=True)
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def pos_to_xy(pos):
    col = ord(pos[0].lower()) - ord('a')
    row = int(pos[1:]) - 1
    # 因為圖片y軸是從上到下，象棋第1行在最下面，所以要倒轉y軸
    y = (BOARD_HEIGHT - 1 - row) * CELL_SIZE
    x = col * CELL_SIZE
    return x, y

def draw_board_image(board_data):
    os.makedirs("images", exist_ok=True)

    print(f"🛠 PIECE_IMG_DIR 實際路徑：{PIECE_IMG_DIR}")

    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), "burlywood")
    draw = ImageDraw.Draw(img)

    # 畫網格線
    for i in range(BOARD_WIDTH):
        x = i * CELL_SIZE + CELL_SIZE // 2
        draw.line([(x, CELL_SIZE // 2), (x, IMG_HEIGHT - CELL_SIZE // 2)], fill="black", width=2)
    for j in range(BOARD_HEIGHT):
        y = j * CELL_SIZE + CELL_SIZE // 2
        draw.line([(CELL_SIZE // 2, y), (IMG_WIDTH - CELL_SIZE // 2, y)], fill="black", width=2)

    board_map = board_data.get("board", {})
    print(f"DEBUG: 棋盤中共有 {len(board_map)} 個棋子")

    # 畫棋子圖片
    for pos, piece in board_map.items():
        x, y = pos_to_xy(pos)
        print(f"DEBUG: 嘗試載入棋子 {piece} 位置 {pos} (像素座標 {x},{y})")
        try:
            piece_path = os.path.join(PIECE_IMG_DIR, f"{piece}.png")
            print(f"DEBUG: 棋子圖片路徑：{piece_path}")
            piece_img = Image.open(piece_path).resize((CELL_SIZE, CELL_SIZE))
            img.paste(piece_img, (x, y), piece_img.convert("RGBA"))
        except Exception as e:
            print(f"⚠️ 無法載入 {piece}：{e}")

    img.save(BOARD_IMAGE)
    print("✅ 棋盤圖片生成完成：", BOARD_IMAGE)

def main():
    board = load_board()
    print("DEBUG: 讀取到的棋盤資料 =", board)
    draw_board_image(board)

if __name__ == "__main__":
    main()
