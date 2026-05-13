import tkinter as tk
from controllers.main_controller import MainController


def main():
    root = tk.Tk()
    root.title('Kết Quả Học Tập - MVC App')
    root.geometry('1000x600')
    app = MainController(root)
    root.mainloop()


if __name__ == '__main__':
    main()
