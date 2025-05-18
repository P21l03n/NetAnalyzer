import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Принудительно используем Tkinter-бэкенд

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор пропускной способности сети")
        self.devices = []
        self.protocols = ["Wi-Fi", "Zigbee", "Bluetooth", "Ethernet"]
        self.connections = []
        self.performance = {}
        self.bandwidths = {}

        # Основные фреймы
        self.frame_input = ttk.LabelFrame(root, text="Ввод данных", padding=10)
        self.frame_input.pack(padx=10, pady=5, fill=tk.X)

        self.frame_output = ttk.Frame(root, padding=10)
        self.frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Ввод устройств
        ttk.Label(self.frame_input, text="Устройство:").grid(row=0, column=0, sticky=tk.W)
        self.device_entry = ttk.Entry(self.frame_input, width=20)
        self.device_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.frame_input, text="Производительность:").grid(row=0, column=2, sticky=tk.W)
        self.performance_entry = ttk.Entry(self.frame_input, width=10)
        self.performance_entry.grid(row=0, column=3, padx=5)

        self.add_device_btn = ttk.Button(self.frame_input, text="Добавить устройство", command=self.add_device)
        self.add_device_btn.grid(row=0, column=4, padx=5)

        # Ввод соединений
        ttk.Label(self.frame_input, text="Соединение:").grid(row=1, column=0, sticky=tk.W)
        self.device1_combo = ttk.Combobox(self.frame_input, width=15, state="readonly")
        self.device1_combo.grid(row=1, column=1, padx=5)

        ttk.Label(self.frame_input, text="<->").grid(row=1, column=2)
        self.device2_combo = ttk.Combobox(self.frame_input, width=15, state="readonly")
        self.device2_combo.grid(row=1, column=3, padx=5)

        ttk.Label(self.frame_input, text="Протокол:").grid(row=2, column=0, sticky=tk.W)
        self.protocol_combo = ttk.Combobox(self.frame_input, values=self.protocols, width=15, state="readonly")
        self.protocol_combo.grid(row=2, column=1, padx=5)

        ttk.Label(self.frame_input, text="Пропускная способность (Мбит/с):").grid(row=2, column=2, sticky=tk.W)
        self.bandwidth_entry = ttk.Entry(self.frame_input, width=10)
        self.bandwidth_entry.grid(row=2, column=3, padx=5)

        self.add_connection_btn = ttk.Button(self.frame_input, text="Добавить соединение", command=self.add_connection)
        self.add_connection_btn.grid(row=2, column=4, padx=5)

        # Ввод пользователей
        ttk.Label(self.frame_input, text="Количество пользователей:").grid(row=3, column=0, sticky=tk.W)
        self.users_entry = ttk.Entry(self.frame_input, width=10)
        self.users_entry.grid(row=3, column=1, padx=5)

        ttk.Label(self.frame_input, text="Запросов на пользователя:").grid(row=3, column=2, sticky=tk.W)
        self.requests_entry = ttk.Entry(self.frame_input, width=10)
        self.requests_entry.grid(row=3, column=3, padx=5)

        self.calculate_btn = ttk.Button(self.frame_input, text="Рассчитать", command=self.calculate)
        self.calculate_btn.grid(row=3, column=4, padx=5)

        # Вывод результатов
        self.result_label = ttk.Label(self.frame_output, text="Результаты появятся здесь")
        self.result_label.pack()

        self.figure = plt.figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_output)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def add_device(self):
        device = self.device_entry.get()
        performance = self.performance_entry.get()

        if not device or not performance:
            messagebox.showerror("Ошибка", "Введите название устройства и его производительность")
            return

        try:
            performance = float(performance)
        except ValueError:
            messagebox.showerror("Ошибка", "Производительность должна быть числом")
            return

        if device in self.performance:
            messagebox.showerror("Ошибка", "Устройство уже существует")
            return

        self.devices.append(device)
        self.performance[device] = performance
        self.device1_combo['values'] = self.devices
        self.device2_combo['values'] = self.devices

        self.device_entry.delete(0, tk.END)
        self.performance_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Устройство '{device}' добавлено")

    def add_connection(self):
        device1 = self.device1_combo.get()
        device2 = self.device2_combo.get()
        protocol = self.protocol_combo.get()
        bandwidth = self.bandwidth_entry.get()

        if not device1 or not device2 or not protocol or not bandwidth:
            messagebox.showerror("Ошибка", "Заполните все поля соединения")
            return

        if device1 == device2:
            messagebox.showerror("Ошибка", "Устройства должны быть разными")
            return

        try:
            bandwidth = float(bandwidth)
        except ValueError:
            messagebox.showerror("Ошибка", "Пропускная способность должна быть числом")
            return

        connection = (device1, device2, protocol, bandwidth)
        reverse_connection = (device2, device1, protocol, bandwidth)

        if connection in self.connections or reverse_connection in self.connections:
            messagebox.showerror("Ошибка", "Такое соединение уже существует")
            return

        self.connections.append(connection)
        self.bandwidths[(device1, device2)] = bandwidth
        self.bandwidths[(device2, device1)] = bandwidth

        self.bandwidth_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Соединение {device1} <-> {device2} добавлено")

    def calculate(self):
        if not self.devices:
            messagebox.showerror("Ошибка", "Добавьте хотя бы одно устройство")
            return

        if not self.connections:
            messagebox.showerror("Ошибка", "Добавьте хотя бы одно соединение")
            return

        try:
            num_users = int(self.users_entry.get())
            requests_per_user = int(self.requests_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа для пользователей и запросов")
            return

        # Расчет общей пропускной способности
        total_bandwidth = sum(bw for bw in self.bandwidths.values()) / 2
        self.result_label.config(text=f"Общая пропускная способность сети: {total_bandwidth:.2f} Мбит/с")

        # Расчет нагрузки
        total_performance = sum(self.performance.values())
        total_requests = num_users * requests_per_user
        load_distribution = {
            device: total_requests * (self.performance[device] / total_performance)
            for device in self.devices
        }

        # Построение графика
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        devices = list(load_distribution.keys())
        loads = list(load_distribution.values())
        
        bars = ax.bar(devices, loads, color='skyblue')
        ax.set_xlabel('Устройства')
        ax.set_ylabel('Нагрузка (запросы/сек)')
        ax.set_title(f'Распределение нагрузки для {num_users} пользователей')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
        
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()