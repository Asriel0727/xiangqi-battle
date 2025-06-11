import os
import json
from github import Github
from PIL import Image, ImageDraw

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
        _, _, move, game_id = issue_title.strip().split('|')
        return move.strip(), game_id.strip()
    except:
        return None, None

def load_board():
    if not os.path.exists(BOARD_FILE):
        return {"turn": "red", "board": {}}
    with open(BOARD_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_board(data):
    os.makedirs("data", exist_ok=True)
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_readme(move):
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    if "✅ 最新一步：" in content:
        content = content.rsplit("✅ 最新一步：", 1)[0].strip()
    content += f"\n\n✅ 最新一步：{move}"
    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def post_comment(repo, issue_num, body):
    issue = repo.get_issue(number=issue_num)
    issue.create_comment(body)
    issue.edit(state="closed")

def pos_to_xy(pos):
    col = ord(pos[0].lower()) - ord('a')
    row = int(pos[1:]) - 1
    return col * CELL_SIZE, row * CELL_SIZE

def draw_board_image(board_data):
    os.makedirs("images", exist_ok=True)

    img = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    # 畫網格線
    for i in range(BOARD_WIDTH):
        x = i * CELL_SIZE + CELL_SIZE // 2
        draw.line([(x, CELL_SIZE // 2), (x, IMG_HEIGHT - CELL_SIZE // 2)], fill="black", width=1)
    for j in range(BOARD_HEIGHT):
        y = j * CELL_SIZE + CELL_SIZE // 2
        draw.line([(CELL_SIZE // 2, y), (IMG_WIDTH - CELL_SIZE // 2, y)], fill="black", width=1)

    # 畫棋子圖片
    for pos, piece in board_data.get("board", {}).items():
        x, y = pos_to_xy(pos)
        try:
            piece_path = os.path.join(PIECE_IMG_DIR, f"{piece}.png")
            piece_img = Image.open(piece_path).resize((CELL_SIZE, CELL_SIZE))
            img.paste(piece_img, (x, y), piece_img.convert("RGBA"))
        except Exception as e:
            print(f"⚠️ 無法載入 {piece}：{e}")

    img.save(BOARD_IMAGE)
    print("✅ 圖片儲存成功：", BOARD_IMAGE)

def main():
    move, game_id = parse_move(ISSUE_TITLE)
    if not move:
        print("Invalid move format.")
        return

    g = Github(TOKEN)
    repo = g.get_repo(REPO_NAME)

    board = load_board()
    if "history" not in board:
        board["history"] = []
    board["history"].append(move)

    # 簡單模擬移動（不檢查合法性）
    src, dst = move.split('-')
    piece = board["board"].pop(src, None)
    if piece:
        board["board"][dst] = piece

    save_board(board)
    draw_board_image(board)
    update_readme(move)
    post_comment(repo, ISSUE_NUMBER, f"✅ 步驟 {move} 已紀錄，棋盤已更新（未驗證合法性）。")

if __name__ == "__main__":
    main()
