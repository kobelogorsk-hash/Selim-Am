import os
import sys
import subprocess
import ctypes
import re
from datetime import datetime

# Попытка импорта psutil для работы с процессами
try:
    import psutil
except ImportError:
    print("Ошибка: Не найдена библиотека 'psutil'.")
    print("Установите её командой: pip install psutil")
    sys.exit(1)

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def is_admin():
    """Проверяет, запущен ли скрипт от имени администратора."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def print_header(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def check_suspicious_processes():
    """Проверяет запущенные процессы на подозрительную активность."""
    print_header("ПРОВЕРКА ПОДОЗРИТЕЛЬНЫХ ПРОЦЕССОВ")
    
    suspicious_count = 0
    # Папки, где часто прячутся вирусы
    suspicious_paths = [
        r"\AppData\Local\Temp",
        r"\Users\Public",
        r"\Windows\Temp",
        r"\AppData\Roaming"
    ]
    
    # Подозрительные имена (маски)
    suspicious_names = ["miner", "hack", "crack", "keygen", "rat", "stealer"]

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            p_info = proc.info
            exe_path = p_info['exe']
            name = p_info['name'].lower()
            cmdline = " ".join(p_info['cmdline']).lower() if p_info['cmdline'] else ""
            
            is_suspicious = False
            reason = []

            # Проверка пути запуска
            if exe_path:
                for susp_path in suspicious_paths:
                    if susp_path.lower() in exe_path.lower():
                        is_suspicious = True
                        reason.append(f"Запуск из временной/общей папки: {exe_path}")
                        break
            
            # Проверка имени и командной строки
            for susp_name in suspicious_names:
                if susp_name in name or susp_name in cmdline:
                    is_suspicious = True
                    reason.append(f"Подозрительное имя/команда: {name}")
                    break
            
            # Проверка на отсутствие исполняемого файла (вирус скрылся)
            if exe_path and not os.path.exists(exe_path):
                is_suspicious = True
                reason.append("Файл процесса удален или скрыт (Rootkit признак)")

            if is_suspicious:
                suspicious_count += 1
                print(f"{Colors.FAIL}[!] ОБНАРУЖЕН ПОДОЗРИТЕЛЬНЫЙ ПРОЦЕСС{Colors.ENDC}")
                print(f"    PID: {p_info['pid']}")
                print(f"    Имя: {name}")
                print(f"    Путь: {exe_path}")
                for r in reason:
                    print(f"    Причина: {r}")
                print("-" * 40)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if suspicious_count == 0:
        print(f"{Colors.OKGREEN}[+] Подозрительных активных процессов не найдено.{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}Всего найдено подозрительных процессов: {suspicious_count}{Colors.ENDC}")
        print("Рекомендуется проверить эти файлы через VirusTotal или удалить их.")

def check_autostart():
    """Проверяет основные места автозагрузки."""
    print_header("ПРОВЕРКА АВТОЗАГРУЗКИ")
    
    autostart_items = []
    
    # 1. Проверка папок автозагрузки
    startup_folders = [
        os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup'),
        os.path.join(os.environ['PROGRAMDATA'], r'Microsoft\Windows\Start Menu\Programs\StartUp')
    ]
    
    for folder in startup_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if not file.startswith('.'):
                    autostart_items.append({
                        'type': 'Папка Startup',
                        'location': folder,
                        'value': file
                    })

    # 2. Проверка реестра (только если админ)
    if is_admin():
        import winreg
        reg_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]
        
        for hkey, path in reg_keys:
            try:
                key = winreg.OpenKey(hkey, path)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        autostart_items.append({
                            'type': 'Реестр',
                            'location': path,
                            'value': f"{name} -> {value}"
                        })
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass
    else:
        print(f"{Colors.WARNING}[*] Запуск не от администратора. Полный скан реестра недоступен.{Colors.ENDC}")

    # Вывод результатов
    print(f"Найдено элементов автозагрузки: {len(autostart_items)}")
    print("\nПоследние 10 элементов:")
    for item in autostart_items[-10:]:
        print(f"  [{item['type']}] {item['value']}")
    
    if len(autostart_items) > 20:
        print(f"... и еще {len(autostart_items) - 20} элементов (полный список можно вывести в лог).")

def run_sfc_scan():
    """Запускает проверку целостности системных файлов Windows (SFC)."""
    print_header("ПРОВЕРКА СИСТЕМНЫХ ФАЙЛОВ (SFC)")
    
    if not is_admin():
        print(f"{Colors.FAIL}[!] Требуется запуск от имени Администратора для проверки SFC!{Colors.ENDC}")
        print("Перезапустите скрипт правой кнопкой мыши -> 'Запуск от имени администратора'.")
        return

    print("Запуск утилиты sfc /scannow...")
    print("Это может занять несколько минут. Пожалуйста, подождите.\n")
    
    try:
        # Запускаем команду и ловим вывод
        process = subprocess.Popen(
            ["sfc", "/scannow"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='cp866' # Кодировка для русской версии Windows
        )
        
        # В реальном времени выводим прогресс (упрощенно)
        print("Сканирование идет... (ожидание завершения)")
        stdout, _ = process.communicate()
        
        print("\n--- Результат проверки ---")
        print(stdout)
        
        if "не найдено нарушений целостности" in stdout or "no integrity violations" in stdout.lower():
            print(f"{Colors.OKGREEN}[+] Системные файлы в порядке.{Colors.ENDC}")
        elif "восстановлены" in stdout.lower() or "found corrupt files" in stdout.lower():
            print(f"{Colors.WARNING}[!] Обнаружены и восстановлены поврежденные файлы.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[!] Возможно, обнаружены критические ошибки, которые не удалось исправить.{Colors.ENDC}")
            
    except Exception as e:
        print(f"{Colors.FAIL}Ошибка при запуске SFC: {e}{Colors.ENDC}")

def main():
    if os.name != 'nt':
        print("Эта программа предназначена только для Windows.")
        return

    if not is_admin():
        print(f"{Colors.WARNING}Внимание: Программа работает в ограниченном режиме.{Colors.ENDC}")
        print("Для полной проверки (Реестр, SFC) запустите от имени Администратора.\n")
    else:
        print(f"{Colors.OKGREEN}Запущено от имени Администратора. Доступны все функции.{Colors.ENDC}\n")

    print(f"{Colors.BOLD}СИСТЕМНЫЙ АНАЛИЗАТОР БЕЗОПАСНОСТИ{Colors.ENDC}")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
        print("\nВыберите действие:")
        print("1. Проверка подозрительных процессов")
        print("2. Проверка автозагрузки")
        print("3. Проверка системных файлов (SFC)")
        print("4. Запустить полную проверку (Все вышеперечисленное)")
        print("5. Выход")
        
        choice = input("\nВаш выбор (1-5): ")
        
        if choice == '1':
            check_suspicious_processes()
        elif choice == '2':
            check_autostart()
        elif choice == '3':
            run_sfc_scan()
        elif choice == '4':
            check_suspicious_processes()
            check_autostart()
            run_sfc_scan()
            print_header("ПРОВЕРКА ЗАВЕРШЕНА")
        elif choice == '5':
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод, попробуйте снова.")

if __name__ == "__main__":
    main()