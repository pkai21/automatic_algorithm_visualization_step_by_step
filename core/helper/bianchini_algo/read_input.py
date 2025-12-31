# core/helper/bianchini_algo/read_input_compare.py
import os
from core.helper.input_config_bianchini import set_nfa_config

def list_nfa_files_in_folder(folder_path=".", file_extension=".txt"):
    """
    Chỉ liệt kê các file input trong folder (không đọc nội dung).
    
    Args:
        folder_path (str): Đường dẫn đến folder chứa file (mặc định thư mục hiện tại)
        file_extension (str): Đuôi file cần lấy (mặc định .txt)
    
    Returns:
        list of str: Danh sách tên file (chỉ tên file, không kèm đường dẫn)
        và list of str: Danh sách đường dẫn đầy đủ đến file
    """
    if not os.path.isdir(folder_path):
        # Nếu thư mục không tồn tại, tạo mới để tránh lỗi
        try:
            os.makedirs(folder_path)
            print(f"Đã tạo thư mục mới: {folder_path}")
        except OSError:
            raise NotADirectoryError(f"Không tìm thấy thư mục: {folder_path}")

    file_names = []
    file_paths = []

    try:
        for filename in sorted(os.listdir(folder_path)):
            if filename.lower().endswith(file_extension.lower()):
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    file_names.append(filename)
                    file_paths.append(filepath)
    except Exception as e:
        print(f"Lỗi khi liệt kê file: {e}")

    if not file_names:
        print(f"Không tìm thấy file nào có đuôi {file_extension} trong thư mục.")

    return file_names, file_paths

def read_nfa_from_file(filepath):
    """
    Đọc nhiều NFA từ một file.
    - Hỗ trợ đọc block rỗng (nhiều dòng trống liên tiếp) để tạo NFA rỗng ở vị trí tương ứng.
    - Tự động điền đầy đủ 4 slot nếu file thiếu dữ liệu.
    
    Trả về: list of (Q, sigma, F, delta, name)
    """
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        # splitlines() giúp xử lý ký tự xuống dòng tốt hơn trên các hệ điều hành khác nhau
        lines = [line.strip() for line in f.read().splitlines()]

    blocks = []
    current_block = []
    
    # --- Logic chia block (Giữ lại các block rỗng) ---
    for line in lines:
        if line:
            current_block.append(line)
        else:
            # Gặp dòng trống -> Kết thúc block hiện tại
            # Kể cả block rỗng (do 2 dòng trống liên tiếp) cũng được append
            blocks.append(current_block)
            current_block = []
    
    # Thêm block cuối cùng (nếu file không kết thúc bằng dòng trống)
    blocks.append(current_block)

    # Loại bỏ các block rỗng dư thừa ở CỐI file (tránh tạo slot rỗng vô nghĩa sau cùng)
    # Nhưng giữ lại các block rỗng nằm giữa các block dữ liệu
    while blocks and not blocks[-1]:
        blocks.pop()

    nfa_list = []
    max_slots = 4 # Giới hạn xử lý tối đa 4 slot

    # --- Xử lý từng block ---
    for i, block in enumerate(blocks):
        if i >= max_slots: 
            break # Chỉ lấy tối đa 4 NFA đầu tiên

        # TRƯỜNG HỢP 1: Block rỗng (Empty Slot)
        if not block:
            print(f"-> Vị trí {i+1} trong file là khoảng trống (Empty Slot).")
            empty_Q = []
            empty_sigma = []
            empty_sigma_labels = {}
            empty_F = []
            empty_delta = {} 
            nfa_list.append((empty_Q, empty_sigma, empty_sigma_labels, empty_F, empty_delta, f"{filename} (Empty Slot {i + 1})"))
            continue # Chuyển sang block tiếp theo
        
        # TRƯỜNG HỢP 2: Block có dữ liệu -> Parse NFA
        if len(block) < 4:
            print(f"Cảnh báo: Khối NFA {i+1} không đủ dữ liệu chuẩn, tạo slot lỗi/rỗng.")
            nfa_list.append(([], [], {}, [], {}, f"{filename} (Error Slot {i+1})"))
            continue 

        try:
            idx = 0
            # 1. Số trạng thái
            n_states = int(block[idx])
            idx += 1

            # 2. Bảng chữ cái Sigma
            sigma_parts = block[idx].split()
            try:
                sigma = [int(x) for x in sigma_parts]
            except:
                sigma = [str(x.strip("'\"")) for x in sigma_parts]
            idx += 1

            # 3. Trạng thái kết thúc F
            F = [int(x) for x in block[idx].split()]
            idx += 1

            # 4. Hàm chuyển Delta
            delta_tuple = []
            for line in block[idx:]:
                parts = line.split()
                if len(parts) != 3:
                    continue
                try:
                    fr, to, sym = int(parts[0]), int(parts[1]), int(parts[2])
                    delta_tuple.append((fr, to, sym))
                except:
                    pass

            # Xử lý tập Q
            Q = list(range(n_states))
            
            # Tự động mở rộng Q nếu delta chứa trạng thái lớn hơn khai báo
            all_states = {fr for fr, _, _ in delta_tuple} | {to for _, to, _ in delta_tuple}
            max_state = max(all_states, default=0)
            if max_state >= n_states:
                Q = list(range(max_state + 1))

            # Tự động mở rộng Sigma nếu delta chứa ký tự lớn hơn khai báo (với sigma số)
            max_sym = max((sym for _, _, sym in delta_tuple), default=-1)
            if isinstance(max_sym, int) and max_sym >= len(sigma):
                 # Chỉ mở rộng nếu sigma đang dùng index số
                 # Nếu sigma là list string thì logic này cần cẩn trọng, ở đây giữ logic cũ của bạn
                 if all(isinstance(s, int) for s in sigma):
                    sigma = list(range(max_sym + 1))

            # Config lại dữ liệu chuẩn
            Q_result, sigma_result, sigma_labels_result, F_result, delta_result = set_nfa_config(Q, F, sigma, delta_tuple)
            
            print("="*60)
            print(f"ĐÃ ĐỌC XONG NFA {i+1} TỪ {filename}")
            print(f"Q : {Q_result}")
            print(f"Σ : {sigma_labels_result}")
            print(f"F : {F_result}")
            print(f"δ : {delta_result}")
            print("="*60)

            nfa_list.append((Q_result, sigma_result, sigma_labels_result, F_result, delta_result, filename))
        
        except Exception as e:
            print(f"Lỗi khi đọc block {i+1}: {e}")
            # Nếu lỗi, thêm slot rỗng để giữ vị trí, tránh làm lệch các slot sau
            nfa_list.append(([], [], {}, [], {}, f"{filename} (Error Slot {i+1})"))

    # --- TRƯỜNG HỢP 3: Lấp đầy các slot còn thiếu ở cuối ---
    # Nếu file chỉ chứa 1 NFA, vòng lặp trên xong thì len = 1.
    # Code dưới sẽ thêm slot 2, 3, 4.
    current_count = len(nfa_list)
    if current_count < max_slots:
        print(f"Thông báo: File {filename} chỉ có {current_count} block. Tự động điền đầy các slot còn lại ({current_count+1} -> {max_slots}).")
        for i in range(current_count, max_slots):
            nfa_list.append(([], [], {}, [], {}, f"{filename} (Empty Slot {i + 1})"))
            
    return nfa_list

def read_nfa_by_filename(filename, folder_path="."):
    """
    Tiện ích: Đọc tất cả NFA từ một file khi bạn chỉ biết tên file.
    """
    filepath = os.path.join(folder_path, filename)
    return read_nfa_from_file(filepath)