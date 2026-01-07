import collections
import itertools

# ==============================================================================
# PHẦN 1: CẤU TRÚC DỮ LIỆU NFA VÀ CÁC THUẬT TOÁN CƠ BẢN (Helper)
# ==============================================================================

class NFA:
    def __init__(self, states=None, start_states=None, accept_states=None):
        self.states = set(states) if states else set()
        self.start_states = set(start_states) if start_states else set()
        self.accept_states = set(accept_states) if accept_states else set()
        # Transitions: {state: {char: {set of next states}}}
        self.transitions = collections.defaultdict(lambda: collections.defaultdict(set))
        self.alphabet = set()

    def add_transition(self, from_state, char, to_state):
        self.states.add(from_state)
        self.states.add(to_state)
        self.alphabet.add(char)
        self.transitions[from_state][char].add(to_state)

    def determinize(self):
        """Chuyển đổi NFA sang DFA (Subset Construction)"""
        if not self.start_states:
            return NFA()

        # Trạng thái DFA là frozenset của các trạng thái NFA
        start_set = frozenset(self.start_states)
        
        dfa_states = {start_set}
        dfa_transitions = collections.defaultdict(lambda: collections.defaultdict(set))
        queue = [start_set]
        processed = set()

        while queue:
            current_subset = queue.pop(0)
            if current_subset in processed:
                continue
            processed.add(current_subset)

            for char in self.alphabet:
                next_subset_set = set()
                for state in current_subset:
                    if state in self.transitions and char in self.transitions[state]:
                        next_subset_set.update(self.transitions[state][char])
                
                if next_subset_set:
                    next_subset = frozenset(next_subset_set)
                    dfa_transitions[current_subset][char].add(next_subset)
                    if next_subset not in dfa_states:
                        dfa_states.add(next_subset)
                        queue.append(next_subset)

        # Xây dựng đối tượng NFA kết quả (thực chất là DFA)
        result = NFA()
        result.alphabet = self.alphabet
        result.states = dfa_states
        result.start_states = {start_set}
        
        for subset in dfa_states:
            # Nếu subset chứa bất kỳ accept state nào của NFA gốc, nó là accept state
            if not subset.isdisjoint(self.accept_states):
                result.accept_states.add(subset)
            
            if subset in dfa_transitions:
                for char, next_sets in dfa_transitions[subset].items():
                    for next_s in next_sets:
                        result.add_transition(subset, char, next_s)
        
        return result

    def reverse(self):
        """Tạo NFA đảo ngược (Dual)"""
        result = NFA()
        result.alphabet = self.alphabet
        result.states = self.states.copy()
        
        # Đảo: Start -> Accept, Accept -> Start
        result.start_states = self.accept_states.copy()
        result.accept_states = self.start_states.copy()

        # Đảo chiều mũi tên
        for src, trans in self.transitions.items():
            for char, dests in trans.items():
                for dst in dests:
                    result.add_transition(dst, char, src)
        
        return result

    def __repr__(self):
        return f"NFA(States={len(self.states)}, Start={len(self.start_states)}, Accept={len(self.accept_states)})"

# ==============================================================================
# PHẦN 2: THUẬT TOÁN KAMEDA-WEINER (Core Logic)
# ==============================================================================

class Grid:
    """Đại diện cho một hình chữ nhật trong ma trận RAM"""
    def __init__(self, rows, cols):
        self.rows = frozenset(rows) # Tập hợp chỉ số dòng
        self.cols = frozenset(cols) # Tập hợp chỉ số cột

    def __eq__(self, other):
        return self.rows == other.rows and self.cols == other.cols

    def __hash__(self):
        return hash((self.rows, self.cols))
    
    def __repr__(self):
        return f"Grid(R={list(self.rows)}, C={list(self.cols)})"

class KamedaWeinerMinimizer:
    def __init__(self, nfa):
        self.nfa = nfa

    def run(self):
        """Hàm chính để thực thi thuật toán"""
        # 1. Tạo bản đồ trạng thái (State Map) từ DFA xuôi và DFA ngược
        # Input: NFA -> Output: Ma trận giao thoa
        matrix_data = self._make_state_map()
        if not matrix_data: 
            return NFA() # Trường hợp rỗng

        # 2. Giảm thiểu bản đồ trạng thái (State Map -> RAM)
        # Gộp các dòng/cột giống nhau
        ram_data = self._reduce_state_map(matrix_data)

        # 3. Tính toán các Grid nguyên tố (Prime Grids)
        # Tìm các hình chữ nhật lớn nhất toàn số 1 trong RAM
        prime_grids = self._compute_prime_grids(ram_data)

        # 4. Tìm phủ tối thiểu (Minimum Cover)
        # Chọn số lượng Grid ít nhất để phủ hết các số 1 trong RAM
        cover = self._find_minimum_cover(ram_data, prime_grids)

        # 5. Xây dựng NFA kết quả từ Cover
        # Ánh xạ mỗi Grid trong cover thành 1 trạng thái mới
        final_nfa = self._construct_nfa_from_cover(matrix_data, ram_data, cover)
        
        return final_nfa

    def _make_state_map(self):
        # Bước 1: Determinize (M')
        dfa = self.nfa.determinize()
        
        # Bước 2: Dual -> Determinize (M^R')
        dual_dfa = self.nfa.reverse().determinize()

        if not dfa.states or not dual_dfa.states:
            return None

        # Sắp xếp để có thứ tự cố định (Indexable)
        # Đưa Start State lên đầu danh sách
        dfa_states = list(dfa.states)
        dfa_start = next(iter(dfa.start_states)) if dfa.start_states else None
        if dfa_start and dfa_start in dfa_states:
            dfa_states.remove(dfa_start)
            dfa_states.insert(0, dfa_start)

        dual_states = list(dual_dfa.states)
        dual_start = next(iter(dual_dfa.start_states)) if dual_dfa.start_states else None
        if dual_start and dual_start in dual_states:
            dual_states.remove(dual_start)
            dual_states.insert(0, dual_start)

        rows_count = len(dfa_states)
        cols_count = len(dual_states)
        
        # Ma trận Boolean EAM (Elementary Automaton Matrix)
        # EAM[i][j] = True nếu (State_i của DFA) giao (State_j của Dual_DFA) khác rỗng
        eam = [[False for _ in range(cols_count)] for _ in range(rows_count)]

        for r in range(rows_count):
            row_set = dfa_states[r] # Set các state gốc
            for c in range(cols_count):
                col_set = dual_states[c] # Set các state gốc
                # Kiểm tra giao nhau
                if not row_set.isdisjoint(col_set):
                    eam[r][c] = True

        return {
            "dfa": dfa,
            "dfa_states": dfa_states, # ordered
            "dual_states": dual_states, # ordered
            "eam": eam,
            "rows": rows_count,
            "cols": cols_count
        }

    def _reduce_state_map(self, matrix_data):
        eam = matrix_data["eam"]
        rows = matrix_data["rows"]
        cols = matrix_data["cols"]

        # --- Gộp Dòng (Merge Rows) ---
        # rows_map[new_index] = {set of original indices}
        merged_rows = []
        visited_rows = [False] * rows
        
        for r in range(rows):
            if visited_rows[r]: continue
            current_group = {r}
            visited_rows[r] = True
            
            # Tìm các dòng giống hệt dòng r
            for r2 in range(r + 1, rows):
                if not visited_rows[r2]:
                    if eam[r] == eam[r2]: # So sánh list boolean
                        current_group.add(r2)
                        visited_rows[r2] = True
            merged_rows.append(current_group)

        # --- Gộp Cột (Merge Cols) ---
        merged_cols = []
        visited_cols = [False] * cols

        for c in range(cols):
            if visited_cols[c]: continue
            current_group = {c}
            visited_cols[c] = True
            
            # Lấy vector cột c
            col_vec = [eam[r][c] for r in range(rows)]
            
            for c2 in range(c + 1, cols):
                if not visited_cols[c2]:
                    col_vec2 = [eam[r][c2] for r in range(rows)]
                    if col_vec == col_vec2:
                        current_group.add(c2)
                        visited_cols[c2] = True
            merged_cols.append(current_group)

        # --- Tạo Ma trận thu gọn (RAM) ---
        new_rows_count = len(merged_rows)
        new_cols_count = len(merged_cols)
        ram = [[False for _ in range(new_cols_count)] for _ in range(new_rows_count)]

        for r_idx, r_group in enumerate(merged_rows):
            original_r = next(iter(r_group))
            for c_idx, c_group in enumerate(merged_cols):
                original_c = next(iter(c_group))
                ram[r_idx][c_idx] = eam[original_r][original_c]

        return {
            "ram": ram,
            "merged_rows": merged_rows, # List of sets
            "merged_cols": merged_cols, # List of sets
            "rows": new_rows_count,
            "cols": new_cols_count
        }

    def _compute_prime_grids(self, ram_data):
        ram = ram_data["ram"]
        rows = ram_data["rows"]
        cols = ram_data["cols"]

        # Khởi tạo: Mỗi ô True là một Grid 1x1
        grids = []
        for r in range(rows):
            for c in range(cols):
                if ram[r][c]:
                    grids.append(Grid({r}, {c}))

        prime_grids = set()
        queue = list(grids)
        processed_hashes = set()

        while queue:
            g = queue.pop(0)
            if hash(g) in processed_hashes:
                continue
            processed_hashes.add(hash(g))

            is_prime = True
            
            # 1. Thử mở rộng thêm Dòng
            # Tìm các dòng chưa có trong grid
            candidate_rows = set(range(rows)) - g.rows
            for r in candidate_rows:
                # Điều kiện: Dòng r phải có True ở TẤT CẢ các cột hiện tại của Grid
                can_add = True
                for c in g.cols:
                    if not ram[r][c]:
                        can_add = False
                        break
                
                if can_add:
                    # Tạo grid mới
                    new_rows = set(g.rows)
                    new_rows.add(r)
                    new_g = Grid(new_rows, g.cols)
                    if hash(new_g) not in processed_hashes:
                        queue.append(new_g)
                    is_prime = False # Grid hiện tại chưa phải cực đại vì còn mở rộng được

            # 2. Thử mở rộng thêm Cột
            candidate_cols = set(range(cols)) - g.cols
            for c in candidate_cols:
                can_add = True
                for r in g.rows:
                    if not ram[r][c]:
                        can_add = False
                        break
                
                if can_add:
                    new_cols = set(g.cols)
                    new_cols.add(c)
                    new_g = Grid(g.rows, new_cols)
                    if hash(new_g) not in processed_hashes:
                        queue.append(new_g)
                    is_prime = False

            if is_prime:
                prime_grids.add(g)

        return list(prime_grids)

    def _find_minimum_cover(self, ram_data, prime_grids):
        ram = ram_data["ram"]
        rows = ram_data["rows"]
        cols = ram_data["cols"]

        # Tập hợp tất cả các ô (r, c) cần được phủ (những ô True)
        universe = set()
        for r in range(rows):
            for c in range(cols):
                if ram[r][c]:
                    universe.add((r, c))

        if not universe:
            return []

        # Map: Grid -> tập các ô nó phủ
        grid_covers = {}
        for g in prime_grids:
            cells = set()
            for r in g.rows:
                for c in g.cols:
                    cells.add((r, c))
            grid_covers[g] = cells

        # Thuật toán tìm Set Cover chính xác (Backtracking tối ưu)
        # Sắp xếp grid theo khả năng phủ (Greedy heuristic để duyệt nhanh hơn)
        sorted_grids = sorted(prime_grids, key=lambda g: len(grid_covers[g]), reverse=True)
        
        best_solution = None

        def backtrack(index, current_solution, covered_cells):
            nonlocal best_solution
            
            # Pruning: Nếu solution hiện tại đã dài hơn best solution tìm được -> Dừng
            if best_solution is not None and len(current_solution) >= len(best_solution):
                return

            # Base case: Đã phủ hết
            if covered_cells == universe:
                if best_solution is None or len(current_solution) < len(best_solution):
                    best_solution = list(current_solution)
                return

            if index >= len(sorted_grids):
                return

            grid = sorted_grids[index]
            new_cells = grid_covers[grid]
            
            # Nhánh 1: Chọn Grid này (nếu nó giúp phủ thêm ít nhất 1 ô mới)
            if not new_cells.issubset(covered_cells):
                current_solution.append(grid)
                backtrack(index + 1, current_solution, covered_cells | new_cells)
                current_solution.pop()

            # Nhánh 2: Không chọn Grid này
            backtrack(index + 1, current_solution, covered_cells)

        # Chạy backtracking
        # Lưu ý: Với bài toán lớn, đây là NP-Hard. Với NFA nhỏ/vừa thì chạy tốt.
        backtrack(0, [], set())
        
        return best_solution if best_solution else []

    def _construct_nfa_from_cover(self, matrix_data, ram_data, cover):
        # Đây là phần thực hiện logic "FromIntersectionRule" trong C#
        final_nfa = NFA()
        alphabet = self.nfa.alphabet
        
        # Mapping Grid -> Integer State ID (0, 1, 2...)
        grid_to_id = {g: i for i, g in enumerate(cover)}
        
        # Thêm states vào NFA mới
        for i in range(len(cover)):
            final_nfa.states.add(i)

        # Dữ liệu cần thiết từ các bước trước
        dfa_states_ordered = matrix_data["dfa_states"] # List các frozenset (state gốc)
        dfa = matrix_data["dfa"]
        merged_rows = ram_data["merged_rows"] # Mapping RAM row index -> DFA state indices

        # --- Xử lý Start / Accept States ---
        # Grid chứa hàng 0 (đại diện Start State của DFA) -> Là Start State
        # Grid chứa cột 0 (đại diện Start State của Dual DFA -> Accept của gốc) -> Là Accept State
        # (Logic C#: if grid.Rows.Contains(0) => Start; if grid.Columns.Contains(0) => Accept)
        # Lưu ý: Cột 0 của RAM tương ứng với nhóm cột chứa cột 0 của EAM
        
        ram_col_0_group_idx = -1
        for idx, group in enumerate(ram_data["merged_cols"]):
            if 0 in group: # Cột 0 của EAM nằm trong nhóm này
                ram_col_0_group_idx = idx
                break
        
        ram_row_0_group_idx = -1
        for idx, group in enumerate(merged_rows):
            if 0 in group: # Hàng 0 của EAM nằm trong nhóm này
                ram_row_0_group_idx = idx
                break

        for g, state_id in grid_to_id.items():
            if ram_row_0_group_idx != -1 and ram_row_0_group_idx in g.rows:
                final_nfa.start_states.add(state_id)
            if ram_col_0_group_idx != -1 and ram_col_0_group_idx in g.cols:
                final_nfa.accept_states.add(state_id)

        # --- Xử lý Transitions (Intersection Rule) ---
        # Logic: State I chuyển sang State J qua ký tự 'c' nếu:
        # Tập hợp tất cả DFA states nằm trong các dòng của Grid I,
        # khi đi qua 'c', đến các DFA states đích.
        # Các DFA states đích này phải nằm gọn trong các dòng của Grid J.
        
        # Để tối ưu, ta tính trước: Với mỗi RAM Row, nó đại diện cho DFA States nào?
        # ram_row_to_dfa_indices[r_idx] = {0, 3, 5...}
        ram_row_to_dfa_indices = merged_rows 

        # Tạo helper map: DFA State Index -> Tập các Grid ID chứa nó (ở phần Row)
        # dfastate_in_grids[dfa_idx] = {grid_id_1, grid_id_2...}
        dfastate_in_grids = collections.defaultdict(set)
        for g, g_id in grid_to_id.items():
            for r_idx in g.rows:
                for dfa_idx in ram_row_to_dfa_indices[r_idx]:
                    dfastate_in_grids[dfa_idx].add(g_id)

        # Duyệt qua từng Grid nguồn (State nguồn)
        for src_grid, src_id in grid_to_id.items():
            
            # Lấy tất cả DFA States tương ứng với các dòng trong src_grid
            src_dfa_indices = set()
            for r_idx in src_grid.rows:
                src_dfa_indices.update(ram_row_to_dfa_indices[r_idx])

            # Với mỗi ký tự trong bảng chữ cái
            for char in alphabet:
                # Tìm tập hợp các Grid đích có thể đến
                # Theo Intersection Rule: Target Grids = Giao(Assignments(NextStates))
                
                target_grids_sets = [] 
                
                # Duyệt qua từng DFA state trong Grid nguồn
                for dfa_idx in src_dfa_indices:
                    current_dfa_state = dfa_states_ordered[dfa_idx]
                    
                    # Tìm trạng thái DFA kế tiếp qua 'char'
                    # Vì là DFA nên chỉ có tối đa 1 state kế tiếp (nhưng cấu trúc NFA lưu set)
                    next_dfa_states = dfa.transitions[current_dfa_state].get(char, set())
                    
                    if not next_dfa_states:
                        # Nếu không có đường đi, nghĩa là đi vào hố đen -> giao với tập rỗng -> rỗng
                        target_grids_sets.append(set())
                        continue

                    next_state = next(iter(next_dfa_states)) # Chỉ có 1 vì là DFA
                    
                    # Tìm index của next_state trong dfa_states_ordered
                    try:
                        next_idx = dfa_states_ordered.index(next_state)
                        # Lấy tập các Grid ID chứa dòng tương ứng với next_idx
                        target_grids_sets.append(dfastate_in_grids[next_idx])
                    except ValueError:
                        target_grids_sets.append(set())

                # Giao tất cả các tập Grid đích lại
                if target_grids_sets:
                    valid_dest_ids = set.intersection(*target_grids_sets)
                    for dest_id in valid_dest_ids:
                        final_nfa.add_transition(src_id, char, dest_id)

        final_nfa.alphabet = alphabet
        return final_nfa
