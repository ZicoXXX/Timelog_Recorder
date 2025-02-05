import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import time
import json
import os

DATA_FILE = "records.json"
PIC_FOLDER = "pic"  # 图片存放的文件夹

class WorkTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("zico的工时记录")
        self.root.geometry("800x600")

        self.projects = self.load_data()
        self.current_project = None
        self.start_time = None
        self.project_image = None

        # 创建 pic 文件夹（如果不存在）
        if not os.path.exists(PIC_FOLDER):
            os.makedirs(PIC_FOLDER)

        # 主框架
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # 左侧图片显示区域
        self.image_label = tk.Label(self.main_frame, bg="gray", width=100, height=100)
        self.image_label.grid(row=0, column=0, rowspan=6, padx=10, sticky="n")

        # 右侧按钮区域
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="n")

        self.label = tk.Label(self.right_frame, text="请选择项目", font=("Arial", 14))
        self.label.pack(pady=10)

        self.project_var = tk.StringVar(value="请选择项目")
        self.project_menu = tk.OptionMenu(self.right_frame, self.project_var, "请选择项目", command=self.select_project)
        self.project_menu.pack(pady=5)

        self.new_project_button = tk.Button(self.right_frame, text="新建项目", command=self.new_project)
        self.new_project_button.pack(pady=5)
        self.export_button = tk.Button(self.right_frame, text="导出项目数据", command=self.export_project,
                                       state=tk.DISABLED)
        self.export_button.pack(pady=5)

        self.start_button = tk.Button(self.right_frame, text="开始", command=self.start_timer, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.right_frame, text="结束", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.export_button = tk.Button(self.right_frame, text="导出项目数据", command=self.export_project, state=tk.DISABLED)
        self.export_button.pack(pady=5)

        self.delete_project_button = tk.Button(self.right_frame, text="删除项目", command=self.delete_project, state=tk.DISABLED)
        self.delete_project_button.pack(pady=5)

        self.update_project_menu()

    def load_data(self):
        """加载项目数据"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        """保存项目数据"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.projects, f, indent=4, ensure_ascii=False)

    def update_project_menu(self):
        """更新项目选择菜单"""
        menu = self.project_menu["menu"]
        menu.delete(0, "end")

        for project_name in self.projects:
            menu.add_command(label=project_name, command=tk._setit(self.project_var, project_name, self.select_project))

        menu.add_command(label="请选择项目", command=tk._setit(self.project_var, "请选择项目", self.select_project))

        if self.projects:
            first_project = list(self.projects.keys())[0]
            self.project_var.set(first_project)
            self.select_project(first_project)

    def select_project(self, project_name):
        """选择项目后更新状态"""
        if project_name == "请选择项目":
            return

        self.current_project = project_name
        self.start_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)
        self.delete_project_button.config(state=tk.NORMAL)

        self.display_project_image()

    def new_project(self):
        """新建项目"""
        project_name = simpledialog.askstring("新建项目", "输入项目名称:")
        if project_name:
            if project_name in self.projects:
                messagebox.showwarning("警告", "该项目已存在！")
                return

            total_cost = simpledialog.askfloat("项目费用", "输入该项目的总费用 (元):")
            if total_cost is None:
                return

            # 选择图片
            image_path = filedialog.askopenfilename(title="选择项目图片", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
            if image_path:
                # 压缩图片并保存到 pic 文件夹
                image_filename = f"{project_name}.png"  # 保存为 PNG 格式
                image_save_path = os.path.join(PIC_FOLDER, image_filename)
                self.save_compressed_image(image_path, image_save_path)

            # 新建项目并保存
            self.projects[project_name] = {
                "total_cost": total_cost,
                "time_records": [],
                "image_path": image_save_path  # 存储图片的相对路径
            }
            self.save_data()

            # 更新 OptionMenu
            self.update_project_menu()

            # 自动选择新创建的项目
            self.select_project(project_name)

    def save_compressed_image(self, image_path, save_path):
        """压缩图片并保存到指定路径"""
        image = Image.open(image_path)
        image = image.resize((100, 100), Image.Resampling.LANCZOS)  # 压缩为 512x512
        image.save(save_path)  # 保存到 pic 文件夹

    def display_project_image(self):
        """显示项目的图片"""
        if self.current_project and self.projects.get(self.current_project):
            image_path = self.projects[self.current_project].get("image_path")
            if image_path:
                image = Image.open(image_path)
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                image = ImageTk.PhotoImage(image)
                self.image_label.config(image=image)
                self.image_label.image = image  # 防止图片被垃圾回收

    def delete_project(self):
        """删除项目"""
        if self.current_project:
            confirm = messagebox.askyesno("删除项目", f"你确定要删除 '{self.current_project}' 吗？")
            if confirm:
                # 删除项目文件夹中的图片
                image_path = self.projects[self.current_project].get("image_path")
                if os.path.exists(image_path):
                    os.remove(image_path)

                # 删除项目
                del self.projects[self.current_project]
                self.save_data()  # 保存删除后的数据

                # 更新 OptionMenu 和项目选择
                self.update_project_menu()

                # 如果删除的是当前选择的项目，则清空当前项目
                self.current_project = None
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
                self.export_button.config(state=tk.DISABLED)
                self.delete_project_button.config(state=tk.DISABLED)

                # 更新界面
                self.label.config(text="请选择项目")
                self.image_label.config(image=None)  # 清除图片
                messagebox.showinfo("删除成功", "项目已删除")

    def start_timer(self):
        """开始计时"""
        if self.current_project:
            self.start_time = time.time()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.label.config(text=f"正在记录: {self.current_project}")

    def stop_timer(self):
        """停止计时并保存数据"""
        if self.current_project and self.start_time:
            elapsed_time = round((time.time() - self.start_time) / 3600, 2)
            self.projects[self.current_project]["time_records"].append(elapsed_time)
            self.save_data()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.label.config(text=f"项目 {self.current_project} 记录时间: {elapsed_time} 小时")
            self.start_time = None

    def export_project(self):
        """导出当前选中项目的所有数据到 TXT 文件"""
        if not self.current_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return

        project_data = self.projects.get(self.current_project, {})
        if not project_data:
            messagebox.showwarning("警告", "该项目没有可导出的数据")
            return

        # 让用户选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")],
            title="导出项目数据",
            initialfile=f"{self.current_project}.txt"
        )

        if not file_path:  # 用户取消选择
            return

        # 写入项目数据
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"项目名称: {self.current_project}\n")
            f.write(f"总费用: {project_data.get('total_cost', 0)} 元\n")
            f.write("时间记录（小时）:\n")
            for i, record in enumerate(project_data.get("time_records", []), 1):
                f.write(f"{i}. {record} 小时\n")

        messagebox.showinfo("导出成功", f"项目 '{self.current_project}' 数据已导出到:\n{file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WorkTimerApp(root)
    root.mainloop()
