#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime

# Путь для логов
LOG_DIR = "/var/log"

def get_timestamp():
    return int(time.time())

def get_cpu_usage():
    with open("/proc/stat", "r") as f:
        line = f.readline().split()
    
    idle = int(line[4])
    total = sum(map(int, line[1:8]))
    
    if not hasattr(get_cpu_usage, "prev_total"):
        get_cpu_usage.prev_total = total
        get_cpu_usage.prev_idle = idle
        return 0.0
    
    prev_total = get_cpu_usage.prev_total
    prev_idle = get_cpu_usage.prev_idle
    
    delta_total = total - prev_total
    delta_idle = idle - prev_idle
    
    get_cpu_usage.prev_total = total
    get_cpu_usage.prev_idle = idle
    
    if delta_total == 0:
        return 0.0
    
    return round((1 - delta_idle / delta_total) * 100, 2)

def get_memory_usage():
    mem_info = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().split()[0]
                mem_info[key] = int(value)
    
    total = mem_info.get("MemTotal", 1)
    available = mem_info.get("MemAvailable", total)
    used = total - available
    
    return {
        "ram_total_mb": round(total / 1024, 2),
        "ram_used_mb": round(used / 1024, 2),
        "ram_available_mb": round(available / 1024, 2),
        "ram_used_percent": round((used / total) * 100, 2)
    }

def get_disk_usage():
    stat = os.statvfs("/")
    total = stat.f_blocks * stat.f_frsize
    free = stat.f_bfree * stat.f_frsize
    used = total - free
    
    return {
        "disk_total_gb": round(total / (1024**3), 2),
        "disk_used_gb": round(used / (1024**3), 2),
        "disk_free_gb": round(free / (1024**3), 2),
        "disk_used_percent": round((used / total) * 100, 2)
    }

def get_load_avg():
    with open("/proc/loadavg", "r") as f:
        data = f.read().split()
    
    return {
        "load_1min": float(data[0]),
        "load_5min": float(data[1]),
        "load_15min": float(data[2])
    }

def get_uptime():
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.read().split()[0])
    
    return {
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_hours": round(uptime_seconds / 3600, 2),
        "uptime_days": round(uptime_seconds / 86400, 2)
    }

def collect_metrics():
    cpu = get_cpu_usage()
    mem = get_memory_usage()
    disk = get_disk_usage()
    load = get_load_avg()
    uptime = get_uptime()
    
    metrics = {
        "timestamp": get_timestamp(),
        "cpu_usage_percent": cpu,
        "ram_used_mb": mem["ram_used_mb"],
        "ram_used_percent": mem["ram_used_percent"],
        "disk_used_percent": disk["disk_used_percent"],
        "disk_free_gb": disk["disk_free_gb"],
        "load_1min": load["load_1min"],
        "load_5min": load["load_5min"],
        "uptime_days": uptime["uptime_days"]
    }
    
    return metrics

def main():
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = f"{LOG_DIR}/{current_date}-awesome-monitoring.log"
    
    data = collect_metrics()
    
    with open(log_file, "a") as f:
        json.dump(data, f)
        f.write("\n")
    
    print(f" Метрики записаны в {log_file}")

if __name__ == "__main__":
    main()
