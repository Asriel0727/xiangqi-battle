def get_piece_type(piece_name):
    """從棋子名稱中提取類型（去掉顏色前綴）"""
    return piece_name.split('_')[1] if '_' in piece_name else piece_name

def is_valid_position(col, row):
    """檢查位置是否在棋盤範圍內"""
    return 'a' <= col <= 'i' and 1 <= row <= 10

def is_in_palace(col, row, color):
    """檢查位置是否在九宮內"""
    if not ('d' <= col <= 'f'):
        return False
    if color == "red" and not (1 <= row <= 3):
        return False
    if color == "black" and not (8 <= row <= 10):
        return False
    return True

def get_rook_moves(board, pos, color):
    """車的移動規則（直線任意格，不能跳過其他棋子）"""
    col, row = pos[0], int(pos[1:])
    moves = []
    
    # 四個方向的移動
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    for dc, dr in directions:
        for step in range(1, 10):
            new_col = chr(ord(col) + dc * step)
            new_row = row + dr * step
            if not is_valid_position(new_col, new_row):
                break
                
            new_pos = f"{new_col}{new_row}"
            target_piece = board.get(new_pos)
            
            if not target_piece:
                moves.append(new_pos)
            else:
                if not target_piece.startswith(color):
                    moves.append(new_pos)  # 可以吃對方棋子
                break  # 遇到任何棋子都停止這個方向的搜索
    
    return moves

def get_knight_moves(board, pos, color):
    """馬的移動規則（日字，考慮蹩馬腿）"""
    col, row = pos[0], int(pos[1:])
    moves = []
    
    # 八個可能的移動方向
    knight_moves = [
        (1, 2), (2, 1), (-1, 2), (-2, 1),
        (1, -2), (2, -1), (-1, -2), (-2, -1)
    ]
    
    for dc, dr in knight_moves:
        new_col = chr(ord(col) + dc)
        new_row = row + dr
        
        if not is_valid_position(new_col, new_row):
            continue
        
        # 檢查是否蹩馬腿
        if abs(dc) == 2:  # 橫向移動兩格
            block_col = chr(ord(col) + (1 if dc > 0 else -1))
            block_pos = f"{block_col}{row}"
        else:  # 縱向移動兩格
            block_row = row + (1 if dr > 0 else -1)
            block_pos = f"{col}{block_row}"
        
        if block_pos in board:  # 馬腿被擋住
            continue
            
        new_pos = f"{new_col}{new_row}"
        target_piece = board.get(new_pos)
        
        if not target_piece or not target_piece.startswith(color):
            moves.append(new_pos)
    
    return moves

def get_elephant_moves(board, pos, color):
    """象的移動規則（田字，不能過河，象眼不被塞）"""
    col, row = pos[0], int(pos[1:])
    moves = []
    
    # 四個可能的移動方向
    elephant_moves = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
    
    for dc, dr in elephant_moves:
        new_col = chr(ord(col) + dc)
        new_row = row + dr
        
        if not is_valid_position(new_col, new_row):
            continue
        
        # 檢查是否過河
        if (color == "red" and new_row > 5) or (color == "black" and new_row < 6):
            continue
            
        # 檢查象眼是否被塞
        block_col = chr(ord(col) + (dc // 2))
        block_row = row + (dr // 2)
        block_pos = f"{block_col}{block_row}"
        
        if block_pos in board:
            continue
            
        new_pos = f"{new_col}{new_row}"
        target_piece = board.get(new_pos)
        
        if not target_piece or not target_piece.startswith(color):
            moves.append(new_pos)
    
    return moves

def get_mandarin_moves(board, pos, color):
    """士的移動規則（斜線一格，不能出九宮）"""
    col, row = pos[0], int(pos[1:])
    moves = []
    
    # 四個可能的移動方向
    mandarin_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for dc, dr in mandarin_moves:
        new_col = chr(ord(col) + dc)
        new_row = row + dr
        
        if not is_in_palace(new_col, new_row, color):
            continue
            
        new_pos = f"{new_col}{new_row}"
        target_piece = board.get(new_pos)
        
        if not target_piece or not target_piece.startswith(color):
            moves.append(new_pos)
    
    return moves

def get_king_moves(board, pos, color):
    """將/帥的移動規則（直線一格，不能出九宮，不能對臉）"""
    col, row = pos[0], int(pos[1:])
    moves = []
    
    # 四個可能的移動方向
    king_moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    for dc, dr in king_moves:
        new_col = chr(ord(col) + dc)
        new_row = row + dr
        
        if not is_in_palace(new_col, new_row, color):
            continue
            
        new_pos = f"{new_col}{new_row}"
        target_piece = board.get(new_pos)
        
        if not target_piece or not target_piece.startswith(color):
            moves.append(new_pos)
    
    # 檢查將帥對臉的特殊規則
    if color == "red":
        opponent_color = "black"
        opponent_king_row = 10
    else:
        opponent_color = "red"
        opponent_king_row = 1
    
    king_col = pos[0]
    # 檢查同一列是否有對方的將/帥
    same_col = True
    for r in range(min(row, opponent_king_row) + 1, max(row, opponent_king_row)):
        if f"{king_col}{r}" in board:
            same_col = False
            break
    
    if same_col:
        opponent_king_pos = f"{king_col}{opponent_king_row}"
        if board.get(opponent_king_pos) == f"{opponent_color}_king":
            moves.append(opponent_king_pos)
    
    return moves

def get_cannon_moves(board, pos, color):
    """炮的移動規則（直線任意格，吃子需隔一子）"""
    col, row = pos[0], int(pos[1:])
    moves = []
    
    # 四個方向的移動
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    for dc, dr in directions:
        found_piece = False  # 是否已經遇到一個棋子
        
        for step in range(1, 10):
            new_col = chr(ord(col) + dc * step)
            new_row = row + dr * step
            if not is_valid_position(new_col, new_row):
                break
                
            new_pos = f"{new_col}{new_row}"
            target_piece = board.get(new_pos)
            
            if not found_piece:
                if not target_piece:
                    moves.append(new_pos)
                else:
                    found_piece = True  # 遇到第一個棋子
            else:
                if target_piece:
                    if not target_piece.startswith(color):
                        moves.append(new_pos)  # 可以吃對方的棋子
                    break  # 無論是否吃子，都停止這個方向的搜索
    
    return moves

def get_pawn_moves(board, pos, color):
    """兵的移動規則（過河前只能前進，過河後可左右移動）"""
    col, row = pos[0], int(pos[1:])
    moves = []
    
    if color == "red":
        # 紅兵向前（增加行號）
        forward = 1
        river_row = 5  # 紅方過河是第6行及以上
    else:
        # 黑兵向前（減少行號）
        forward = -1
        river_row = 6  # 黑方過河是第5行及以下
    
    # 前進
    new_row = row + forward
    if 1 <= new_row <= 10:
        new_pos = f"{col}{new_row}"
        target_piece = board.get(new_pos)
        if not target_piece or not target_piece.startswith(color):
            moves.append(new_pos)
    
    # 過河後可以左右移動
    if (color == "red" and row > river_row) or (color == "black" and row < river_row):
        for dc in [-1, 1]:
            new_col = chr(ord(col) + dc)
            if 'a' <= new_col <= 'i':
                new_pos = f"{new_col}{row}"
                target_piece = board.get(new_pos)
                if not target_piece or not target_piece.startswith(color):
                    moves.append(new_pos)
    
    return moves

def get_possible_moves(board_data, pos):
    """獲取指定位置棋子的所有合法移動"""
    board = board_data["board"]
    piece = board.get(pos)
    if not piece:
        return []
    
    color, piece_type = piece.split('_')
    
    if piece_type == "rook":
        return get_rook_moves(board, pos, color)
    elif piece_type == "knight":
        return get_knight_moves(board, pos, color)
    elif piece_type == "elephant":
        return get_elephant_moves(board, pos, color)
    elif piece_type == "mandarin":
        return get_mandarin_moves(board, pos, color)
    elif piece_type == "king":
        return get_king_moves(board, pos, color)
    elif piece_type == "cannon":
        return get_cannon_moves(board, pos, color)
    elif piece_type == "pawn":
        return get_pawn_moves(board, pos, color)
    
    return []  # 未知棋子類型

def check_game_result(board_data):
    """檢查遊戲是否結束（將/帥被吃）"""
    board = board_data["board"]
    red_king_exists = any(piece == "red_king" for piece in board.values())
    black_king_exists = any(piece == "black_king" for piece in board.values())
    
    if not red_king_exists:
        return "black"  # 黑方勝
    if not black_king_exists:
        return "red"    # 紅方勝
    return None         # 遊戲繼續