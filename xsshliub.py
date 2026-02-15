#!/usr/bin/env python3
import time
import sys
import argparse
import random
import os
import platform
from queue import Queue
from threading import Thread, Lock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

PAYLOADS_FILE = "payloads.txt"
RESULTS_FILE = "xss_found.txt"
MAX_REQ_PER_SESSION = 20

BANNER = f"""{Fore.MAGENTA}
██╗  ██╗███████╗███████╗██╗  ██╗██╗     ██╗██╗   ██╗██████╗ 
╚██╗██╔╝██╔════╝██╔════╝██║  ██║██║     ██║██║   ██║██╔══██╗
 ╚███╔╝ ███████╗███████╗███████║██║     ██║██║   ██║██████╔╝
 ██╔██╗ ╚════██║╚════██║██╔══██║██║     ██║██║   ██║██╔══██╗
██╔╝ ██╗███████║███████║██║  ██║███████╗██║╚██████╔╝██████╔╝
╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═════╝ 
                                                            
{Fore.RED}      ♥  Happy Bug Hunting Day  ♥
{Fore.CYAN}    The Union of Payload & Browser
{Style.RESET_ALL}"""

print_lock = Lock()
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

def load_file(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        return [l.strip() for l in f if l.strip()]

def get_driver(headless=True, proxies=None):
    options = Options()
    system_os = platform.system()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    if proxies:
        proxy = random.choice(proxies)
        options.add_argument(f"--proxy-server={proxy}")
    
    if headless:
        options.add_argument("--headless=new")

    service = None
    
    if system_os == "Linux":
        if os.path.exists("/usr/bin/chromium"):
            options.binary_location = "/usr/bin/chromium"
        elif os.path.exists("/usr/bin/google-chrome"):
            options.binary_location = "/usr/bin/google-chrome"
            
        if os.path.exists("/usr/bin/chromedriver"):
            service = Service("/usr/bin/chromedriver")
        else:
            service = Service()
            
    elif system_os == "Windows":
        service = Service()

    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(20)
        return driver
    except Exception as e:
        return None

def check_payload(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text
    except:
        return None

def worker(queue, delay, headless, proxies, pbar):
    while not queue.empty():
        driver = get_driver(headless, proxies)
        
        if not driver:
            time.sleep(1)
            continue

        requests_made = 0
        try:
            while requests_made < MAX_REQ_PER_SESSION and not queue.empty():
                try:
                    target_url, payload = queue.get(timeout=1)
                except:
                    break

                time.sleep(random.uniform(delay, delay * 1.5))
                alert_text = check_payload(driver, target_url)
                
                if alert_text:
                    with print_lock:
                        tqdm.write(f"\n{Fore.RED}♥ {Fore.GREEN}XSS FOUND! {Fore.RED}♥{Style.RESET_ALL}")
                        tqdm.write(f"{Fore.YELLOW}URL: {target_url}{Style.RESET_ALL}")
                        tqdm.write(f"{Fore.YELLOW}Payload: {payload}{Style.RESET_ALL}")
                        tqdm.write(f"{Fore.CYAN}Alert Text: {alert_text}{Style.RESET_ALL}")
                        
                        with open(RESULTS_FILE, "a") as f:
                            f.write(f"{target_url} | Alert: {alert_text}\n")
                
                requests_made += 1
                pbar.update(1)
                queue.task_done()
        except:
            pass
        finally:
            try:
                driver.quit()
            except:
                pass

def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Single URL with FUZZ")
    parser.add_argument("-l", "--list", help="List of URLs with FUZZ")
    parser.add_argument("-t", "--threads", type=int, default=3, help="Threads (Default: 3)")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay (sec)")
    parser.add_argument("-p", "--proxy", help="Single proxy")
    parser.add_argument("--proxy-list", help="File with list of proxies")
    parser.add_argument("--head", action="store_true", help="Show browser")
    args = parser.parse_args()

    payloads = load_file(PAYLOADS_FILE)
    if not payloads:
        print(f"{Fore.RED}[!] Create {PAYLOADS_FILE}!{Style.RESET_ALL}")
        sys.exit()

    targets = []
    if args.url:
        targets.append(args.url)
    
    if args.list:
        targets.extend(load_file(args.list))

    if not targets:
        print(f"{Fore.RED}[!] No targets specified (-u or -l){Style.RESET_ALL}")
        sys.exit()

    proxy_pool = []
    if args.proxy:
        proxy_pool.append(args.proxy)
    if args.proxy_list:
        proxy_pool.extend(load_file(args.proxy_list))
    
    if proxy_pool:
        print(f"{Fore.YELLOW}[*] Proxies loaded: {len(proxy_pool)}{Style.RESET_ALL}")

    task_queue = Queue()
    total_tasks = 0
    print(f"{Fore.BLUE}[*] Generating attack matrix...{Style.RESET_ALL}")
    
    for url in targets:
        if "FUZZ" not in url:
            url += "FUZZ"
            
        for pay in payloads:
            final_url = url.replace("FUZZ", pay)
            task_queue.put((final_url, pay))
            total_tasks += 1

    print(f"{Fore.BLUE}[*] Targets: {len(targets)}")
    print(f"{Fore.BLUE}[*] Payloads: {len(payloads)}")
    print(f"{Fore.BLUE}[*] Total Checks: {total_tasks}")
    print(f"{Fore.BLUE}[*] Engines: {args.threads}")
    print(f"{Fore.MAGENTA}[*] May the XSS be with you...{Style.RESET_ALL}\n")

    with tqdm(total=total_tasks, ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        threads = []
        for _ in range(args.threads):
            t = Thread(target=worker, args=(task_queue, args.delay, not args.head, proxy_pool, pbar))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

    print(f"\n{Fore.GREEN}[*] Scan finished. Check {RESULTS_FILE}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()