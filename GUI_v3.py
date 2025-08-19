import customtkinter as ctk
from tkinter import StringVar, messagebox
import time
import random

class SudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sudoku")
        self.geometry("600x850")
        self.grid_columnconfigure(0, weight=1)

        # --- Game State ---
        self.initial_board = [[0]*9 for _ in range(9)]
        self.solution = [[0]*9 for _ in range(9)]
        self.grid_data = [[0]*9 for _ in range(9)]
        self.selected_cell = None
        self.mistakes = 0
        self.elapsed_time = 0
        self.timer_running = False
        self.timer_id = None
        self.hints_used = 0
        self.max_hints = 3
        self.first_move_made = False

        # --- UI Vars ---
        self.cell_vars = [[StringVar() for _ in range(9)] for _ in range(9)]
        self.cell_widgets = [[None for _ in range(9)] for _ in range(9)]
        self.difficulty_var = StringVar(value="Medium")

        # --- Theme & Fonts ---
        self.light_theme = {
            "main_bg": "#EAEBEC", "grid_bg": "#FFFFFF", "prefilled_text": "#1F1F1F",
            "user_text": "#2E63B2", "block_colors": ("#FFFFFF", "#F0F0F0"),
            "highlight_bg": "#D6E4F0", "selected_cell_bg": "#A9CCE3",
            "solving_fg": "#3A9A41", "backtrack_fg": "#D9534F", "error_bg": "#F5B7B1"
        }
        self.dark_theme = {
            "main_bg": "#1F1F1F", "grid_bg": "#2B2B2B", "prefilled_text": "#EAEBEC",
            "user_text": "#85C1E9", "block_colors": ("#2B2B2B", "#343638"),
            "highlight_bg": "#4A4D50", "selected_cell_bg": "#34495E",
            "solving_fg": "#2ECC71", "backtrack_fg": "#E74C3C", "error_bg": "#A93226"
        }
        self.theme = self.light_theme
        self.font_regular = ("Helvetica", 18)
        self.font_bold = ("Helvetica", 18, "bold")

        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        # --- Top Frame (New Game & Difficulty) ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=20, fill="x")
        self.top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.new_game_button = ctk.CTkButton(self.top_frame, text="New Game", command=self.new_game)
        self.new_game_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.top_frame, text="Difficulty:").grid(row=0, column=1, sticky="e", padx=5)
        self.difficulty_menu = ctk.CTkOptionMenu(self.top_frame, variable=self.difficulty_var, values=["Easy", "Medium", "Hard", "Expert"])
        self.difficulty_menu.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # --- Stats Frame ---
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(pady=5, padx=20, fill="x")
        self.stats_frame.grid_columnconfigure((0,1,2), weight=1)

        self.timer_label = ctk.CTkLabel(self.stats_frame, text="Time: 00:00")
        self.timer_label.grid(row=0, column=0)
        self.mistakes_label = ctk.CTkLabel(self.stats_frame, text="Mistakes: 0")
        self.mistakes_label.grid(row=0, column=1)
        self.hints_label = ctk.CTkLabel(self.stats_frame, text=f"Hints: {self.max_hints}")
        self.hints_label.grid(row=0, column=2)

        # --- Main Grid Frame ---
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(pady=20, padx=20, fill="both", expand=True)
        block_frames = [[ctk.CTkFrame(self.grid_frame, fg_color="transparent", border_width=2) for _ in range(3)] for _ in range(3)]
        for r_block in range(3):
            self.grid_frame.grid_rowconfigure(r_block, weight=1)
            for c_block in range(3):
                self.grid_frame.grid_columnconfigure(c_block, weight=1)
                block_frames[r_block][c_block].grid(row=r_block, column=c_block, padx=1, pady=1, sticky="nsew")

        # --- Cells ---
        for r in range(9):
            for c in range(9):
                r_block, c_block = r // 3, c // 3
                r_local, c_local = r % 3, c % 3
                cell = ctk.CTkEntry(
                    block_frames[r_block][c_block], width=60, height=60, justify="center",
                    textvariable=self.cell_vars[r][c], corner_radius=0, border_width=0)
                cell.grid(row=r_local, column=c_local, padx=1, pady=1, sticky="nsew")
                cell.bind("<FocusIn>", lambda e, r=r, c=c: self.select_cell(r, c))
                cell.bind("<KeyRelease>", lambda e, r=r, c=c: self.validate_entry(r, c))
                self.cell_widgets[r][c] = cell

        # --- Controls Frame ---
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(pady=10, padx=20, fill="x")
        self.controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.solve_button = ctk.CTkButton(self.controls_frame, text="Solve", command=self.solve_puzzle_visual)
        self.solve_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.hint_button = ctk.CTkButton(self.controls_frame, text="Hint", command=self.use_hint)
        self.hint_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.clear_button = ctk.CTkButton(self.controls_frame, text="Clear", command=self.clear_user_input)
        self.clear_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.reset_button = ctk.CTkButton(self.controls_frame, text="Reset", command=self.reset_board)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        self.theme_switch = ctk.CTkSwitch(self.controls_frame, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.pack(pady=5, padx=20, fill="x")

    def new_game(self):
        self.stop_timer()
        difficulty = self.difficulty_var.get()
        self.generate_puzzle(difficulty)
        self.grid_data = [row[:] for row in self.initial_board]
        self.reset_stats()
        self.reset_board()
        self.status_label.configure(text=f"{difficulty} puzzle loaded. Good luck!")

    def reset_stats(self):
        self.mistakes = 0
        self.elapsed_time = 0
        self.hints_used = 0
        self.first_move_made = False
        self.mistakes_label.configure(text=f"Mistakes: {self.mistakes}")
        self.timer_label.configure(text="Time: 00:00")
        self.update_hints_label()

    def generate_puzzle(self, difficulty):
        board = [[0]*9 for _ in range(9)]
        self.solve_for_solution(board, shuffle_numbers=True)
        self.solution = [row[:] for row in board]

        clues = {"Easy": 40, "Medium": 32, "Hard": 25, "Expert": 22}
        cells_to_remove = 81 - clues.get(difficulty, 32)
        
        self.initial_board = [row[:] for row in self.solution]
        
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        
        for r, c in cells[:cells_to_remove]:
            self.initial_board[r][c] = 0

    def use_hint(self):
        if self.hints_used >= self.max_hints:
            self.status_label.configure(text="No hints left!")
            return
        if not self.selected_cell:
            self.status_label.configure(text="Select a cell to use a hint.")
            return

        r, c = self.selected_cell
        if self.initial_board[r][c] != 0 or self.grid_data[r][c] != 0:
            self.status_label.configure(text="Cell is already filled.")
            return

        if not self.first_move_made:
            self.first_move_made = True
            self.start_timer()
            
        correct_value = self.solution[r][c]
        self.grid_data[r][c] = correct_value
        self.cell_vars[r][c].set(str(correct_value))
        
        self.hints_used += 1
        self.update_hints_label()
        self.highlight_related_cells(r, c)
        self.check_completion()
    
    def update_hints_label(self):
        remaining = self.max_hints - self.hints_used
        self.hints_label.configure(text=f"Hints: {remaining}")
        self.hint_button.configure(state="disabled" if remaining <= 0 else "normal")
            
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time += 1
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.timer_label.configure(text=f"Time: {minutes:02d}:{seconds:02d}")
            self.timer_id = self.after(1000, self.update_timer)

    def validate_entry(self, r, c):
        value = self.cell_vars[r][c].get()

        if not value.isdigit() or len(value) > 1 or value == '0':
            self.cell_vars[r][c].set("")
            self.grid_data[r][c] = 0
            return

        if not self.first_move_made:
            self.first_move_made = True
            self.start_timer()

        num = int(value)
        if num == self.solution[r][c]:
            self.grid_data[r][c] = num
            self.highlight_related_cells(r,c)
            self.check_completion()
        else:
            self.mistakes += 1
            self.mistakes_label.configure(text=f"Mistakes: {self.mistakes}")
            self.cell_widgets[r][c].configure(fg_color=self.theme["error_bg"])
            self.after(500, lambda: self.highlight_related_cells(r, c))
            self.after(100, lambda: self.cell_vars[r][c].set(""))
            self.grid_data[r][c] = 0
            
    def check_completion(self):
        for r in range(9):
            for c in range(9):
                if self.grid_data[r][c] != self.solution[r][c]:
                    return False
        
        self.stop_timer()
        time_str = self.timer_label.cget('text').split(' ')[1]
        msg = f"Solved in {time_str} with {self.mistakes} mistakes."
        self.status_label.configure(text=f"Congratulations! {msg}")
        messagebox.showinfo("Sudoku", f"You solved the puzzle!\n{msg}")
        return True

    def reset_board(self):
        self.grid_data = [row[:] for row in self.initial_board]
        self.stop_timer()
        self.reset_stats()
        
        for r in range(9):
            for c in range(9):
                value = self.grid_data[r][c]
                is_prefilled = value != 0
                self.cell_vars[r][c].set(str(value) if is_prefilled else "")
                self.cell_widgets[r][c].configure(
                    font=self.font_bold if is_prefilled else self.font_regular,
                    state="disabled" if is_prefilled else "normal")
        self.update_colors()

    def clear_user_input(self):
        for r in range(9):
            for c in range(9):
                if self.initial_board[r][c] == 0:
                    self.grid_data[r][c] = 0
                    self.cell_vars[r][c].set("")
        self.update_colors()
        self.status_label.configure(text="User input cleared")

    def toggle_theme(self):
        ctk.set_appearance_mode("dark" if self.theme_switch.get() == 1 else "light")
        self.theme = self.dark_theme if self.theme_switch.get() == 1 else self.light_theme
        self.update_colors()

    def update_colors(self):
        self.configure(fg_color=self.theme["main_bg"])
        for r in range(9):
            for c in range(9):
                is_prefilled = self.initial_board[r][c] != 0
                block_color = self.theme["block_colors"][(r // 3 + c // 3) % 2]
                text_color = self.theme["prefilled_text"] if is_prefilled else self.theme["user_text"]
                self.cell_widgets[r][c].configure(fg_color=block_color, text_color=text_color)
    
    def select_cell(self, r, c):
        if self.initial_board[r][c] != 0:
            self.grid_frame.focus_set()
            return
        self.selected_cell = (r, c)
        self.highlight_related_cells(r, c)

    def highlight_related_cells(self, r_sel, c_sel):
        self.update_colors()
        box_r_start, box_c_start = r_sel // 3 * 3, c_sel // 3 * 3
        for i in range(9):
            for j in range(9):
                in_row, in_col = (i == r_sel), (j == c_sel)
                in_box = (box_r_start <= i < box_r_start + 3 and box_c_start <= j < box_c_start + 3)
                if in_row or in_col or in_box:
                    self.cell_widgets[i][j].configure(fg_color=self.theme["highlight_bg"])
        self.cell_widgets[r_sel][c_sel].configure(fg_color=self.theme["selected_cell_bg"])

    def solve_for_solution(self, board, shuffle_numbers=False):
        empty = self.find_empty(board)
        if not empty:
            return True
        row, col = empty
        
        numbers = list(range(1, 10))
        if shuffle_numbers:
            random.shuffle(numbers)

        for num in numbers:
            if self.is_valid(num, (row, col), board):
                board[row][col] = num
                if self.solve_for_solution(board, shuffle_numbers):
                    return True
                board[row][col] = 0
        return False
    
    def solve_puzzle_visual(self):
        self.set_ui_state(False)
        self.stop_timer()
        self.status_label.configure(text="Solving...")
        self.update()
        
        self.grid_data = [row[:] for row in self.initial_board]
        
        if self.solve_recursive_visual():
            self.status_label.configure(text="Solved!")
            self.animate_success()
        else:
            self.status_label.configure(text="No solution found!")
            messagebox.showerror("Solver", "This Sudoku puzzle has no solution.")
        self.set_ui_state(True)
        
    def solve_recursive_visual(self):
        empty = self.find_empty(self.grid_data)
        if not empty:
            return True
        row, col = empty

        for num in range(1, 10):
            if self.is_valid(num, (row, col), self.grid_data):
                self.grid_data[row][col] = num
                self.cell_vars[row][col].set(str(num))
                self.cell_widgets[row][col].configure(text_color=self.theme["solving_fg"])
                self.update()
                time.sleep(0.01)
                if self.solve_recursive_visual():
                    return True
                self.grid_data[row][col] = 0
                self.cell_vars[row][col].set("")
                self.cell_widgets[row][col].configure(text_color=self.theme["backtrack_fg"])
                self.update()
                time.sleep(0.02)
        
        self.cell_widgets[row][col].configure(text_color=self.theme["user_text"])
        return False

    def animate_success(self):
        for r in range(9):
            for c in range(9):
                self.cell_widgets[r][c].configure(fg_color=self.theme["solving_fg"])
                self.update()
                time.sleep(0.01)
        self.after(500, self.update_colors)

    def set_ui_state(self, is_enabled):
        state = "normal" if is_enabled else "disabled"
        self.solve_button.configure(state=state)
        self.clear_button.configure(state=state)
        self.reset_button.configure(state=state)
        self.new_game_button.configure(state=state)
        self.difficulty_menu.configure(state=state)
        self.update_hints_label()
        for r in range(9):
            for c in range(9):
                if self.initial_board[r][c] == 0:
                    self.cell_widgets[r][c].configure(state=state)

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def is_valid(self, num, pos, board):
        row, col = pos
        if num in board[row]: return False
        if num in [board[r][col] for r in range(9)]: return False
        box_x, box_y = col // 3, row // 3
        for r in range(box_y * 3, box_y * 3 + 3):
            for c in range(box_x * 3, box_x * 3 + 3):
                if board[r][c] == num:
                    return False
        return True

if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()