import customtkinter as ctk
from tkinter import StringVar
from time import sleep


class SudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sudoku")
        self.geometry("600x700")
        self.theme_mode = "light"
        self.saved_numbers = [[StringVar() for _ in range(9)] for _ in range(9)]
        self.grid = [
            [7, 8, 0, 4, 0, 0, 1, 2, 0],
            [6, 0, 0, 0, 7, 5, 0, 0, 9],
            [0, 0, 0, 6, 0, 1, 0, 7, 8],
            [0, 0, 7, 0, 4, 0, 2, 6, 0],
            [0, 0, 1, 0, 5, 0, 9, 3, 0],
            [9, 0, 4, 0, 6, 0, 0, 0, 5],
            [0, 7, 0, 3, 0, 0, 0, 1, 2],
            [1, 2, 0, 0, 0, 7, 4, 0, 0],
            [0, 4, 9, 2, 0, 6, 0, 0, 7],
        ]
        self.selected_cell = None

        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(pady=20)

        self.__table = []
        self.create_grid()

        # Theme toggle switch
        self.switch_frame = ctk.CTkFrame(self)
        self.switch_frame.pack(pady=10)
        self.theme_label = ctk.CTkLabel(self.switch_frame, text="Toggle Theme:")
        self.theme_label.grid(row=0, column=0, padx=5)
        self.theme_switch = ctk.CTkSwitch(
            self.switch_frame, text="Dark Mode", command=self.toggle_theme
        )
        self.theme_switch.grid(row=0, column=1, padx=5)

        # Solve button
        self.solve_button = ctk.CTkButton(
            self, text="Solve", command=self.solve_puzzle_with_animation
        )
        self.solve_button.pack(pady=10)

    def create_grid(self):
        font = ("Arial", 16)
        for i in range(9):
            row = []
            for j in range(9):
                color = "gray" if (i // 3 + j // 3) % 2 == 0 else "white"
                value = self.grid[i][j]
                cell = ctk.CTkEntry(
                    self.grid_frame,
                    width=50,
                    height=50,
                    justify="center",
                    font=font,
                    textvariable=self.saved_numbers[i][j],
                    corner_radius=0,
                )
                cell.configure(fg_color=color)
                if value != 0:
                    cell.insert(0, str(value))
                    cell.configure(state="disabled")  # Pre-filled cells are read-only
                else:
                    cell.bind("<FocusIn>", lambda e, r=i, c=j: self.select_cell(r, c))
                    cell.bind("<KeyRelease>", lambda e, r=i, c=j: self.validate_entry(r, c))
                cell.grid(row=i, column=j, padx=1, pady=1)
                row.append(cell)
            self.__table.append(row)

    def toggle_theme(self):
        if self.theme_switch.get() == 1:  # Dark mode enabled
            ctk.set_appearance_mode("dark")
        else:  # Light mode enabled
            ctk.set_appearance_mode("light")

    def validate_entry(self, row, col):
        value = self.saved_numbers[row][col].get()
        if not value.isdigit() or not (1 <= int(value) <= 9):
            self.__table[row][col].configure(fg_color="red")
            return

        num = int(value)
        if self.is_valid(num, (row, col)):
            self.grid[row][col] = num
            self.__table[row][col].configure(fg_color="lightgreen")
        else:
            self.grid[row][col] = 0
            self.__table[row][col].configure(fg_color="red")

    def is_valid(self, num, pos):
        row, col = pos

        # Check row
        for c in range(9):
            if self.grid[row][c] == num and col != c:
                return False

        # Check column
        for r in range(9):
            if self.grid[r][col] == num and row != r:
                return False

        # Check box
        box_x, box_y = col // 3, row // 3
        for r in range(box_y * 3, box_y * 3 + 3):
            for c in range(box_x * 3, box_x * 3 + 3):
                if self.grid[r][c] == num and (r, c) != pos:
                    return False

        return True

    def solve_puzzle_with_animation(self):
        if self.solve_with_animation():
            print("Sudoku Solved!")
        else:
            print("Sudoku cannot be solved!")

    def solve_with_animation(self):
        empty = self.find_empty()
        if not empty:
            return True  # Solved
        row, col = empty

        for num in range(1, 10):
            if self.is_valid(num, (row, col)):
                self.grid[row][col] = num
                self.saved_numbers[row][col].set(num)
                self.__table[row][col].configure(fg_color="lightgreen")  # Highlight cell
                self.update()
                sleep(0.1)  # Pause for animation

                if self.solve_with_animation():
                    return True

                # Backtracking
                self.grid[row][col] = 0
                self.saved_numbers[row][col].set("")
                self.__table[row][col].configure(fg_color="red")  # Highlight backtracking
                self.update()
                sleep(0.1)

        self.__table[row][col].configure(fg_color="gray")  # Reset color
        return False

    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return i, j
        return None

    def select_cell(self, row, col):
        self.selected_cell = (row, col)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # Default light mode
    ctk.set_default_color_theme("blue")
    app = SudokuApp()
    app.mainloop()
