import time
import psutil
import threading
import subprocess
from collections import defaultdict
from statistics import mean
from datetime import datetime


class Monitor:
    def __init__(self, keywords, duration, interval=1):
        self.keywords = keywords
        self.duration = duration
        self.interval = interval
        self.data = defaultdict(lambda: defaultdict(list))
        self.filename = self.generate_filename()
        self.start_time = None
        self.end_time = None

    def generate_filename(self):
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"{'_'.join(self.keywords)}_{timestamp}.txt"
        return filename

    def start(self):
        self.start_time = datetime.now()
        start_time = time.time()
        while time.time() - start_time < self.duration:
            self.collect_data()
            time.sleep(self.interval)
        self.end_time = datetime.now()
        self.save_data()
        self.summarize_data()

    def collect_data(self):
        cpu_percent = round(psutil.cpu_percent(), 2)
        mem_info = round(psutil.virtual_memory().used / (1024 ** 3), 2)  # Convert to GB and round

        self.data["system"]["cpu"].append(cpu_percent)
        self.data["system"]["memory"].append(mem_info)

        for keyword in self.keywords:
            cpu_percent = 0.0
            mem_info = 0.0
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'cmdline']):
                if keyword in (' '.join(proc.info['cmdline']) if proc.info['cmdline'] else proc.info['name']):
                    cpu_percent += proc.info['cpu_percent']
                    mem_info += proc.info['memory_info'].rss / (1024 ** 3)  # Convert to GB

            self.data[keyword]['cpu'].append(round(cpu_percent, 2))
            self.data[keyword]['memory'].append(round(mem_info, 2))

    def save_data(self):
        with open(self.filename, "w") as f:
            f.write(f'Start Time: {self.start_time.strftime("%Y.%m.%d %H:%M:%S")}\n')
            for key, values in self.data.items():
                f.write(f'--- {key} ---\n')
                for metric, readings in values.items():
                    f.write(f'{metric}: {readings}\n')
                f.write('\n')
            f.write(f'End Time: {self.end_time.strftime("%Y.%m.%d %H:%M:%S")}\n')

    def summarize_data(self):
        summary = {}
        for key, values in self.data.items():
            summary[key] = {k: {"min": round(min(v), 2),
                                "max": round(max(v), 2),
                                "avg": round(mean(v), 2)}
                            for k, v in values.items()}
        with open(self.filename, "a") as f:
            f.write('--- Summary ---\n')
            print('--- Summary ---')
            for key, value in summary.items():
                f.write(f'{key}: {value}\n')
                print(f'{key}: {value}')

    # def get_gpu_memory(self):
    #     result = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
    #                             stdout=subprocess.PIPE)
    #     return sum(float(x) for x in result.stdout.decode().strip().split('\n')) / 1024  # Convert to GB


monitor = Monitor(["pycharm", "Chrome"], 10)
monitor.start()


