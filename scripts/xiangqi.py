import os
import json
from github import Github
from PIL import Image, ImageDraw
from datetime import datetime

from xiangqi_rules import get_possible_moves

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
    image_filename = draw_board_image(board)  # 生成新圖片並獲取文件名
    update_readme("新對局開始", board["turn"], image_filename)  # 傳入圖片文件名
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

def update_readme(move, turn, image_filename):
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    if "✅ 最新一步：" in content:
        content = content.rsplit("✅ 最新一步：", 1)[0].strip()

    chinese_turn = "紅" if turn == "red" else "黑"

    # 獲取當前棋盤狀態
    board = load_board()

    # 生成移動建議表格
    moves_table = "## ♟️ 可行動的棋子\n\n"
    moves_table += "| 棋子 | 位置 | 可移動位置 (點擊連結直接移動) |\n"
    moves_table += "|------|------|-----------------------------|\n"

    # 棋子類型對應的中文名稱
    piece_names = {
        "king": "將/帥",
        "mandarin": "士",
        "elephant": "相/象",
        "knight": "馬",
        "rook": "車",
        "cannon": "炮",
        "pawn": "兵/卒"
    }

    # 按棋子類型分組
    moves_by_piece = {}
    for pos, piece in board["board"].items():
        if piece.startswith(turn):
            piece_type = piece.split('_')[1]
            possible_moves = get_possible_moves(board, pos)
            if possible_moves:
                if piece_type not in moves_by_piece:
                    moves_by_piece[piece_type] = []
                moves_by_piece[piece_type].append((pos, possible_moves))

    # 按指定順序顯示棋子
    display_order = ["king", "mandarin", "elephant", "knight", "rook", "cannon", "pawn"]

    for piece_type in display_order:
        if piece_type in moves_by_piece:
            for pos, moves in moves_by_piece[piece_type]:
                # 創建所有移動連結
                move_links = []
                for target in moves:
                    raw_title = f"xiangqi|move|{pos}-{target}|game001"
                    encoded_title = raw_title.replace("|", "%7C")
                    issue_link = f"https://github.com/{REPO_NAME}/issues/new?title={encoded_title}&body=請勿修改標題，直接提交即可"
                    move_links.append(f"[{target}]({issue_link})")

                moves_table += f"| {piece_names.get(piece_type, piece_type)} | {pos} | {' '.join(move_links)} |\n"

    # 加上隨機參數避免快取
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    image_url = f"https://raw.githubusercontent.com/Asriel0727/xiangqi-battle/main/images/board/{image_filename}?{timestamp}"

    new_section = f"""
![current board]({image_url})

✅ 最新一步：{move}  
🎯 現在輪到：**{chinese_turn}方**

{moves_table}

### 如何移動？
1. 點擊表格中的位置連結 (如 `a2-a3`)
2. 系統會自動建立包含移動指令的 Issue
3. 直接提交該 Issue 即可完成移動
"""

    content = content.split("## ⚫️ 當前棋盤")[0] + f"## ⚫️ 當前棋盤\n\n{new_section}"

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ README.md 已更新，目前輪到：", turn)


def save_board(data):
    os.makedirs("data", exist_ok=True)
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ 棋盤資料已儲存到 {BOARD_FILE}")

def draw_board_image(board_data):
    # 確保 board 目錄存在
    board_dir = "images/board"
    os.makedirs(board_dir, exist_ok=True)

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

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    new_image_name = f"board_{timestamp}.png"
    new_image_path = os.path.join(board_dir, new_image_name)
    img.save(new_image_path)
    print(f"✅ 棋盤圖片已儲存為 {new_image_path}")

    # 同步為最新棋盤
    img.save(BOARD_IMAGE)

    # 刪除舊的棋盤圖片（保留最新的一張）
    if os.path.exists(board_dir):
        board_files = [f for f in os.listdir(board_dir) 
                      if f.startswith("board_") and f.endswith(".png")]
        board_files.sort()
        print(f"找到的棋盤圖片: {board_files}")
        
        # 保留最新的檔案，刪除其他
        for old_file in board_files[:-1]:
            try:
                os.remove(os.path.join(board_dir, old_file))
                print(f"🗑️ 已刪除舊棋盤圖片: {old_file}")
            except Exception as e:
                print(f"⚠️ 無法刪除 {old_file}: {e}")

    return new_image_name


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

        # 基本格式檢查
        if '-' not in move:
            post_comment(repo, ISSUE_NUMBER, "⚠️ 移動指令格式錯誤，應為「起始位置-目標位置」(如 a2-a3)")
            return

        src, dst = move.split('-')
        piece = board["board"].get(src)
        
        # 檢查是否存在棋子
        if not piece:
            post_comment(repo, ISSUE_NUMBER, f"⚠️ 沒有找到 {src} 的棋子，無法移動")
            return
            
        # 檢查是否輪到該玩家
        piece_color = piece.split('_')[0]
        if piece_color != board["turn"]:
            post_comment(repo, ISSUE_NUMBER, f"⚠️ 現在輪到 {board['turn']} 方，不能移動 {piece_color} 方的棋子")
            return
            
        # 檢查移動是否合法
        possible_moves = get_possible_moves(board, src)
        if dst not in possible_moves:
            post_comment(repo, ISSUE_NUMBER, f"⚠️ 非法移動！{piece} 不能從 {src} 移動到 {dst}")
            return

        # 執行移動
        if "history" not in board:
            board["history"] = []
        board["history"].append(move)
        
        board["board"].pop(src)
        board["board"][dst] = piece
        board["turn"] = "black" if board["turn"] == "red" else "red"

        save_board(board)
        image_filename = draw_board_image(board)
        update_readme(move, board["turn"], image_filename)
        post_comment(repo, ISSUE_NUMBER, f"✅ 移動 {move} 已執行，現在輪到 **{board['turn']}** 方")
        return

    print("⚠️ 不支援的指令類型")

if __name__ == "__main__":
    main()