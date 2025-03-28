import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
from pynput import keyboard
import threading

# 禁用pyautogui的FAILSAFE功能
pyautogui.FAILSAFE = False

class ClickerApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.click_count = 0
        self.start_time = 0
        
        # 创建主界面
        root.title("鼠标连点器 v1.1")
        root.geometry("480x850")
        root.resizable(False, False)  # 禁止调整窗口大小
        
        # 设置主题样式
        style = ttk.Style()
        # 设置整体背景色
        root.configure(background="#f5f5f7")
        style.configure("TFrame", background="#f5f5f7")
        style.configure("TLabel", background="#f5f5f7", font=("微软雅黑", 9))
        style.configure("TButton", font=("微软雅黑", 9))
        style.configure("TRadiobutton", background="#f5f5f7", font=("微软雅黑", 9))
        style.configure("TEntry", font=("微软雅黑", 9))
        
        # 设置标签框样式
        style.configure("TLabelframe", background="#f5f5f7", font=("微软雅黑", 9, "bold"))
        style.configure("TLabelframe.Label", background="#f5f5f7", foreground="#333333", font=("微软雅黑", 10, "bold"))
        
        # 设置按钮样式
        style.configure("TButton", background="#000000", foreground="#ffffff")
        style.map("TButton", background=[("active", "#333333")])
        
        # 设置添加/清空坐标按钮的特殊样式
        style.configure("Coord.TButton", background="#000000", foreground="#ff9900")
        style.map("Coord.TButton", background=[("active", "#333333")])
        
        # 设置状态标签样式
        style.configure("Status.TLabel", font=("微软雅黑", 9, "bold"), background="#f5f5f7")
        style.configure("Header.TLabel", font=("微软雅黑", 10, "bold"), background="#f5f5f7")
        
        # 设置开始按钮的特殊样式
        style.configure("Start.TButton", background="#ff0000", foreground="#ff0000")
        style.map("Start.TButton", background=[["active", "#cc0000"]])
        
        # 参数设置区
        self.create_widgets()
        
        # 热键监听
        self.listener = keyboard.Listener(
            on_press=self.on_key_press)
        self.listener.start()
            
    def on_key_press(self, key):
        try:
            # 检查是否按下F6键
            if key == keyboard.Key.f6:
                # 使用after方法确保在主线程中执行UI操作
                self.root.after(0, self.toggle_start_stop)
        except Exception as e:
            print(f"热键处理错误: {str(e)}")

    def create_widgets(self):
        # 创建主容器
        main_container = ttk.Frame(self.root, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 1. 参数设置区域
        param_frame = ttk.LabelFrame(main_container, text="参数设置", padding=10)
        param_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 点击间隔
        interval_frame = ttk.Frame(param_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        ttk.Label(interval_frame, text="点击间隔（秒）:", width=15).pack(side=tk.LEFT)
        self.interval = ttk.Entry(interval_frame, width=10)
        self.interval.insert(0, "1")
        self.interval.pack(side=tk.LEFT, padx=5)

        # 持续时间
        duration_frame = ttk.Frame(param_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        ttk.Label(duration_frame, text="持续时间（秒）:", width=15).pack(side=tk.LEFT)
        self.duration = ttk.Entry(duration_frame, width=10)
        self.duration.insert(0, "1000")  # 默认值为1000秒
        self.duration.pack(side=tk.LEFT, padx=5)
        
        # 添加无限时间复选框
        self.infinite_var = tk.BooleanVar(value=True)
        self.infinite_check = ttk.Checkbutton(duration_frame, text="无限时间", 
                                            variable=self.infinite_var,
                                            command=self.toggle_duration_entry)
        self.infinite_check.pack(side=tk.LEFT, padx=5)
        self.toggle_duration_entry()

        # 鼠标按键选择
        button_frame = ttk.Frame(param_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Label(button_frame, text="鼠标按键:", width=15).pack(side=tk.LEFT)
        self.btn_var = tk.StringVar(value="left")
        ttk.Radiobutton(button_frame, text="左键", variable=self.btn_var, 
                       value="left").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(button_frame, text="右键", variable=self.btn_var,
                       value="right").pack(side=tk.LEFT)
        
        # 2. 坐标设置区域
        coord_frame = ttk.LabelFrame(main_container, text="坐标设置", padding=10)
        coord_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 坐标输入
        input_frame = ttk.Frame(coord_frame)
        input_frame.pack(fill=tk.X, pady=5)
        ttk.Label(input_frame, text="坐标(x,y):", width=10).pack(side=tk.LEFT)
        self.coord_entry = ttk.Entry(input_frame)
        self.coord_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 坐标操作按钮
        btn_frame = ttk.Frame(coord_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.add_btn = ttk.Button(btn_frame, text="添加坐标", command=self.add_coordinate, style="Coord.TButton")
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_btn = ttk.Button(btn_frame, text="清空坐标", command=self.clear_coordinates, style="Coord.TButton")
        self.clear_btn.pack(side=tk.LEFT)
        
        # 坐标列表框架
        list_frame = ttk.Frame(coord_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 坐标列表 - 美化列表框
        self.coord_listbox = tk.Listbox(list_frame, height=6, yscrollcommand=scrollbar.set,
                                     font=("微软雅黑", 9), bg="#ffffff", fg="#333333",
                                     selectbackground="#4a86e8", selectforeground="#ffffff",
                                     relief=tk.FLAT, borderwidth=1, highlightthickness=1,
                                     highlightcolor="#4a86e8", highlightbackground="#dddddd")
        self.coord_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.coord_listbox.yview)
        
        # 3. 状态和控制区域
        status_frame = ttk.LabelFrame(main_container, text="状态和控制", padding=10)
        status_frame.pack(fill=tk.X)
        
        # 状态显示
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.status = ttk.Label(info_frame, text="状态: 等待开始", foreground="blue", style="Status.TLabel")
        self.status.pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(info_frame, text="点击次数: 0", style="Status.TLabel")
        self.count_label.pack(side=tk.RIGHT)
        
        # 控制按钮
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="开始 (F6)", 
                                  command=self.toggle_start_stop, width=20, style="Start.TButton")
        self.start_btn.pack(pady=5)

    def toggle_duration_entry(self):
        """切换持续时间输入框的可用状态"""
        if self.infinite_var.get():
            self.duration.delete(0, tk.END)
            self.duration.config(state="disabled")
        else:
            self.duration.config(state="normal")
            if not self.duration.get():
                self.duration.insert(0, "1000")
                
    def toggle_start_stop(self):
        if not self.running:
            try:
                interval = float(self.interval.get())
                duration = "" if self.infinite_var.get() else self.duration.get()
                if interval <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "请输入有效的点击间隔数字")
                return
            
            # 先设置状态，再启动线程
            self.running = True
            self.start_time = time.time()
            self.click_count = 0
            self.start_btn.config(text="停止 (F6)")
            self.status.config(text="状态: 运行中", foreground="green")
            
            # 创建并启动线程，设置为守护线程
            click_thread = threading.Thread(target=self.auto_click, daemon=True)
            click_thread.start()
        else:
            # 停止时，先更新状态变量，线程会自行检测并退出
            self.running = False
            self.start_btn.config(text="开始 (F6)")
            self.status.config(text="状态: 已停止", foreground="red")

    def auto_click(self):
        interval = float(self.interval.get())
        duration = self.duration.get()
        
        # 检查持续时间是否为空或非数字
        try:
            end_time = time.time() + float(duration) if duration and duration.strip() else float('inf')
        except ValueError:
            end_time = float('inf')
            self.root.after(0, lambda: messagebox.showinfo("提示", "持续时间设置无效，将无限点击直到手动停止"))
        
        # 添加一个小延迟，确保UI更新完成
        time.sleep(0.1)
        
        # 确保线程不会立即退出
        click_error_count = 0  # 错误计数器
        current_coord_index = 0
        coord_list = [self.coord_listbox.get(i) for i in range(self.coord_listbox.size())]
        
        while self.running and time.time() < end_time:
            try:
                # 如果有坐标列表，则轮流点击每个坐标
                if coord_list:
                    x, y = map(int, coord_list[current_coord_index].split(','))
                    pyautogui.click(x, y, button=self.btn_var.get())
                    current_coord_index = (current_coord_index + 1) % len(coord_list)
                else:
                    # 没有坐标时使用当前位置点击
                    pyautogui.click(button=self.btn_var.get())
                
                self.click_count += 1
                # 使用线程安全的方式更新UI
                self.root.after(0, self.update_count)
                # 等待指定的间隔时间
                time.sleep(interval)
                # 重置错误计数
                click_error_count = 0
            except Exception as e:
                click_error_count += 1
                print(f"点击错误: {str(e)}")
                # 只有连续错误超过3次才显示错误消息并退出
                if click_error_count >= 3:
                    self.root.after(0, lambda e=e: messagebox.showerror("错误", f"点击过程中出错: {str(e)}"))
                    break
                # 短暂暂停后继续尝试
                time.sleep(0.5)
        
        # 只有在线程正常结束时才更新状态
        if self.running:
            self.running = False
            self.root.after(0, lambda: self.start_btn.config(text="开始 (F6)"))
            self.root.after(0, lambda: self.status.config(text="状态: 已完成", foreground="blue"))

    def add_coordinate(self):
        """添加坐标到列表"""
        coord_str = self.coord_entry.get()
        if not coord_str:
            messagebox.showwarning("警告", "请输入坐标")
            return
            
        try:
            # 验证坐标格式
            x, y = map(int, coord_str.split(','))
            self.coord_listbox.insert(tk.END, f"{x},{y}")
            self.coord_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("错误", "坐标格式不正确，请使用x,y格式")
    
    def clear_coordinates(self):
        """清空坐标列表"""
        self.coord_listbox.delete(0, tk.END)
    
    def update_count(self):
        self.count_label.config(text=f"点击次数: {self.click_count}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClickerApp(root)
    root.mainloop()