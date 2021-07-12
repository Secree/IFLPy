import tkinter as tk

window = tk.Tk()

greeting = tk.Label(text="Playlist ID:")
entry = tk.Entry()

entry.pack()
greeting.pack()

window.mainloop()