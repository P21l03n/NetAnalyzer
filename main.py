import json
import time
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Принудительно используем Tkinter-бэкенд
import os
import webbrowser
import time
from tkinter import messagebox
from pyvis.network import Network
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class CiscoVisualizer:
    def __init__(self, devices, connections):
        """
        Улучшенный визуализатор сетевой топологии с функциями:
        - Подсветка критических путей
        - Экспорт в PNG
        - Имитация трафика

        :param devices: Список устройств ["Роутер", "Умная колонка"]
        :param connections: Список соединений [(src, dst, proto, bw), ...]
        """
        self.devices = devices
        self.connections = connections
        self.net = self._initialize_network()
        self.highlighted_paths = []
        self.traffic_animation = False

    def _initialize_network(self):
        """Инициализация сети с настройками Cisco"""
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#f5f5f5",
            font_color="#333",
            notebook=False,
            cdn_resources='remote'
        )
        net.toggle_physics(True)
        return net

    def _get_device_properties(self, device):
        """Определение свойств устройства по его типу"""
        device_props = {
            "роутер": {
                "image": "https://img.icons8.com/color/48/router.png",
                "color": "#0066CC",
                "shape": "image",
                "size": 30
            },
            "смартфон": {
                "image": "https://img.icons8.com/color/48/iphone.png",
                "color": "#33CC33",
                "shape": "image",
                "size": 25
            },
            "лампочка": {
                "image": "https://img.icons8.com/color/48/light-on.png",
                "color": "#FFCC00",
                "shape": "image",
                "size": 20
            },
            "розетка": {
                "image": "https://img.icons8.com/color/48/electrical.png",
                "color": "#CC3300",
                "shape": "image",
                "size": 20
            },
            "колонка": {
                "image": "https://img.icons8.com/color/48/speaker.png",
                "color": "#9933CC",
                "shape": "image",
                "size": 25
            }
        }

        for key, props in device_props.items():
            if key in device.lower():
                return props

        return {
            "color": "#666666",
            "shape": "box",
            "size": 20
        }

    def _get_protocol_style(self, protocol):
        """Стили для разных типов протоколов"""
        return {
            "wi-fi": {"color": "#FF8800", "width": 3},
            "zigbee": {"color": "#00CC66", "width": 2, "dashes": [5, 5]},
            "bluetooth": {"color": "#9966FF", "width": 2},
            "ethernet": {"color": "#333333", "width": 4}
        }.get(protocol.lower(), {"color": "#AAAAAA", "width": 2})

    def generate_topology(self):
        """Генерация базовой топологии с устройствами и соединениями"""
        # Добавление устройств
        for device in self.devices:
            props = self._get_device_properties(device)
            self.net.add_node(
                device,
                shape=props["shape"],
                image=props.get("image", ""),
                color=props["color"],
                size=props["size"],
                borderWidth=2,
                font={"size": 12}
            )

        # Добавление соединений
        for src, dst, proto, bw in self.connections:
            style = self._get_protocol_style(proto)
            self.net.add_edge(
                src,
                dst,
                label=f"{proto.upper()} {bw}Mbps",
                color=style["color"],
                width=style["width"],
                dashes=style.get("dashes", False),
                font={"size": 10}
            )

        # Восстановление подсвеченных путей
        for path, color, width in self.highlighted_paths:
            self._apply_path_highlight(path, color, width)

        return self

    def highlight_path(self, path, color="#FF0000", width=5):
        """
        Подсветка указанного пути в топологии
        :param path: Список устройств ["Роутер", "Смартфон"]
        :param color: Цвет подсветки
        :param width: Толщина линии
        """
        self._apply_path_highlight(path, color, width)
        self.highlighted_paths.append((path, color, width))
        return self

    def _apply_path_highlight(self, path, color, width):
        """Внутренний метод для подсветки пути"""
        for i in range(len(path) - 1):
            edge = f"{path[i]}-{path[i + 1]}"
            if edge in self.net.edges:
                self.net.edges[edge]["color"] = color
                self.net.edges[edge]["width"] = width
                self.net.edges[edge]["shadow"] = True

    def generate(self, filename="cisco_topology.html", auto_animate=False, animation_path=None):
        """
        Генерация топологии с возможностью автозапуска анимации
        :param auto_animate: Автоматически запускать анимацию
        :param animation_path: Путь для анимации (например, ["Роутер", "Смартфон"])
        """
        try:
            # Генерируем базовую топологию
            self.generate_topology()

            # Настраиваем физику для плавной анимации
            self.net.toggle_physics(True)
            options = {
                "physics": {
                    "enabled": True,
                    "stabilization": {
                        "enabled": True,
                        "iterations": 100,
                        "updateInterval": 25
                    },
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 200,
                        "springConstant": 0.04,
                        "damping": 0.09,
                        "avoidOverlap": 0.1
                    }
                }
            }
            self.net.set_options(options)

            # Добавляем JavaScript для автоматической анимации
            if auto_animate and animation_path:
                self._add_animation_script(animation_path)

            if os.path.exists(filename):
                os.remove(filename)

            self.net.show(filename)
            return os.path.abspath(filename)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return None

    def _add_animation_script(self, path):
        """Добавляем JavaScript код для анимации"""
        # Преобразуем путь в JavaScript-массив
        js_path = str([str(device) for device in path])

        animation_js = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Ждем загрузки визуализации
            setTimeout(function() {{
                const path = {js_path};
                animateSignal(path);
            }}, 2000);

            function animateSignal(path) {{
                // Реализация анимации на JavaScript
                const edges = network.body.data.edges;
                const originalColors = {{}};

                // Сохраняем оригинальные цвета
                for (let i = 0; i < path.length - 1; i++) {{
                    const edgeId = `${{path[i]}}->${{path[i + 1]}}`;
                    const edge = edges.get(edgeId);
                    if (edge) {{
                        originalColors[edgeId] = edge.color;
                    }}
                }}

                // Анимация (3 цикла)
                let cycles = 0;
                const animationInterval = setInterval(function() {{
                    // Вперед
                    for (let i = 0; i < path.length - 1; i++) {{
                        const edgeId = `${{path[i]}}->${{path[i + 1]}}`;
                        if (edges.get(edgeId)) {{
                            edges.update({{
                                id: edgeId,
                                color: {{highlight: '#FF0000', hover: '#FF0000'}},
                                width: 5
                            }});
                        }}
                    }}

                    // Обратно
                    setTimeout(function() {{
                        for (let i = 0; i < path.length - 1; i++) {{
                            const edgeId = `${{path[i]}}->${{path[i + 1]}}`;
                            if (edges.get(edgeId)) {{
                                edges.update({{
                                    id: edgeId,
                                    color: originalColors[edgeId],
                                    width: 2
                                }});
                            }}
                        }}

                        cycles++;
                        if (cycles >= 3) clearInterval(animationInterval);
                    }}, 500);
                }}, 1000);
            }}
        }});
        </script>
        """
        self.net.template = self.net.template.replace("</body>", f"{animation_js}</body>")
    def show(self):
        """Отображение топологии в браузере"""
        output_file = "cisco_topology.html"

        # Удаляем старый файл если есть
        if os.path.exists(output_file):
            os.remove(output_file)

        # Генерируем и открываем
        self.net.save_graph(output_file)
        webbrowser.open(f"file://{os.path.abspath(output_file)}")

        return output_file
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