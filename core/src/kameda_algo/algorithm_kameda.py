import collections
import itertools

class NFA:
    def __init__(self, states=None, start_states=None, accept_states=None):
        self.states = set(states) if states else set()
        self.start_states = set(start_states) if start_states else set()
        self.accept_states = set(accept_states) if accept_states else set()
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

        result = NFA()
        result.alphabet = self.alphabet
        result.states = dfa_states
        result.start_states = {start_set}
        
        for subset in dfa_states:
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
        
        result.start_states = self.accept_states.copy()
        result.accept_states = self.start_states.copy()

        for src, trans in self.transitions.items():
            for char, dests in trans.items():
                for dst in dests:
                    result.add_transition(dst, char, src)
        
        return result

    def __repr__(self):
        return f"NFA(States={len(self.states)}, Start={len(self.start_states)}, Accept={len(self.accept_states)})"

class Grid:
    """Đại diện cho một hình chữ nhật trong ma trận RAM"""
    def __init__(self, rows, cols):
        self.rows = frozenset(rows) 
        self.cols = frozenset(cols) 

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
        matrix_data = self._make_state_map()
        if not matrix_data: 
            return NFA() 

        ram_data = self._reduce_state_map(matrix_data)

        prime_grids = self._compute_prime_grids(ram_data)

        cover = self._find_minimum_cover(ram_data, prime_grids)

        final_nfa = self._construct_nfa_from_cover(matrix_data, ram_data, cover)
        
        return final_nfa

    def _make_state_map(self):
        dfa = self.nfa.determinize()

        dual_dfa = self.nfa.reverse().determinize()

        if not dfa.states or not dual_dfa.states:
            return None

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

        eam = [[False for _ in range(cols_count)] for _ in range(rows_count)]

        for r in range(rows_count):
            row_set = dfa_states[r]
            for c in range(cols_count):
                col_set = dual_states[c] 
                if not row_set.isdisjoint(col_set):
                    eam[r][c] = True

        return {
            "dfa": dfa,
            "dfa_states": dfa_states, 
            "dual_states": dual_states,
            "eam": eam,
            "rows": rows_count,
            "cols": cols_count
        }

    def _reduce_state_map(self, matrix_data):
        eam = matrix_data["eam"]
        rows = matrix_data["rows"]
        cols = matrix_data["cols"]

        merged_rows = []
        visited_rows = [False] * rows
        
        for r in range(rows):
            if visited_rows[r]: continue
            current_group = {r}
            visited_rows[r] = True
            
            for r2 in range(r + 1, rows):
                if not visited_rows[r2]:
                    if eam[r] == eam[r2]:
                        current_group.add(r2)
                        visited_rows[r2] = True
            merged_rows.append(current_group)

        merged_cols = []
        visited_cols = [False] * cols

        for c in range(cols):
            if visited_cols[c]: continue
            current_group = {c}
            visited_cols[c] = True

            col_vec = [eam[r][c] for r in range(rows)]
            
            for c2 in range(c + 1, cols):
                if not visited_cols[c2]:
                    col_vec2 = [eam[r][c2] for r in range(rows)]
                    if col_vec == col_vec2:
                        current_group.add(c2)
                        visited_cols[c2] = True
            merged_cols.append(current_group)

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
            "merged_rows": merged_rows, 
            "merged_cols": merged_cols, 
            "rows": new_rows_count,
            "cols": new_cols_count
        }

    def _compute_prime_grids(self, ram_data):
        ram = ram_data["ram"]
        rows = ram_data["rows"]
        cols = ram_data["cols"]

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

            candidate_rows = set(range(rows)) - g.rows
            for r in candidate_rows:
                can_add = True
                for c in g.cols:
                    if not ram[r][c]:
                        can_add = False
                        break
                
                if can_add:
                    new_rows = set(g.rows)
                    new_rows.add(r)
                    new_g = Grid(new_rows, g.cols)
                    if hash(new_g) not in processed_hashes:
                        queue.append(new_g)
                    is_prime = False 

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

        universe = set()
        for r in range(rows):
            for c in range(cols):
                if ram[r][c]:
                    universe.add((r, c))

        if not universe:
            return []

        grid_covers = {}
        for g in prime_grids:
            cells = set()
            for r in g.rows:
                for c in g.cols:
                    cells.add((r, c))
            grid_covers[g] = cells

        sorted_grids = sorted(prime_grids, key=lambda g: len(grid_covers[g]), reverse=True)
        
        best_solution = None

        def backtrack(index, current_solution, covered_cells):
            nonlocal best_solution

            if best_solution is not None and len(current_solution) >= len(best_solution):
                return

            if covered_cells == universe:
                if best_solution is None or len(current_solution) < len(best_solution):
                    best_solution = list(current_solution)
                return

            if index >= len(sorted_grids):
                return

            grid = sorted_grids[index]
            new_cells = grid_covers[grid]

            if not new_cells.issubset(covered_cells):
                current_solution.append(grid)
                backtrack(index + 1, current_solution, covered_cells | new_cells)
                current_solution.pop()

            backtrack(index + 1, current_solution, covered_cells)

        backtrack(0, [], set())
        
        return best_solution if best_solution else []

    def _construct_nfa_from_cover(self, matrix_data, ram_data, cover):
        final_nfa = NFA()
        alphabet = self.nfa.alphabet

        grid_to_id = {g: i for i, g in enumerate(cover)}
        
        for i in range(len(cover)):
            final_nfa.states.add(i)

        dfa_states_ordered = matrix_data["dfa_states"] 
        dfa = matrix_data["dfa"]
        merged_rows = ram_data["merged_rows"] 
        
        ram_col_0_group_idx = -1
        for idx, group in enumerate(ram_data["merged_cols"]):
            if 0 in group:
                ram_col_0_group_idx = idx
                break
        
        ram_row_0_group_idx = -1
        for idx, group in enumerate(merged_rows):
            if 0 in group:
                ram_row_0_group_idx = idx
                break

        for g, state_id in grid_to_id.items():
            if ram_row_0_group_idx != -1 and ram_row_0_group_idx in g.rows:
                final_nfa.start_states.add(state_id)
            if ram_col_0_group_idx != -1 and ram_col_0_group_idx in g.cols:
                final_nfa.accept_states.add(state_id)

        ram_row_to_dfa_indices = merged_rows 

        dfastate_in_grids = collections.defaultdict(set)
        for g, g_id in grid_to_id.items():
            for r_idx in g.rows:
                for dfa_idx in ram_row_to_dfa_indices[r_idx]:
                    dfastate_in_grids[dfa_idx].add(g_id)

        for src_grid, src_id in grid_to_id.items():

            src_dfa_indices = set()
            for r_idx in src_grid.rows:
                src_dfa_indices.update(ram_row_to_dfa_indices[r_idx])
            for char in alphabet:
                
                target_grids_sets = [] 

                for dfa_idx in src_dfa_indices:
                    current_dfa_state = dfa_states_ordered[dfa_idx]

                    next_dfa_states = dfa.transitions[current_dfa_state].get(char, set())
                    
                    if not next_dfa_states:
                        target_grids_sets.append(set())
                        continue

                    next_state = next(iter(next_dfa_states)) 
                    
                    try:
                        next_idx = dfa_states_ordered.index(next_state)
                        target_grids_sets.append(dfastate_in_grids[next_idx])
                    except ValueError:
                        target_grids_sets.append(set())

                if target_grids_sets:
                    valid_dest_ids = set.intersection(*target_grids_sets)
                    for dest_id in valid_dest_ids:
                        final_nfa.add_transition(src_id, char, dest_id)

        final_nfa.alphabet = alphabet
        return final_nfa
