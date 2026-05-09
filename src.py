import threading
import tkinter as tk
import random
import time

# ========== 排序算法（带 yield，逐步输出中间状态） ==========
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield arr.copy()

def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        yield arr.copy()

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        yield arr.copy()

# ========== 单个排序窗口类 ==========
class SortWindow:
    def __init__(self, root, title, algorithm, data, color):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title(title)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.canvas = tk.Canvas(self.window, width=600, height=400, bg='white')
        self.canvas.pack()

        self.data = data                     # 本窗口的初始乱序数组
        self.generator = algorithm(data)     # 对应算法的生成器
        self.color = color
        self.running = True

        # 启动一个线程专门驱动排序步骤
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def animate(self):
        """后台线程：不断从生成器取下一个状态，交给 GUI 绘制"""
        try:
            while self.running:
                state = next(self.generator)
                self.window.after(0, self.draw, state)
                time.sleep(0.05)            # 控制每步之间的速度
        except StopIteration:
            pass                            # 排序结束，线程自动退出

    def draw(self, arr):
        """在主线程中重绘当前数组的所有条形"""
        self.canvas.delete("all")           # 清空画布
        bar_width = 600 // len(arr)
        for i, val in enumerate(arr):
            x0 = i * bar_width
            y0 = 400
            x1 = i * bar_width + bar_width - 2
            y1 = 400 - val
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=self.color,
                outline=""
            )

    def close(self):
        """关闭窗口时停止线程并销毁窗口"""
        self.running = False
        self.window.destroy()

# ========== 主程序 ==========
if __name__ == "__main__":
    # 1. 创建一个隐藏的根窗口（Tk要求有一个主窗口）
    root = tk.Tk()
    root.withdraw()

    # 2. 生成一份乱序数组，每个算法窗口拷贝一份（互不干扰）
    SIZE = 30
    original = [random.randint(10, 300) for _ in range(SIZE)]

    # 3. 创建三个独立窗口，分别运行不同排序
    win_bubble = SortWindow(
        root, "冒泡排序 Bubble Sort",
        bubble_sort, original.copy(), "red"
    )
    win_select = SortWindow(
        root, "选择排序 Selection Sort",
        selection_sort, original.copy(), "green"
    )
    win_insert = SortWindow(
        root, "插入排序 Insertion Sort",
        insertion_sort, original.copy(), "blue"
    )

    # 4. 设置窗口位置，避免重叠（根据屏幕尺寸可自行调整）
    win_bubble.window.geometry("600x400+0+0")
    win_select.window.geometry("600x400+620+0")
    win_insert.window.geometry("600x400+1240+0")

    # 5. 进入主事件循环
    root.mainloop()

    # 6. 程序退出后确保所有线程停止（实际上窗口关闭时已经停掉）
    win_bubble.running = False
    win_select.running = False
    win_insert.running = False