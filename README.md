# GUI-Sudoku-with-Solver
This is a GUI sudoku solver using the backtracking algorithm.

Run GUI.py to play sudoku.

# How to Play
Click a box and hit the number on your keybaord to enter a number. It will validate if that value is correct or not. To delete a entered value use Delete. Finally to solve the board click "Solve", sit back and watch the algorithm run.


# Build InstructionsUsing PyInstaller
```
pyinstaller -F gui.py --collect-all customtkinter -w
```