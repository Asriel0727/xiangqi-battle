import os
import json
from github import Github
from PIL import Image, ImageDraw
from datetime import datetime

# 環境變數
ISSUE_TITLE = os.environ.get("ISSUE_TITLE")
ISSUE_NUMBER = int(os.environ.get("ISSUE_NUMBER"))
TOKEN = os.environ.get("GITHUB_TOKEN")

REPO_NAME = "Asriel0727/xiangqi-battle"
BOARD_FILE = "data/board.json"
README_FILE = "README.md"
BOARD_IMAGE = "images/board.png"

# 畫面格局
BOARD_WIDTH = 9
BOARD_HEIGHT = 10
CELL_SIZE = 60
IMG_WIDTH = BOARD_WIDTH * CELL_SIZE
IMG_HEIGHT = BOARD_HEIGHT * CELL_SIZE

PIECE_IMG_DIR = "images/pieces"

def parse_move(issue_title):
    try:
        _, category, action, game_id = issue_title.strip().split('|')
        return category.strip(), action.strip(), game_id.strip()
    except Exception as e:
        print(f"⚠️ 解析 ISSUE_TITLE 失敗: {e}")
        return None, None, None
        
def reset_board():
    print("♟️ 正在建立新的棋局...")
    board = {
        "turn": "red",
        "board": {
            "a1": "red_rook", "b1": "red_knight", "c1": "red_elephant", "d1": "red_mandarin",
            "e1": "red_king", "f1": "red_mandarin", "g1": "red_elephant", "h1": "red_knight", "i1": "red_rook",
            "b3": "red_cannon", "h3": "red_cannon",
            "a4": "red_pawn", "c4": "red_pawn", "e4": "red_pawn", "g4": "red_pawn", "i4": "red_pawn",
            "a10": "black_rook", "b10": "black_knight", "c10": "black_elephant", "d10": "black_mandarin",
            "e10": "black_king", "f10": "black_mandarin", "g10": "black_elephant", "h10": "black_knight", "i10": "black_rook",
            "b8": "black_cannon", "h8": "black_cannon",
            "a7": "black_pawn", "c7": "black_pawn", "e7": "black_pawn", "g7": "black_pawn", "i7": "black_pawn"
        },
        "history": []
    }
    save_board(board)
    draw_board_image(board)
    update_readme("新對局開始", board["turn"])
    return board

def load_board():
    if not os.path.exists(BOARD_FILE):
        print("⚠️ 找不到 board.json，初始化空棋盤")
        return {"turn": "red", "board": {}, "history": []}
    
    with open(BOARD_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"✅ 從 {BOARD_FILE} 載入棋盤資料")

    # 如果是舊格式（直接是 pos-to-piece dict），轉換為新版格式
    if all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        print("⚠️ 偵測到舊格式棋盤，自動轉換為新格式")
        data = {
            "turn": "red",
            "board": data,
            "history": []
        }

    # 確保基本欄位存在
    if "board" not in data:
        data["board"] = {}
    if "turn" not in data:
        data["turn"] = "red"
    if "history" not in data:
        data["history"] = []

    return data

def save_board(data):
    os.makedirs("data", exist_ok=True)
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ 棋盤資料已儲存到 {BOARD_FILE}")

def update_readme(move, turn):
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    if "✅ 最新一步：" in content:
        content = content.rsplit("✅ 最新一步：", 1)[0].strip()

    chinese_turn = "紅" if turn == "red" else "黑"
    
    # 加上隨機參數避免快取
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    image_url = f"images/board.png?{timestamp}"

    new_section = f"""

![current board]({image_url})

✅ 最新一步：{move}  
🎯 現在輪到：**{chinese_turn}方**
"""
    content = content.split("## ⚫️ 當前棋盤")[0] + f"## ⚫️ 當前棋盤\n\n{new_section}"

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ README.md 已更新，目前輪到：", turn)

def post_comment(repo, issue_num, body):
    issue = repo.get_issue(number=issue_num)
    issue.create_comment(body)
    issue.edit(state="closed")
    print(f"✅ 已於 Issue #{issue_num} 留言並關閉")

def pos_to_xy(pos):
    col = ord(pos[0].lower()) - ord('a')
    row = int(pos[1:]) - 1
    # 反轉 Y 軸，讓棋盤1排在下方
    y = (BOARD_HEIGHT - 1 - row) * CELL_SIZE
    x = col * CELL_SIZE
    print(f"DEBUG: 位置 {pos} 轉換成像素座標 ({x}, {y})")
    return x, y

def draw_board_image(board_data):
    os.makedirs("images", exist_ok=True)

    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), "burlywood")
    draw = ImageDraw.Draw(img)

    # 畫網格線
    for i in range(BOARD_WIDTH):
        x = i * CELL_SIZE + CELL_SIZE // 2
        draw.line([(x, CELL_SIZE // 2), (x, IMG_HEIGHT - CELL_SIZE // 2)], fill="black", width=1)
    for j in range(BOARD_HEIGHT):
        y = j * CELL_SIZE + CELL_SIZE // 2
        draw.line([(CELL_SIZE // 2, y), (IMG_WIDTH - CELL_SIZE // 2, y)], fill="black", width=1)

    # 畫棋子圖片
    total_pieces = 0
    for pos, piece in board_data.get("board", {}).items():
        x, y = pos_to_xy(pos)
        try:
            piece_path = os.path.join(PIECE_IMG_DIR, f"{piece}.png")
            piece_img = Image.open(piece_path).resize((CELL_SIZE, CELL_SIZE))
            img.paste(piece_img, (x, y), piece_img.convert("RGBA"))
            total_pieces += 1
        except Exception as e:
            print(f"⚠️ 無法載入棋子圖檔 {piece}，錯誤：{e}")

    img.save(BOARD_IMAGE)
    print(f"✅ 棋盤圖片生成成功，總共繪製了 {total_pieces} 個棋子，存成 {BOARD_IMAGE}")

def main():
    category, action, game_id = parse_move(ISSUE_TITLE)
    if not category or not action:
        print("⚠️ 無法解析 Issue Title，請檢查格式")
        return

    g = Github(TOKEN)
    repo = g.get_repo(REPO_NAME)

    if category == "chess" and action == "new":
        board = reset_board()
        post_comment(repo, ISSUE_NUMBER, "🆕 已啟動新對局，請紅方先行。")
        return

    if category == "move":
        board = load_board()
        move = action

        if "history" not in board:
            board["history"] = []
        board["history"].append(move)

        # 執行移動（簡化，不檢查合法性）
        src, dst = move.split('-')
        piece = board["board"].pop(src, None)
        if piece:
            board["board"][dst] = piece
            board["turn"] = "black" if board["turn"] == "red" else "red"
        else:
            print(f"⚠️ 沒有找到 {src} 的棋子，無法移動")

        save_board(board)
        draw_board_image(board)
        update_readme(move, board["turn"])
        post_comment(repo, ISSUE_NUMBER, f"✅ 步驟 {move} 已執行，現在輪到 **{board['turn']}** 方")
        return

    print("⚠️ 不支援的指令類型")

if __name__ == "__main__":
    main()
