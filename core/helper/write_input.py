import os
import re

def write_test_case(states, alphabet, final_states, transitions, 
                    states_mini, alphabet_mini, final_states_mini, transitions_mini):
    """
    Ghi file test case với tên tự động tăng (test1.txt, test2.txt...)
    trong thư mục NFA_test_case.
    """
    
    # 1. Tạo folder NFA_test_case nếu chưa tồn tại
    folder_name = "NFA_test_case"
    if not os.path.exists(folder_name):
        try:
            os.makedirs(folder_name)
        except OSError as e:
            print(f"Error creating directory: {e}")
            return None

    # 2. Logic tự động sinh tên file (test1, test2, ...)
    # Lấy danh sách file hiện có
    existing_files = os.listdir(folder_name)
    max_index = 0
    
    # Regex để bắt đúng định dạng 'test' + số + '.txt'
    pattern = re.compile(r'^test(\d+)\.txt$')

    for file_name in existing_files:
        match = pattern.match(file_name)
        if match:
            # Lấy phần số ra (group 1) và ép kiểu int
            number = int(match.group(1))
            if number > max_index:
                max_index = number
    
    # Tên file mới = số lớn nhất + 1
    new_filename = f"test{max_index + 1}.txt"
    file_path = os.path.join(folder_name, new_filename)

    # 3. Ghi file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # --- PHẦN 1: NFA GỐC ---
            
            # Dòng 1: Số lượng states
            f.write(f"{len(states)}\n")
            
            # Dòng 2: Alphabet
            f.write(" ".join(map(str, alphabet)) + "\n")
            
            # Dòng 3: Final states
            f.write(" ".join(map(str, final_states)) + "\n")
            
            # Transitions (Input là list tuple [(src, dest, sym), ...])
            # Ghi ra: src dest sym
            for t in transitions:
                f.write(" ".join(map(str, t)) + "\n")

            # --- NGĂN CÁCH ---
            f.write("\n")

            # --- PHẦN 2: MINI NFA ---
            
            # Dòng 1: Số lượng states mini
            f.write(f"{len(states_mini)}\n")
            
            # Dòng 2: Alphabet mini
            f.write(" ".join(map(str, alphabet_mini)) + "\n")
            
            # Dòng 3: Final states mini
            f.write(" ".join(map(str, final_states_mini)) + "\n")
            
            # Transitions mini
            for t in transitions_mini:
                f.write(" ".join(map(str, t)) + "\n")
                
        print(f"Successfully saved new test case: {new_filename}")
        return new_filename 
        
    except Exception as e:
        print(f"Failed to write file: {e}")
        return None