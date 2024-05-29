import psutil
import cpuinfo
import GPUtil

def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = []

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent_used = usage.percent

            disk_info.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'total_gb': total_gb,
                'used_gb': used_gb,
                'free_gb': free_gb,
                'percent_used': percent_used
            })
        except Exception as e:
            print(f"Could not get usage for {partition.device}: {e}")
    
    return disk_info

def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    return {
        'brand': info['brand_raw'],
        'cores': psutil.cpu_count(logical=False),
        'threads': psutil.cpu_count(logical=True)
    }

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    gpu_info = []

    for gpu in gpus:
        gpu_info.append({
            'name': gpu.name,
            'driver_version': gpu.driver,
            'memory_total': gpu.memoryTotal,
            'memory_free': gpu.memoryFree,
            'memory_used': gpu.memoryUsed,
            'temperature': gpu.temperature
        })
    
    return gpu_info

def disks():
    print("CPU Information:")
    cpu = get_cpu_info()
    print(f"  Brand: {cpu['brand']}")
    print(f"  Cores: {cpu['cores']}")
    print(f"  Threads: {cpu['threads']}")
    print()

    print("GPU Information:")
    gpus = get_gpu_info()
    if gpus:
        for gpu in gpus:
            print(f"  Name: {gpu['name']}")
            print(f"  Driver Version: {gpu['driver_version']}")
            print(f"  Total Memory: {gpu['memory_total']} MB")
            print(f"  Used Memory: {gpu['memory_used']} MB")
            print(f"  Free Memory: {gpu['memory_free']} MB")
            print(f"  Temperature: {gpu['temperature']}°C")
            print()
    else:
        print("  No GPUs found")
        print()

    print("Disk Information:")
    disks = get_disk_info()
    for disk in disks:
        print(f"  Device: {disk['device']}")
        print(f"    Mountpoint: {disk['mountpoint']}")
        print(f"    Total Space: {disk['total_gb']:.2f} GB")
        print(f"    Used Space: {disk['used_gb']:.2f} GB ({disk['percent_used']}%)")
        print(f"    Free Space: {disk['free_gb']:.2f} GB")

if __name__ == "__main__":
    disks()
