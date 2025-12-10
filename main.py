# Main.py - Hoàn toàn phù hợp với định dạng delta_tuple = (từ, đến, ký_tự)
import ast
import time
import core.helper.input_config_bianchini as input_config_bianchini
from core.src.bianchini_algo.algorithm_3 import MINIMIZENFA, newNFA
from core.visualization.visualization_bianchini_algo import visualize

def input_list(prompt, caster=int):
    while True:
        s = input(prompt).strip()
        if not s:
            return []
        try:
            return [caster(x) for x in ast.literal_eval(s)]
        except:
            print("Sai định dạng! Ví dụ: [0,1,2] hoặc ['a','b']")

def input_transitions(n_states, n_symbols):
    print("\n" + "="*60)
    print("NHẬP CHUYỂN TRẠNG THÁI (δ)")
    print("Định dạng: trạng_thái_hiện_tại  trạng_thái_đích  chỉ_số_ký_tự")
    print(f"→ Trạng thái: 0 đến {n_states-1}")
    print(f"→ Chỉ số ký tự: 0 đến {n_symbols-1} (tương ứng với sigma)")
    print("Ví dụ: 0 1 1    → từ trạng thái 0 → đến trạng thái 1 khi đọc ký tự sigma[1]")
    print("Gõ Enter (dòng trống) để kết thúc.\n")
    
    transitions = []
    while True:
        line = input("δ → ").strip()
        if line == "":
            break
        parts = line.split()
        if len(parts) != 3:
            print("Phải nhập đúng 3 số! Thử lại.")
            continue
        try:
            curr = int(parts[0])
            next_st = int(parts[1])
            sym = int(parts[2])
            
            if not (0 <= curr < n_states):
                print(f"Trạng thái hiện tại phải từ 0 đến {n_states-1}")
                continue
            if not (0 <= next_st < n_states):
                print(f"Trạng thái đích phải từ 0 đến {n_states-1}")
                continue
            if not (0 <= sym < n_symbols):
                print(f"Chỉ số ký tự phải từ 0 đến {n_symbols-1} (bạn có {n_symbols} ký tự)")
                continue
                
            transitions.append((curr, next_st, sym))  # đúng thứ tự bạn dùng!
        except ValueError:
            print("Phải nhập số nguyên!")
    
    return transitions

def main():
    print("=" * 70)
    print("     CHẠY THỬ MINIMIZE NFA - PHIÊN BẢN DÀNH RIÊNG CHO BẠN")
    print("     Delta tuple dạng: (từ, đến, ký_tự) ← đúng như code của bạn")
    print("=" * 70)

    # Nhập số trạng thái
    while True:
        try:
            n = int(input("\nSố trạng thái (|Q|): "))
            if n > 0: break
        except:
            pass
        print("Nhập số nguyên dương!")

    Q_states = list(range(n))

    # Nhập bảng chữ cái
    sigma_input = input_list("Nhập Σ (ví dụ [0,1]): ", str)
    if not sigma_input:
        sigma_input = [0, 1]  # mặc định có epsilon
        print("→ Để trống → dùng mặc định: [0, 1]")
    sigma = sigma_input

    # Nhập tập kết thúc
    F_val = input_list("Nhập tập trạng thái kết thúc F (ví dụ [2]): ")

    # Nhập delta theo đúng định dạng của bạn
    delta_tuple = input_transitions(n, len(sigma))

    if not delta_tuple:
        print("Không có chuyển trạng thái nào! Dừng chương trình.")
        return

    print("\n" + "─" * 70)
    print("NFA bạn vừa nhập:")
    print(f"Q  = {Q_states}")
    print(f"Σ  = {sigma}")
    print(f"F  = {F_val}")
    print(f"δ  = {delta_tuple}")
    print("─" * 70)

    # Thiết lập NFA
    input_config_bianchini.set_nfa_config(Q_states, F_val, sigma, delta_tuple)

    print("DEBUG: delta sau khi set:", input_config_bianchini.delta)  # THÊM DÒNG NÀY
    print("DEBUG: F sau khi set:", input_config_bianchini.F)
    print("DEBUG: Q sau khi set:", input_config_bianchini.Q)  # THÊM DÒNG NÀY
    print("DEBUG: sigma sau khi set:", input_config_bianchini.sigma)
    # Vẽ NFA gốc
    try:
        visualize(input_config_bianchini.F, input_config_bianchini.delta, input_config_bianchini.sigma, "Original_NFA")
        print("Đã vẽ: Original_NFA.png")
    except Exception as e:
        print(f"Không vẽ được đồ thị gốc: {e}")

    print("\nBắt đầu minimize NFA...\n")

    # Chạy 2 lần
    for use_algo5, title in [(0, "KHÔNG dùng Algorithm 5"), (1, "DÙNG Algorithm 5")]:
        print(f"→ {title}...", end=" ")
        try:
            start = time.time()
            minimized = MINIMIZENFA(use_algo5)
            elapsed = time.time() - start

            new_Q, new_F, new_delta = newNFA(minimized)
            suffix = "_without_Algo5" if use_algo5 == 0 else "_with_Algo5"
            visualize(new_F, new_delta, input_config_bianchini.sigma, f"Minimized_NFA{suffix}")

            print(f"HOÀN TẤT trong {elapsed:.6f}s → {len(new_Q)} trạng thái")
        except RecursionError:
            print("ĐỆ QUY QUÁ SÂU!")
        except Exception as e:
            print(f"LỖI: {e}")

    print("\nHOÀN TẤT! Kết quả đồ thị:")
    print("   • Original_NFA.png")
    print("   • Minimized_NFA_without_Algo5.png")
    print("   • Minimized_NFA_with_Algo5.png")

if __name__ == "__main__":
    main()