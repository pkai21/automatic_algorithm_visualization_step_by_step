# main.py - Đã được đơn giản hóa cực mạnh
import time
from core.helper.bianchini_algo.read_input import read_nfa_from_file
import core.helper.bianchini_algo.input_config_bianchini as input_config_bianchini
from core.src.bianchini_algo.algorithm_3 import MINIMIZENFA, newNFA
from core.visualization.visualization_bianchini_algo import visualize

def main():
    print("=" * 70)
    print("     MINIMIZE NFA - CHẾ ĐỘ ĐỌC TỪ FILE (test.txt)")
    print("     Delta tuple: (từ, đến, ký_tự) - đúng chuẩn của bạn")
    print("=" * 70)

    try:
        # ĐỌC TOÀN BỘ NFA TỪ FILE
        read_nfa_from_file("test.txt")  # hoặc để tham số khác: "my_nfa.txt"
    except Exception as e:
        print(f"LỖI ĐỌC FILE: {e}")
        return

    # Vẽ NFA gốc
    try:
        visualize(input_config_bianchini.F, input_config_bianchini.delta, input_config_bianchini.sigma, "Original_NFA")
        print("Đã vẽ: Original_NFA.png")
    except Exception as e:
        print(f"Không vẽ được NFA gốc: {e}")

    print("\nBắt đầu minimize NFA...\n")

    # Chạy 2 phiên bản
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

    print("\nHOÀN TẤT! Các file ảnh:")
    print("   • Original_NFA.png")
    print("   • Minimized_NFA_without_Algo5.png")
    print("   • Minimized_NFA_with_Algo5.png")

if __name__ == "__main__":
    main()