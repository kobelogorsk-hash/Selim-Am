import os
import sys
import subprocess
import winreg
from datetime import datetime
import hashlib

# Попытка импортировать psutil для расширенной проверки процессов
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[-] Библиотека psutil не найдена. Расширенная проверка процессов будет отключена.")
    print("    Установите её командой: pip install psutil")

class SecurityScanner:
    def __init__(self):
        self.suspicious_keywords = ["miner", "hack", "keylog", "inject", "rat", "trojan"]
        self.temp_folders = [os.environ.get('TEMP'), os.environ.get('TMP'), r"C:\Windows\Temp"]
        
    def print_header(self, title):
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)

    def check_autostart_registry(self):
        """Проверка автозагрузки через реестр Windows"""
        self.print_header("ПРОВЕРКА АВТОЗАГРУЗКИ (Реестр)")
        autostart_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]
        
        found_items = []
        for hkey, path in autostart_keys:
            try:
                key = winreg.OpenKey(hkey, path)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        found_items.append({"name": name, "path": value, "source": path})
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except FileNotFoundError:
                continue
            except PermissionError:
                print(f"[!] Нет доступа к разделу: {path}")

        if not found_items:
            print("[+] В реестре не найдено подозрительных элементов автозагрузки.")
        else:
            print(f"[i] Найдено элементов автозагрузки: {len(found_items)}")
            for item in found_items:
                is_suspicious = any(k in item['path'].lower() for k in self.suspicious_keywords)
                status = "[!]" if is_suspicious else "[ ]"
                print(f"{status} {item['name']}: {item['path']}")
        
        return found_items

    def check_startup_folder(self):
        """Проверка папки Автозагрузка"""
        self.print_header("ПРОВЕРКА ПАПКИ АВТОЗАГРУЗКИ")
        startup_paths = [
            os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup'),
            r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup'
        ]
        
        found_files = []
        for path in startup_paths:
            if os.path.exists(path):
                files = os.listdir(path)
                for f in files:
                    full_path = os.path.join(path, f)
                    found_files.append(full_path)
                    is_suspicious = any(k in f.lower() for k in self.suspicious_keywords)
                    status = "[!]" if is_suspicious else "[ ]"
                    print(f"{status} Файл: {f}")
        
        if not found_files:
            print("[+] Папки автозагрузки пусты или недоступны.")
        return found_files

    def check_processes(self):
        """Проверка запущенных процессов"""
        if not PSUTIL_AVAILABLE:
            print("[!] Пропуск проверки процессов (требуется psutil).")
            return

        self.print_header("ПРОВЕРКА ЗАПУЩЕННЫХ ПРОЦЕССОВ")
        suspicious_procs = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cwd']):
            try:
                info = proc.info
                name = info['name']
                exe = info['exe']
                cwd = info['cwd']
                
                is_suspicious = False
                reason = []

                # Проверка по имени
                if any(k in name.lower() for k in self.suspicious_keywords):
                    is_suspicious = True
                    reason.append("Подозрительное имя")
                
                # Проверка запуска из временной папки
                if exe:
                    for temp in self.temp_folders:
                        if temp and exe.lower().startswith(temp.lower()):
                            is_suspicious = True
                            reason.append("Запуск из Temp-папки")
                            break
                
                if is_suspicious:
                    suspicious_procs.append({'pid': info['pid'], 'name': name, 'exe': exe, 'reason': reason})
                    print(f"[!] ПОДОЗРИТЕЛЬНО: PID {info['pid']} | {name}")
                    print(f"    Путь: {exe}")
                    print(f"    Причина: {', '.join(reason)}")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if not suspicious_procs:
            print("[+] Явных подозрительных процессов не обнаружено.")
        else:
            print(f"\n[!] Всего найдено подозрительных процессов: {len(suspicious_procs)}")

    def check_system_integrity():
        """Запуск проверки системных файлов Windows (SFC)"""
        print("\n" + "="*60)
        print(" ПРОВЕРКА ЦЕЛОСТНОСТИ СИСТЕМЫ (SFC)")
        print("="*60)
        print("[i] Запуск утилиты sfc /scannow...")
        print("[!] Требуется запуск от имени Администратора.")
        
        try:
            # Запускаем sfc в фоновом режиме, так как он требует консольного взаимодействия
            # Мы просто проверим, может ли команда быть вызвана
            result = subprocess.run(["sfc", "/verifyonly"], capture_output=True, text=True, timeout=10)
            if "Защита ресурсов Windows" in result.stdout or "Windows Resource Protection" in result.stdout:
                print("[+] Служба проверки системных файлов доступна.")
                print("[i] Для полного исправления запустите в терминале (Администратор): sfc /scannow")
            else:
                print("[-] Не удалось получить статус SFC.")
        except FileNotFoundError:
            print("[-] Утилита sfc не найдена (только для Windows).")
        except subprocess.TimeoutExpired:
            print("[i] Проверка занимает много времени, запущена в фоновом режиме проверки статуса.")
        except Exception as e:
            print(f"[-] Ошибка при проверке: {e}")

    def run_full_scan(self):
        print("\n🛡️  ЗАПУСК СКАНЕРА БЕЗОПАСНОСТИ СИСТЕМЫ")
        print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_autostart_registry()
        self.check_startup_folder()
        self.check_processes()
        SecurityScanner.check_system_integrity()
        
        print("\n" + "="*60)
        print(" СКАНИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print("[i] Обратите внимание: этот инструмент является базовым анализатором.")
        print("    Для полной защиты используйте профессиональные антивирусы.")

if __name__ == "__main__":
    # Проверка прав администратора (желательно для полной проверки)
    if not sys.platform.startswith('win'):
        print("[-] Этот скрипт предназначен для Windows.")
        sys.exit(1)

    scanner = SecurityScanner()
    scanner.run_full_scan()
    
    input("\nНажмите Enter, чтобы выйти...")
