import time
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Принудительно используем Tkinter-бэкенд
import os
import webbrowser
from pyvis.network import Network
from tkinter import messagebox


class CiscoVisualizer:
    def __init__(self, devices, connections):
        """
        Инициализация визуализатора Cisco-топологии

        :param devices: Список устройств (например, ["Роутер", "Умная колонка"])
        :param connections: Список соединений в формате
               [(device1, device2, protocol, bandwidth), ...]
        """
        self.devices = devices
        self.connections = connections
        self.net = self._initialize_network()

    def _initialize_network(self):
        """Настройка базовых параметров сети"""
        return Network(
            height="800px",
            width="100%",
            bgcolor="#f0f0f0",  # Cisco-style background
            font_color="#333333",
            directed=False,
            notebook=False
        )

    def _get_device_properties(self, device):
        """Определяем иконки и цвета для разных типов устройств"""
        device_props = {
            "роутер": {
                "image": "https://img.icons8.com/color/48/router.png",
                "color": "#0066CC",
                "shape": "image"
            },
            "смартфон": {
                "image": "https://img.icons8.com/color/48/iphone.png",
                "color": "#33CC33",
                "shape": "image"
            },
            "лампочка": {
                "image": "https://img.icons8.com/color/48/light-on.png",
                "color": "#FFCC00",
                "shape": "image"
            },
            "розетка": {
                "image": "https://img.icons8.com/color/48/electrical.png",
                "color": "#CC3300",
                "shape": "image"
            },
            "колонка": {
                "image": "https://img.icons8.com/color/48/speaker.png",
                "color": "#9933CC",
                "shape": "image"
            }
        }

        for key, props in device_props.items():
            if key in device.lower():
                return props

        # Дефолтные значения для неизвестных устройств
        return {
            "color": "#666666",
            "shape": "box"
        }

    def _add_devices(self):
        """Добавление устройств с соответствующими иконками"""
        for device in self.devices:
            props = self._get_device_properties(device)
            self.net.add_node(
                device,
                shape=props["shape"],
                image=props.get("image", ""),
                color=props["color"],
                size=25,
                borderWidth=2,
                font={"size": 12},
                labelHighlightBold=True
            )

    def _add_connections(self):
        """Добавление соединений с подписями"""
        protocol_styles = {
            "wi-fi": {"color": "#FF8800", "dashes": False},
            "zigbee": {"color": "#00CC66", "dashes": [5, 5]},
            "bluetooth": {"color": "#9966FF", "dashes": [3, 3]},
            "ethernet": {"color": "#333333", "dashes": False}
        }

        for src, dst, proto, bw in self.connections:
            style = protocol_styles.get(proto.lower(), {"color": "#AAAAAA"})
            self.net.add_edge(
                src,
                dst,
                label=f"{proto.upper()} {bw}Mbps",
                color=style["color"],
                width=2,
                dashes=style.get("dashes", False),
                font={"size": 10},
                smooth=False
            )

    def _configure_physics(self):
        """Настройка физической модели (аналогично Cisco Packet Tracer)"""
        self.net.toggle_physics(True)
        self.net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 150,
                    "damping": 0.4,
                    "avoidOverlap": 0.8
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            },
            "nodes": {
                "scaling": {
                    "min": 20,
                    "max": 30
                }
            }
        }
        """)

    def generate(self, filename="cisco_topology.html"):
        """
        Генерация и отображение топологии

        :param filename: Имя выходного HTML-файла
        :return: Путь к сохраненному файлу
        """
        try:
            if not self.devices:
                raise ValueError("Нет устройств для визуализации")
            if not self.connections:
                raise ValueError("Нет соединений между устройствами")

            self._add_devices()
            self._add_connections()
            self._configure_physics()

            # Очистка предыдущего файла
            if os.path.exists(filename):
                os.remove(filename)

            # Сохранение и открытие
            self.net.show(filename)
            filepath = os.path.abspath(filename)
            webbrowser.open(f"file://{filepath}")

            return filepath

        except Exception as e:
            messagebox.showerror(
                "Ошибка визуализации",
                f"Не удалось создать топологию:\n{str(e)}\n\n"
                "Проверьте:\n"
                "1. Наличие устройств и соединений\n"
                "2. Корректность данных\n"
                "3. Доступ к интернету (для загрузки иконок)"
            )
            return None

    def highlight_path(self, path, color="#FF0000", width=5):
        """
        Подсветка указанного пути в топологии

        :param path: Список устройств пути (например, ["Роутер", "Смартфон"])
        :param color: Цвет подсветки
        :param width: Толщина линии
        """
        for i in range(len(path) - 1):
            edge = f"{path[i]}->{path[i + 1]}"
            if edge in self.net.edges:
                self.net.edges[edge]["color"] = color
                self.net.edges[edge]["width"] = width

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

        self._create_cisco_button()

    def _create_cisco_button(self):
        """Создает кнопку для визуализации Cisco"""
        style = ttk.Style()
        style.configure("Cisco.TButton",
                        foreground="white",
                        background="#0066CC",
                        font=('Helvetica', 10, 'bold'),
                        padding=5)

        self.cisco_btn = ttk.Button(
            self.frame_input,
            text="Cisco Visualization",
            command=self._show_cisco_visualization,
            style="Cisco.TButton",
            state="normal"
        )
        self.cisco_btn.grid(row=4, column=4, padx=5, pady=5, sticky="ew")

    def _show_cisco_visualization(self):
        """Генерация Cisco-подобной визуализации с полной обработкой ошибок"""
        try:
            # Проверка данных
            if not hasattr(self, 'devices') or not self.devices:
                raise ValueError("Не добавлены устройства")

            if not hasattr(self, 'connections') or not self.connections:
                raise ValueError("Не добавлены соединения")

            # Импорт библиотек (с проверкой)
            try:
                from pyvis.network import Network
            except ImportError:
                raise ImportError("Библиотека PyVis не установлена. Выполните: pip install pyvis")

            # Подготовка файла
            output_file = os.path.abspath("cisco_topology.html")
            temp_file = os.path.abspath("temp_cisco_topology.html")

            # Удаляем старые файлы
            for filepath in [output_file, temp_file]:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        print(f"Ошибка удаления файла {filepath}: {str(e)}")

            # Создаем сеть
            net = Network(
                height="800px",
                width="100%",
                bgcolor="#f0f0f0",
                font_color="#333333",
                notebook=False,
                cdn_resources="remote"
            )

            # Добавляем устройства
            device_types = {
                "роутер": {"color": "#0066CC", "shape": "box"},
                "смартфон": {"color": "#33CC33", "shape": "ellipse"},
                "лампочка": {"color": "#FFCC00", "shape": "circle"},
                "розетка": {"color": "#CC3300", "shape": "database"},
                "колонка": {"color": "#9933CC", "shape": "triangle"}
            }

            for device in self.devices:
                device_lower = device.lower()
                props = next(
                    (v for k, v in device_types.items() if k in device_lower),
                    {"color": "#666666", "shape": "dot"}
                )
                net.add_node(
                    device,
                    color=props["color"],
                    shape=props["shape"],
                    size=25,
                    font={"size": 12}
                )

            # Добавляем соединения
            for src, dst, proto, bw in self.connections:
                net.add_edge(
                    src,
                    dst,
                    label=f"{proto} {bw}Mbps",
                    color=self._get_protocol_color(proto),
                    width=2
                )

            # Сохраняем во временный файл
            net.save_graph(temp_file)

            # Проверяем создание файла
            if not os.path.exists(temp_file):
                raise RuntimeError("Не удалось создать файл визуализации")

            # Переименовываем (чтобы избежать проблем с кэшированием)
            os.rename(temp_file, output_file)

            # Открываем в браузере
            webbrowser.open(f"file://{output_file}")

        except Exception as e:
            messagebox.showerror(
                "Ошибка визуализации",
                f"Произошла ошибка:\n\n{str(e)}\n\n"
                "Рекомендуемые действия:\n"
                "1. Проверьте наличие устройств и соединений\n"
                "2. Установите PyVis: pip install --upgrade pyvis\n"
                "3. Проверьте права на запись в текущую директорию"
            )

    def _get_protocol_color(self, protocol):
        """Возвращает цвет для разных протоколов"""
        protocol = protocol.lower()
        return {
            "wi-fi": "#FF8800",
            "zigbee": "#00CC66",
            "bluetooth": "#9966FF",
            "ethernet": "#333333"
        }.get(protocol, "#AAAAAA")
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