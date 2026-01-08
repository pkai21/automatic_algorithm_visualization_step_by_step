# ------------------------------------------------------------------------------
# Copyright (c) 2026 Phan_Van_Khai
# All rights reserved.
#
# This source code is the proprietary and confidential property of Phan_Van_Khai.
# Unauthorized copying, distribution, or modification of this file, 
# via any medium, is strictly prohibited.
# ------------------------------------------------------------------------------

import sys
import os
from core.helper.input_config_bianchini import set_nfa_config

def list_nfa_files_in_folder(folder_path=".", file_extension=".txt"):
    if not os.path.isdir(folder_path):
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
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.read().splitlines()]

    blocks = []
    current_block = []
    
    for line in lines:
        if line:
            current_block.append(line)
        else:
            blocks.append(current_block)
            current_block = []
    
    blocks.append(current_block)

    while blocks and not blocks[-1]:
        blocks.pop()

    nfa_list = []
    max_slots = 4

    for i, block in enumerate(blocks):
        if i >= max_slots: 
            break 

        if not block:
            print(f"-> Vị trí {i+1} trong file là khoảng trống (Empty Slot).")
            empty_Q = []
            empty_sigma = []
            empty_sigma_labels = {}
            empty_F = []
            empty_delta = {} 
            nfa_list.append((empty_Q, empty_sigma, empty_sigma_labels, empty_F, empty_delta, f"{filename} (Empty Slot {i + 1})"))
            continue 
        
        if len(block) < 4:
            print(f"Cảnh báo: Khối NFA {i+1} không đủ dữ liệu chuẩn, tạo slot lỗi/rỗng.")
            nfa_list.append(([], [], {}, [], {}, f"{filename} (Error Slot {i+1})"))
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
            if isinstance(max_sym, int) and max_sym >= len(sigma):
                 if all(isinstance(s, int) for s in sigma):
                    sigma = list(range(max_sym + 1))

            Q_result, sigma_result, sigma_labels_result, F_result, delta_result = set_nfa_config(Q, F, sigma, delta_tuple)

            nfa_list.append((Q_result, sigma_result, sigma_labels_result, F_result, delta_result, filename))
        
        except Exception as e:
            print(f"Lỗi khi đọc block {i+1}: {e}")
            nfa_list.append(([], [], {}, [], {}, f"{filename} (Error Slot {i+1})"))

    current_count = len(nfa_list)
    if current_count < max_slots:
        print(f"Thông báo: File {filename} chỉ có {current_count} block. Tự động điền đầy các slot còn lại ({current_count+1} -> {max_slots}).")
        for i in range(current_count, max_slots):
            nfa_list.append(([], [], {}, [], {}, f"{filename} (Empty Slot {i + 1})"))
            
    return nfa_list

def read_nfa_by_filename(filename, folder_path="."):
    filepath = os.path.join(folder_path, filename)
    return read_nfa_from_file(filepath)