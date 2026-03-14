import psutil
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated


# ---------------------------------------------------------
# Помощни функции за извличане на системната информация
# ---------------------------------------------------------
def get_system_metrics():
    # Извличане на данни за процесора (CPU)
    # interval=None е важно при уеб заявки, за да не блокираме сървъра
    cpu_total = psutil.cpu_percent(interval=None)
    cpu_cores = psutil.cpu_percent(interval=None, percpu=True)

    # Извличане на данни за RAM паметта
    ram = psutil.virtual_memory()

    # Извличане на данни за Диска (Root директорията)
    disk = psutil.disk_usage('/')

    # Конвертиране на байтовете в Гигабайти за по-лесно четене
    bytes_to_gb = 1024 ** 3

    return {
        'cpu': {
            'total_percent': cpu_total,
            'cores_percent': cpu_cores,
            'core_count': psutil.cpu_count(logical=True)
        },
        'ram': {
            'total_gb': round(ram.total / bytes_to_gb, 2),
            'used_gb': round(ram.used / bytes_to_gb, 2),
            'free_gb': round(ram.available / bytes_to_gb, 2),
            'percent': ram.percent
        },
        'disk': {
            'total_gb': round(disk.total / bytes_to_gb, 2),
            'used_gb': round(disk.used / bytes_to_gb, 2),
            'free_gb': round(disk.free / bytes_to_gb, 2),
            'percent': disk.percent
        }
    }


def get_top_processes(limit=10):
    processes = []
    core_count = psutil.cpu_count(logical=True)  # Взимаме броя ядра за нормализиране на процентите

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info

            # 1. Игнорираме "System Idle Process" (обикновено е с PID 0 на Windows)
            if info['pid'] == 0 or info['name'] == 'System Idle Process':
                continue

            # Закръгляме RAM процентите
            if info['memory_percent'] is not None:
                info['memory_percent'] = round(info['memory_percent'], 2)

            # 2. Нормализираме CPU процентите спрямо броя ядра (за да са от 0 до 100%)
            if info['cpu_percent'] is not None:
                normalized_cpu = info['cpu_percent'] / core_count
                info['cpu_percent'] = round(normalized_cpu, 2)

            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    processes = sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:limit]
    return processes

# ---------------------------------------------------------
# DRF API Ендпойнти (Views)
# ---------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Временно разрешаваме достъп до всички за тест. После ще сменим на IsAuthenticated.
def api_system_stats(request):
    """ Връща JSON с натоварването на CPU, RAM и Disk """
    stats = get_system_metrics()
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_top_processes(request):
    """ Връща JSON със списък от най-натоварващите процеси """
    processes = get_top_processes(limit=10)
    return Response({'processes': processes})


# ---------------------------------------------------------
# Основен изглед за Frontend-a
# ---------------------------------------------------------
@login_required(login_url='/login/') # Ако не е логнат, го пращаме към логин страницата
def index(request):
    """ Зарежда основния HTML шаблон, където ще работи Vue.js """
    return render(request, 'main/index.html')
