import os
import json
from datetime import datetime
from xiangqi_rules import get_possible_moves

def load_board(board_file):
    """從檔案載入棋盤狀態"""
    if not os.path.exists(board_file):
        print("找不到 board.json，初始化空棋盤")
        return {"turn": "red", "board": {}, "history": []}
    
    with open(board_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"從 {board_file} 載入棋盤資料")

    # 確保基本欄位存在
    if "board" not in data:
        data["board"] = {}
    if "turn" not in data:
        data["turn"] = "red"
    if "history" not in data:
        data["history"] = []

    return data

def get_chinese_piece_name(color, piece_type):
    if piece_type == "king":
        return "帥" if color == "red" else "將"
    elif piece_type == "mandarin":
        return "仕" if color == "red" else "士"
    elif piece_type == "elephant":
        return "相" if color == "red" else "象"
    elif piece_type == "pawn":
        return "兵" if color == "red" else "卒"
    elif piece_type == "cannon":
        return "炮"
    elif piece_type == "rook":
        return "車"
    elif piece_type == "knight":
        return "馬"
    else:
        return "？"

def generate_moves_table(board, turn, repo_name):
    """生成移動建議表格"""
    moves_table = "## ♟️ 可行動的棋子\n\n"
    moves_table += "| 棋子 | 位置 | 可移動位置 (點擊連結直接移動) |\n"
    moves_table += "|------|------|-----------------------------|\n"
    
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
                    issue_link = f"https://github.com/{repo_name}/issues/new?title={encoded_title}&body=請勿修改標題,直接提交即可"
                    move_links.append(f"[{target}]({issue_link})")

                chinese_name = get_chinese_piece_name(turn, piece_type)
                moves_table += f"| {chinese_name} | {pos} | {'、'.join(move_links)} |\n"
    
    return moves_table

def update_readme(move, turn, image_filename, repo_name, readme_file, board_file):
    """更新 README 檔案內容"""
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if "✅ 最新一步：" in content:
        content = content.rsplit("✅ 最新一步：", 1)[0].strip()

    board = load_board(board_file)
    
    # 判斷是否有勝負（turn為None表示遊戲結束）
    game_ended = turn is None
    
    # 生成歷史紀錄部分
    history_section = ""
    if game_ended:
        # 遊戲結束時顯示完整歷史
        history_section = "### 📜 完整移動歷史：\n\n"
        for i, item in enumerate(board.get("history", []), 1):
            if isinstance(item, dict) and "turn" in item and "move" in item:
                side = "紅" if item["turn"] == "red" else "黑"
                user = item.get("user", "未知")
                history_section += f"{i}. {side}方 ({user})：{item['move']}\n"
            else:
                history_section += f"{i}. ❓ 資料格式錯誤：{item}\n"
    else:
        # 遊戲進行中只顯示最近5步
        recent_moves = board.get("history", [])[-5:]
        history_section = "### 📜 最近五步：\n\n"
        for i, item in enumerate(recent_moves[::-1], 1):
            if isinstance(item, dict) and "turn" in item and "move" in item:
                side = "紅" if item["turn"] == "red" else "黑"
                user = item.get("user", "未知")
                history_section += f"{i}. {side}方 ({user})：{item['move']}\n"
            else:
                history_section += f"{i}. ❓ 資料格式錯誤：{item}\n"

    # 加上隨機參數避免快取
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    image_url = f"https://raw.githubusercontent.com/{repo_name}/main/images/board/{image_filename}?{timestamp}"
    reset_url = f"https://github.com/{repo_name}/issues/new?title=xiangqi|chess|new|game001&body=請勿修改標題,直接提交即可"

    if game_ended:
        # 遊戲結束時的顯示
        winner = "紅" if "紅方勝" in move else "黑"
        new_section = f"""
🎉 遊戲結束！{winner}方獲勝！

✅ 最後一步：{move}  
![current board]({image_url})  

{history_section}  

👉 [開始新對局]({reset_url})
"""
    else:
        # 遊戲進行中的顯示
        chinese_turn = "紅" if turn == "red" else "黑"
        moves_table = generate_moves_table(board, turn, repo_name)
        new_section = f"""
✅ 最新一步：{move}  
🎯 現在輪到：**{chinese_turn}方**  
![current board]({image_url})  

{moves_table}  

{history_section}  

👉 [重開一局]({reset_url})
"""

    content = content.split("## ⚫️ 當前棋盤")[0] + f"## ⚫️ 當前棋盤\n\n{new_section}"

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("README.md 已更新", "，遊戲已結束" if game_ended else f"，目前輪到：{turn}")
