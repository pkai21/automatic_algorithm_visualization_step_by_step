# export_input_config_bianchini.py

def get_nfa_config(Q, sigma, sigma_labels, F, delta):
    """
    Hàm này nhận dữ liệu đã qua xử lý (cấu trúc dữ liệu nội bộ),
    thực hiện logic ngược và TRẢ VỀ dữ liệu thô ban đầu (states, final_states, alphabet, transitions).
    """
    
    # 1. Reverse normalize: Thực tế là identity vì normalize chỉ sort, 
    # nhưng ta giữ đúng flow ngược lại của set_nfa_config
    delta_raw = re_normalize_delta(delta)
    
    # 2. Reverse delta table to tuples
    # Input của convert_to_2d_array là (transitions, Q, sigma), Output là delta
    # Nên Input của re_ là delta, Output là transitions (Q và sigma được suy ra từ kích thước mảng nhưng ở đây ta chỉ cần transitions)
    transitions = re_convert_to_2d_array(delta_raw)
    
    # 3. Reverse F (one-hot) to list of indices
    final_states = re_convert_F(F)
    
    # 4. Reverse sigma indices/labels to alphabet list
    alphabet = re_convert_sigma(sigma, sigma_labels)
    
    # States Q giữ nguyên
    states = Q

    # Trả về các tham số đầu vào gốc
    return states, final_states, alphabet, transitions

# --- Các hàm hỗ trợ (re_) ---

def re_convert_to_2d_array(result):
    """
    Ngược lại của convert_to_2d_array.
    Input: result (mảng 2 chiều delta[state][symbol_idx] = [next_states...])
    Output: delta_tuple (list các tuple (curr, next, sym))
    """
    delta_tuple = []
    # Duyệt qua từng dòng (curr state)
    for curr, row in enumerate(result):
        # Duyệt qua từng cột (symbol index)
        for sym, next_states in enumerate(row):
            # Với mỗi state tiếp theo trong danh sách
            for next_state in next_states:
                # Tạo lại tuple gốc: (curr, next, sym)
                # Lưu ý: convert_to_2d_array gốc dùng sym ở vị trí index 2
                delta_tuple.append((curr, next_state, sym))
    return delta_tuple

def re_normalize_delta(delta):
    """
    Ngược lại của normalize_delta.
    Input: delta (đã sorted)
    Output: delta_raw
    Vì normalize chỉ sort list con, nên cấu trúc không đổi, ta trả về chính nó.
    """
    return delta

def re_convert_F(F_res):
    """
    Ngược lại của convert_F.
    Input: F_res (mảng 0/1 độ dài bằng Q)
    Output: F_val (danh sách các index có giá trị 1)
    """
    F_val = []
    for i, val in enumerate(F_res):
        if val == 1:
            F_val.append(i)
    return F_val

def re_convert_sigma(sigma, sigma_labels):
    """
    Ngược lại của convert_sigma.
    Input: sigma (list index), sigma_labels (dict {index: char})
    Output: alphabet (list các char gốc)
    """
    # Vì sigma_labels lưu {index: 'a', index: 'b'}, ta cần sort theo index (sigma) để lấy lại thứ tự alphabet gốc
    alphabet = []
    # Sắp xếp sigma để đảm bảo thứ tự đúng như lúc sinh ra (range)
    sorted_sigma = sorted(sigma)
    
    for idx in sorted_sigma:
        if idx in sigma_labels:
            alphabet.append(sigma_labels[idx])
            
    return alphabet