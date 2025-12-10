# core/helper/bianchini_algo/read_input.py
from collections import defaultdict
import os
from core.helper.bianchini_algo.input_config_bianchini import set_nfa_config

def read_nfa_from_file(filename="test.txt"):
    """
    Đọc NFA từ file có định dạng như bạn đã cho:
    Dòng 1: số trạng thái n
    Dòng 2: sigma (các ký tự, cách nhau space)
    Dòng 3: các trạng thái kết thúc F (cách nhau space)
    Các dòng tiếp: delta_tuple dạng: from to symbol
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Không tìm thấy file: {filename}")

    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) < 4:
        raise ValueError("File input phải có ít nhất 4 dòng!")

    idx = 0

    # Dòng 1: số trạng thái
    try:
        n_states = int(lines[idx])
        idx += 1
    except:
        raise ValueError("Dòng đầu tiên phải là số trạng thái (số nguyên)")

    # Dòng 2: sigma
    try:
        sigma = [int(x) for x in lines[idx].split()]
        idx += 1
    except:
        try:
            sigma = [str(x.strip("'\"")) for x in lines[idx].split()]
        except:
            raise ValueError("Dòng sigma không đúng định dạng")

    # Dòng 3: tập F
    try:
        F = [int(x) for x in lines[idx].split()]
        idx += 1
    except:
        raise ValueError("Dòng tập kết thúc F phải là các số nguyên cách nhau space")

    # Các dòng còn lại: delta_tuple
    delta_tuple = []
    for line in lines[idx:]:
        parts = line.split()
        if len(parts) != 3:
            print(f"Cảnh báo: bỏ qua dòng không đúng định dạng: {line}")
            continue
        try:
            fr, to, sym = int(parts[0]), int(parts[1]), int(parts[2])
            delta_tuple.append((fr, to, sym))
        except:
            print(f"Cảnh báo: bỏ qua dòng lỗi chuyển đổi số: {line}")

    # Tạo Q
    Q = list(range(n_states))

    # Kiểm tra tính hợp lệ cơ bản
    max_state = max(n_states - 1, max((fr for fr, _, _ in delta_tuple), default=0), max((to for _, to, _ in delta_tuple), default=0))
    if max_state >= n_states:
        print(f"Cảnh báo: có trạng thái >= {n_states}, sẽ tự mở rộng Q...")
        Q = list(range(max_state + 1))

    max_sym = max((sym for _, _, sym in delta_tuple), default=0)
    if max_sym >= len(sigma):
        print(f"Cảnh báo: chỉ số ký tự lớn hơn độ dài sigma → tự mở rộng sigma")
        sigma = list(range(max_sym + 1))  # hoặc giữ nguyên và cảnh báo

    print("="*60)
    print("ĐÃ ĐỌC XONG NFA TỪ FILE")
    print(f"Q     : {Q}")
    print(f"Σ     : {sigma}")
    print(f"F     : {F}")
    print(f"δ     : {delta_tuple} ({len(delta_tuple)} chuyển)")
    print("="*60)

    # Áp dụng config vào hệ thống
    set_nfa_config(Q, F, sigma, delta_tuple)

    return Q, F, sigma, delta_tuple