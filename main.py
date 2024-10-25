import tkinter as tk
from scripts.UI import GridApp

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    app.canvas.create_line(0, 0, 600, 400)  # Optional grid drawing for visual alignment
    root.mainloop()

