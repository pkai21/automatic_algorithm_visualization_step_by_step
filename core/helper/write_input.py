import os
import re

def write_test_case(states, alphabet, final_states, transitions, 
                    states_mini, alphabet_mini, final_states_mini, transitions_mini):
    
    folder_name = "NFA_test_case"
    if not os.path.exists(folder_name):
        try:
            os.makedirs(folder_name)
        except OSError as e:
            print(f"Error creating directory: {e}")
            return None

    existing_files = os.listdir(folder_name)
    max_index = 0
    
    pattern = re.compile(r'^test(\d+)\.txt$')

    for file_name in existing_files:
        match = pattern.match(file_name)
        if match:
            number = int(match.group(1))
            if number > max_index:
                max_index = number
    
    new_filename = f"test{max_index + 1}.txt"
    file_path = os.path.join(folder_name, new_filename)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{len(states)}\n")

            f.write(" ".join(map(str, alphabet)) + "\n")

            f.write(" ".join(map(str, final_states)) + "\n")

            for t in transitions:
                f.write(" ".join(map(str, t)) + "\n")

            f.write("\n")

            f.write(f"{len(states_mini)}\n")

            f.write(" ".join(map(str, alphabet_mini)) + "\n")

            f.write(" ".join(map(str, final_states_mini)) + "\n")

            for t in transitions_mini:
                f.write(" ".join(map(str, t)) + "\n")
                
        print(f"Successfully saved new test case: {new_filename}")
        return new_filename 
        
    except Exception as e:
        print(f"Failed to write file: {e}")
        return None