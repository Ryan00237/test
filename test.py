import psutil
import threading
import time
import datetime
import subprocess
from collections import defaultdict


class PerformanceMonitor:
    def __init__(self, keywords, file_path):
        self.keywords = keywords
        self.file_path = file_path
        self.stop_flag = False
        self.data = defaultdict(list)

    def start(self):
        self.thread = threading.Thread(target=self.collect_data)
        self.thread.start()

    def collect_data(self):
        while not self.stop_flag:
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
                for keyword in self.keywords:
                    if keyword.lower() in proc.info['name'].lower():
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cpu = round(proc.info['cpu_percent'] / psutil.cpu_count(), 2)  # Convert to percentage
                        memory = round(proc.info['memory_info'].rss / (1024 ** 3), 2)  # Convert to GB
                        gpu_memory = self.get_gpu_memory()  # Get GPU memory usage
                        self.data[keyword].append((timestamp, cpu, memory, gpu_memory))
                        with open(self.file_path, 'a') as f:
                            f.write(
                                f"{timestamp}, {keyword}, CPU: {cpu}%, Memory: {memory}GB, GPU Memory: {gpu_memory}GB\n")
            time.sleep(1)

    def stop(self):
        self.stop_flag = True
        self.thread.join()
        self.calculate_statistics()

    def calculate_statistics(self):
        for keyword, data in self.data.items():
            cpu_values = [x[1] for x in data]
            memory_values = [x[2] for x in data]
            gpu_memory_values = [x[3] for x in data]
            cpu_max = max(cpu_values)
            cpu_min = min(cpu_values)
            cpu_avg = round(sum(cpu_values) / len(cpu_values), 2)
            memory_max = max(memory_values)
            memory_min = min(memory_values)
            memory_avg = round(sum(memory_values) / len(memory_values), 2)
            gpu_memory_max = max(gpu_memory_values)
            gpu_memory_min = min(gpu_memory_values)
            gpu_memory_avg = round(sum(gpu_memory_values) / len(gpu_memory_values), 2)
            print(f"{keyword}:\nCPU - Max: {cpu_max}%, Min: {cpu_min}%, Avg: {cpu_avg}%")
            print(f"Memory - Max: {memory_max}GB, Min: {memory_min}GB, Avg: {memory_avg}GB")
            print(f"GPU Memory - Max: {gpu_memory_max}GB, Min: {gpu_memory_min}GB, Avg: {gpu_memory_avg}GB\n")

    def get_gpu_memory(self):
        try:
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'])
            return round(float(output.decode('utf-8').strip()) / 1024, 2)  # Convert to GB
        except Exception as e:
            print(f"Error getting GPU memory usage: {e}")
            return 0.0


monitor = PerformanceMonitor(["Chrome", "python", "iTerm", "pycharm", "download"], "performance.txt")
monitor.start()
time.sleep(10)  # Collect data for 10 seconds
monitor.stop()
