import threading
import tkinter as tk
import random
import time

# ==================== 排序算法（带高亮信息） ====================
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            # 1. 比较前：高亮 j 和 j+1 为“比较中”
            yield arr.copy(), [j, j+1], []

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                # 2. 交换后：高亮 j 和 j+1 为“刚交换”
                yield arr.copy(), [], [j, j+1]
    # 全部完成，返回空高亮（外部会处理完成状态）
    yield arr.copy(), [], []

def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            # 1. 每次比较：高亮 j 和当前最小值 min_idx
            yield arr.copy(), [j, min_idx], []

            if arr[j] < arr[min_idx]:
                min_idx = j
                # 更新最小值候选时也可以给个提示（可选）
                # yield arr.copy(), [], [min_idx]
        # 2. 一轮结束，交换 i 和 min_idx（如果不同）
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            yield arr.copy(), [], [i, min_idx]
    yield arr.copy(), [], []

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # 1. 移动前，高亮当前位置 i（待插入元素）和 j（比较起始）
        yield arr.copy(), [i, j], []

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            # 2. 移动后：高亮 j 和 j+1（被移动的位置）
            yield arr.copy(), [], [j, j+1]
            j -= 1
            # 3. 继续比较，高亮新的 j 位置
            if j >= 0:
                yield arr.copy(), [j, j+1], []

        arr[j + 1] = key
        # 4. 插入完成，高亮插入位置 j+1
        yield arr.copy(), [], [j+1]
    yield arr.copy(), [], []

# ==================== 单个排序窗口类 ====================
class SortWindow:
    def __init__(self, root, title, algorithm, data, color):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title(title)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.canvas = tk.Canvas(self.window, width=600, height=400, bg='white')
        self.canvas.pack()

        self.data = data
        self.generator = algorithm(data)
        self.color = color          # 基础条形颜色
        self.running = True

        # 启动后台线程
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def animate(self):
        """后台线程：不断从生成器取出状态并交给主线程绘制"""
        try:
            while self.running:
                arr, active, swapped = next(self.generator)
                self.window.after(0, self.draw, arr, active, swapped)
                time.sleep(0.08)    # 速度可调，比之前稍慢以便看清高亮
        except StopIteration:
            # 排序结束时 data 已经是完全有序的，触发最终绘制
            self.window.after(0, self.draw_completed)

    def draw(self, arr, active, swapped):
        """在主线程中绘制数组，高亮 active 和 swapped 中的索引"""
        self.canvas.delete("all")
        bar_width = 600 // len(arr)

        for i, val in enumerate(arr):
            x0 = i * bar_width
            y0 = 400
            x1 = i * bar_width + bar_width - 2
            y1 = 400 - val

            # 确定当前条形的颜色
            if i in active:
                fill = "yellow"          # 正在比较
            elif i in swapped:
                fill = "orange"          # 刚交换/移动
            else:
                fill = self.color        # 默认算法颜色

            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=fill,
                outline=""
            )

    def draw_completed(self):
        """排序完成后，将所有条形变成绿色"""
        self.canvas.delete("all")
        bar_width = 600 // len(self.data)
        for i, val in enumerate(self.data):
            x0 = i * bar_width
            y0 = 400
            x1 = i * bar_width + bar_width - 2
            y1 = 400 - val
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill="lightgreen",
                outline=""
            )
        self.window.title(self.window.title() + " （已完成）")

    def close(self):
        self.running = False
        self.window.destroy()

# ==================== 主程序 ====================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    SIZE = 30
    original = [random.randint(10, 300) for _ in range(SIZE)]

    # 创建三个独立窗口
    win_bubble = SortWindow(
        root, "冒泡排序 Bubble Sort",
        bubble_sort, original.copy(), "tomato"
    )
    win_select = SortWindow(
        root, "选择排序 Selection Sort",
        selection_sort, original.copy(), "dodgerblue"
    )
    win_insert = SortWindow(
        root, "插入排序 Insertion Sort",
        insertion_sort, original.copy(), "mediumpurple"
    )

    # 窗口布局（根据屏幕尺寸可自行调整）
    win_bubble.window.geometry("600x400+50+50")
    win_select.window.geometry("600x400+700+50")
    win_insert.window.geometry("600x400+1350+50")

    root.mainloop()

    # 确保线程停止
    win_bubble.running = False
    win_select.running = False
    win_insert.running = False