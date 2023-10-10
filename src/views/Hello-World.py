# import tkinter as tk

# # Create the main window
# root = tk.Tk()
# root.title("Simple tkinter App")

# # Create a label widget
# label = tk.Label(root, text="Hello, tkinter!")
# label.pack(pady=20, padx=20)  # Add some padding

# def on_button_click():
#     print("Button clicked!")

# button = tk.Button(root, text="Click Me", command=on_button_click)
# button.pack(expand=True)


# def on_enterkey(event):
#     print(entry.get())

# entry = tk.Entry(root)
# entry.bind("<Return>",on_enterkey)
# entry.pack()


# def open_new_window():
#     new_window = tk.Toplevel(root)
#     new_window.title("New Window")
#     label = tk.Label(new_window, text="This is a new window!")
#     label.pack(pady=20, padx=20)

# button = tk.Button(root, text="Open New Window", command=open_new_window)
# button.pack(pady=20, padx=20)


# menu = tk.Menu(root)
# root.config(menu=menu)

# file_menu = tk.Menu(menu)
# menu.add_cascade(label="File", menu=file_menu)
# file_menu.add_separator()
# file_menu.add_command(label="Exit", command=root.quit)


# canvas = tk.Canvas(root, width=400, height=400)
# canvas.pack()

# canvas.create_line(0, 0, 200, 200, fill="red")
# canvas.create_oval(50, 50, 150, 150, fill="blue")
# canvas.create_rectangle(100, 100, 300, 300, fill="green")

# from tkinter import messagebox, filedialog

# # Show an info message box
# messagebox.showinfo("Info", "This is an info message box!")

# # Open a file selection dialog
# filename = filedialog.askopenfilename(title="Select a File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])


# # Run the main loop
# root.mainloop()


import tkinter as tk
from tkinter import ttk

rootWindow = tk.Tk()
rootWindow.title("Layout Title")
rootWindow.geometry("600x600")
frame1 = ttk.Frame(rootWindow)
frame2 = ttk.Frame(frame1)

label1 = ttk.Label(rootWindow, text = "First label", background="red")

#bottom left
label2 = ttk.Label(frame1, text="Label 2", background = "blue")

#bottom right
label3 = ttk.Label(frame2, text = "Last of the labels",background="green")
button = ttk.Button(frame2,text = "Button")

label1.pack(side = "top", expand = True, fill = "both")

#start bottom half
#bottom frame
frame1.pack(side = "bottom", expand= True, fill = "both")

#right side of the bottom frame
frame2.pack(side="right",expand=False,fill="both")

#Put label 2 on the left frame
label2.pack(side = "left", expand = True, fill = "both")

#Put label 3 and button on the bottom right
label3.pack(expand=True,fill="both")
button.pack(expand=True,fill="both")

rootWindow.bind("<Escape>", lambda event: rootWindow.quit())

rootWindow.mainloop()



def isValid(str) -> bool:
    if len(str) % 2 != 0 or str == "":
        return False
    
    dict = {'(':')','{':'}','[':']'}
    stack = []

    for char in str:
        if char in dict:
            stack.append(char)
        else:
            if len(stack) == 0:
                return False
            poppedValue = stack.pop()
            dictValue = dict[poppedValue]
            if dictValue != char:
                return False
            
    return len(stack) == 0

str = "(){}}}{"
print(isValid(str))