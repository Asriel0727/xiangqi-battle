import os
import json
from github import Github

ISSUE_TITLE = os.environ.get("ISSUE_TITLE")
ISSUE_NUMBER = int(os.environ.get("ISSUE_NUMBER"))
TOKEN = os.environ.get("GITHUB_TOKEN")

REPO_NAME = "Asriel0727/xiangqi-battle"
BOARD_FILE = "data/board.json"
README_FILE = "README.md"

def parse_move(issue_title):
    # ex: xiangqi|move|b2-b3|game001
    try:
        _, _, move, game_id = issue_title.strip().split('|')
        return move.strip(), game_id.strip()
    except:
        return None, None

def load_board():
    if not os.path.exists(BOARD_FILE):
        return {"turn": "red", "board": []}
    with open(BOARD_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_board(data):
    os.makedirs("data", exist_ok=True)
    with open(BOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_readme(move):
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    content += f"\n\n✅ 最新一步：{move}"
    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def post_comment(repo, issue_num, body):
    issue = repo.get_issue(number=issue_num)
    issue.create_comment(body)
    issue.edit(state="closed")

def main():
    move, game_id = parse_move(ISSUE_TITLE)
    if not move:
        print("Invalid move format.")
        return

    g = Github(TOKEN)
    repo = g.get_repo(REPO_NAME)

    # 模擬棋局處理：未驗證規則，只更新記錄
    board = load_board()
    if "history" not in board:
        board["history"] = []
    board["history"].append(move)
    save_board(board)
    update_readme(move)

    post_comment(repo, ISSUE_NUMBER, f"✅ 步驟 {move} 已紀錄（未驗證合法性）。")

if __name__ == "__main__":
    main()
