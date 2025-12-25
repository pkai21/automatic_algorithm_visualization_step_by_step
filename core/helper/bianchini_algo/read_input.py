# core/helper/bianchini_algo/read_input.py
import os
from core.helper.bianchini_algo.input_config_bianchini import set_nfa_config

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
        raise NotADirectoryError(f"Không tìm thấy thư mục: {folder_path}")

    file_names = []
    file_paths = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(file_extension.lower()):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                file_names.append(filename)
                file_paths.append(filepath)

    if not file_names:
        print(f"Không tìm thấy file nào có đuôi {file_extension} trong thư mục.")

    return file_names, file_paths

def read_nfa_from_file(filepath):
    """
    Đọc nhiều NFA từ một file (các NFA cách nhau bằng dòng trắng).
    Trả về: list of (Q, F, sigma, delta_tuple)
    """
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    blocks = []
    current_block = []
    for line in lines:
        if line:
            current_block.append(line)
        else:
            if current_block:
                blocks.append(current_block)
                current_block = []
    if current_block:
        blocks.append(current_block)

    if not blocks:
        print(f"Cảnh báo: File {filename} không chứa dữ liệu NFA nào.")
        return []

    nfa_list = []
    for i, block in enumerate(blocks):
        if len(block) < 4:
            # Nếu block quá ngắn, có thể bỏ qua hoặc báo lỗi
            print(f"Cảnh báo: Khối NFA {i+1} không đủ dữ liệu, bỏ qua.")
            continue 

        try:
            idx = 0
            n_states = int(block[idx])
            idx += 1

            sigma_parts = block[idx].split()
            try:
                sigma = [int(x) for x in sigma_parts]
            except:
                sigma = [str(x.strip("'\"")) for x in sigma_parts]
            idx += 1

            F = [int(x) for x in block[idx].split()]
            idx += 1

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

            Q = list(range(n_states))
            all_states = {fr for fr, _, _ in delta_tuple} | {to for _, to, _ in delta_tuple}
            max_state = max(all_states, default=0)
            if max_state >= n_states:
                Q = list(range(max_state + 1))

            max_sym = max((sym for _, _, sym in delta_tuple), default=-1)
            if max_sym >= len(sigma):
                sigma = list(range(max_sym + 1))

            Q_result, sigma_result, F_result, delta_result = set_nfa_config(Q, F, sigma, delta_tuple)
            
            # Print log 
            print("="*60)
            print(f"ĐÃ ĐỌC XONG NFA {i+1} TỪ {filename}")
            print(f"Q : {Q_result}")
            print(f"Σ : {sigma_result}")
            print(f"F : {F_result}")
            print(f"δ : {delta_result}")
            print("="*60)

            nfa_list.append((Q_result, sigma_result, F_result, delta_result, filename))
        except Exception as e:
            print(f"Lỗi khi đọc block {i+1}: {e}")

    # Kiểm tra nếu chỉ có đúng 1 NFA được đọc thành công
    if len(nfa_list) == 1:
        print(f"Thông báo: File {filename} chỉ chứa 1 NFA. Tự động tạo NFA rỗng cho vị trí thứ 2.")
        
        # Tạo dữ liệu rỗng để GUI không bị lỗi index
        empty_Q = []
        empty_sigma = []
        empty_F = []
        empty_delta = {} 
        
        nfa_list.append((empty_Q, empty_sigma, empty_F, empty_delta, f"{filename} (Empty)"))
    # ------------------------------

    return nfa_list

# Hàm tiện ích: đọc NFA từ tên file (khi đã có danh sách file)
def read_nfa_by_filename(filename, folder_path="."):
    """
    Tiện ích: Đọc tất cả NFA từ một file khi bạn chỉ biết tên file.
    """
    filepath = os.path.join(folder_path, filename)
    return read_nfa_from_file(filepath)