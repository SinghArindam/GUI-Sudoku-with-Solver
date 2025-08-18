import customtkinter as ctk
from tkinter import StringVar, messagebox
import time

class SudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sudoku Visualizer")
        self.geometry("600x750")
        self.grid_columnconfigure(0, weight=1)

        # --- Color and Font Palette ---
        self.light_theme = {
            "main_bg": "#EAEBEC",
            "grid_bg": "#FFFFFF",
            "prefilled_text": "#1F1F1F",
            "user_text": "#2E63B2",
            "block_colors": ("#FFFFFF", "#F0F0F0"),
            "highlight_bg": "#D6E4F0",
            "selected_cell_bg": "#A9CCE3",
            "solving_fg": "#3A9A41", # Green for placing
            "backtrack_fg": "#D9534F"  # Red for backtracking
        }
        self.dark_theme = {
            "main_bg": "#1F1F1F",
            "grid_bg": "#2B2B2B",
            "prefilled_text": "#EAEBEC",
            "user_text": "#85C1E9",
            "block_colors": ("#2B2B2B", "#343638"),
            "highlight_bg": "#4A4D50",
            "selected_cell_bg": "#34495E",
            "solving_fg": "#2ECC71",
            "backtrack_fg": "#E74C3C"
        }
        self.theme = self.light_theme
        self.font_regular = ("Helvetica", 18)
        self.font_bold = ("Helvetica", 18, "bold")

        # --- Data Structures ---
        self.initial_board = [
            [7, 8, 0, 4, 0, 0, 1, 2, 0], [6, 0, 0, 0, 7, 5, 0, 0, 9],
            [0, 0, 0, 6, 0, 1, 0, 7, 8], [0, 0, 7, 0, 4, 0, 2, 6, 0],
            [0, 0, 1, 0, 5, 0, 9, 3, 0], [9, 0, 4, 0, 6, 0, 0, 0, 5],
            [0, 7, 0, 3, 0, 0, 0, 1, 2], [1, 2, 0, 0, 0, 7, 4, 0, 0],
            [0, 4, 9, 2, 0, 6, 0, 0, 7]
        ]
        self.grid_data = [row[:] for row in self.initial_board]
        self.cell_vars = [[StringVar() for _ in range(9)] for _ in range(9)]
        self.cell_widgets = [[None for _ in range(9)] for _ in range(9)]
        self.selected_cell = None

        self.create_widgets()
        self.reset_board()

    def create_widgets(self):
        # --- Main Grid Frame ---
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        block_frames = [[ctk.CTkFrame(self.grid_frame, fg_color="transparent", border_width=2) 
                         for _ in range(3)] for _ in range(3)]
        
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
                    block_frames[r_block][c_block],
                    width=60, height=60,
                    justify="center",
                    textvariable=self.cell_vars[r][c],
                    corner_radius=0,
                    border_width=0
                )
                cell.grid(row=r_local, column=c_local, padx=1, pady=1, sticky="nsew")
                cell.bind("<FocusIn>", lambda e, r=r, c=c: self.select_cell(r, c))
                cell.bind("<KeyRelease>", lambda e, r=r, c=c: self.validate_entry(r, c))
                self.cell_widgets[r][c] = cell
        
        # --- Controls Frame ---
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(pady=10, padx=20, fill="x")
        self.controls_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.solve_button = ctk.CTkButton(self.controls_frame, text="Solve", command=self.solve_puzzle_visual)
        self.solve_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.clear_button = ctk.CTkButton(self.controls_frame, text="Clear", command=self.clear_user_input)
        self.clear_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.reset_button = ctk.CTkButton(self.controls_frame, text="Reset", command=self.reset_board)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # --- Theme Toggle ---
        self.theme_switch = ctk.CTkSwitch(self.controls_frame, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=1, column=0, columnspan=3, pady=10)
        
        # --- Status Bar ---
        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.pack(pady=5, padx=20, fill="x")

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.theme = self.dark_theme
        else:
            ctk.set_appearance_mode("light")
            self.theme = self.light_theme
        self.update_colors()

    def update_colors(self):
        self.configure(fg_color=self.theme["main_bg"])
        for r in range(9):
            for c in range(9):
                cell_widget = self.cell_widgets[r][c]
                is_prefilled = self.initial_board[r][c] != 0
                
                block_color = self.theme["block_colors"][(r // 3 + c // 3) % 2]
                text_color = self.theme["prefilled_text"] if is_prefilled else self.theme["user_text"]
                
                cell_widget.configure(
                    fg_color=block_color,
                    text_color=text_color
                )

    def select_cell(self, r, c):
        if self.initial_board[r][c] != 0:
            self.cell_widgets[r][c].master.focus_set()
            return
            
        self.selected_cell = (r, c)
        self.highlight_related_cells(r, c)

    def highlight_related_cells(self, r_sel, c_sel):
        self.update_colors() # Reset all colors first
        
        # Highlight row, column, and block
        box_r_start, box_c_start = r_sel // 3 * 3, c_sel // 3 * 3
        for i in range(9):
            for j in range(9):
                in_row = (i == r_sel)
                in_col = (j == c_sel)
                in_box = (box_r_start <= i < box_r_start + 3 and box_c_start <= j < box_c_start + 3)
                
                if in_row or in_col or in_box:
                    self.cell_widgets[i][j].configure(fg_color=self.theme["highlight_bg"])
        
        # Highlight selected cell
        self.cell_widgets[r_sel][c_sel].configure(fg_color=self.theme["selected_cell_bg"])

    def validate_entry(self, r, c):
        value = self.cell_vars[r][c].get()
        if not value.isdigit() or not (1 <= int(value) <= 9):
            self.grid_data[r][c] = 0
            self.highlight_related_cells(r, c)
            return

        num = int(value)
        if self.is_valid(num, (r, c), self.grid_data):
            self.grid_data[r][c] = num
        else:
            self.grid_data[r][c] = 0
            self.cell_widgets[r][c].configure(fg_color=self.theme["backtrack_fg"])

    def set_ui_state(self, is_enabled):
        state = "normal" if is_enabled else "disabled"
        self.solve_button.configure(state=state)
        self.clear_button.configure(state=state)
        self.reset_button.configure(state=state)
        for r in range(9):
            for c in range(9):
                if self.initial_board[r][c] == 0:
                    self.cell_widgets[r][c].configure(state=state)

    def reset_board(self):
        self.grid_data = [row[:] for row in self.initial_board]
        for r in range(9):
            for c in range(9):
                value = self.grid_data[r][c]
                is_prefilled = value != 0
                
                self.cell_vars[r][c].set(str(value) if is_prefilled else "")
                self.cell_widgets[r][c].configure(
                    font=self.font_bold if is_prefilled else self.font_regular,
                    state="disabled" if is_prefilled else "normal"
                )
        self.update_colors()
        self.status_label.configure(text="Ready")
    
    def clear_user_input(self):
        for r in range(9):
            for c in range(9):
                if self.initial_board[r][c] == 0:
                    self.grid_data[r][c] = 0
                    self.cell_vars[r][c].set("")
        self.update_colors()
        self.status_label.configure(text="User input cleared")

    def solve_puzzle_visual(self):
        self.set_ui_state(False)
        self.status_label.configure(text="Solving...")
        self.update()
        
        if self.solve_recursive():
            self.status_label.configure(text="Solved! [Credits: @SinghArindam]")
            self.animate_success()
        else:
            self.status_label.configure(text="No solution found!")
            messagebox.showerror("Solver", "This Sudoku puzzle has no solution.")
        
        self.set_ui_state(True)
        
    def solve_recursive(self):
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

                if self.solve_recursive():
                    return True

                # Backtrack
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
            self.update_colors()

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def is_valid(self, num, pos, board):
        row, col = pos
        # Check row
        if num in board[row]:
            return False
        # Check column
        if num in [board[r][col] for r in range(9)]:
            return False
        # Check box
        box_x, box_y = col // 3, row // 3
        for r in range(box_y * 3, box_y * 3 + 3):
            for c in range(box_x * 3, box_x * 3 + 3):
                if board[r][c] == num:
                    return False
        return True


if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()