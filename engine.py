#!/usr/bin/env python3
"""
prosty silnik scrapingu - wieloprocesowy z asyncio
"""

import aiohttp
import asyncio
import multiprocessing as mp
from multiprocessing import Queue, Process
import re
import json
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse

# wzorce do wyodrebniania danych
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'(?:\+\d{1,3}\s?)?\d{2,3}[-\s]?\d{3}[-\s]?\d{2,4}')
ADDRESS_PATTERN = re.compile(r'\d{2}-\d{3}\s+[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż\s]+')

def is_valid_url(url):
    """prosta walidacja url"""
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False

async def fetch_page(session, url):
    """pobiera strone"""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                return await response.text()
            else:
                logging.warning(f"blad http {response.status} dla {url}")
    except Exception as e:
        logging.error(f"blad {url}: {e}")
    return None

def parse_html(html_content, url):
    """parsuje html i wyodrebnia dane"""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # usun skrypty i style
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text()
    title = soup.find('title')
    title = title.get_text() if title else ""
    
    # wyodrebnianie danych - 4 grupy
    emails = EMAIL_PATTERN.findall(text)[:5]
    phones = PHONE_PATTERN.findall(text)[:3]  
    addresses = ADDRESS_PATTERN.findall(text)[:2]
    headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
    
    return {
        'url': url,
        'title': title,
        'emails': emails,
        'phones': phones,
        'addresses': addresses,
        'headings': headings
    }

async def scrape_urls(urls):
    """scrapuje liste url-i asynchronicznie"""
    results = []
    # zmniejsz limit polaczen
    connector = aiohttp.TCPConnector(limit=3)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for url in urls:
            if is_valid_url(url):
                tasks.append(fetch_page(session, url))
            else:
                logging.warning(f"nieprawidlowy url: {url}")
                tasks.append(asyncio.sleep(0, result=None))  # placeholder
        
        html_pages = await asyncio.gather(*tasks)
        for html, url in zip(html_pages, urls):
            data = parse_html(html, url)
            if data:
                results.append(data)
                logging.info(f"przetworzono: {url}")
    return results

def worker(urls_chunk, result_queue, process_id):
    """funkcja robocza procesu"""
    print(f"proces {process_id} - {len(urls_chunk)} url-i")
    
    # nowa petla asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(scrape_urls(urls_chunk))
        for result in results:
            result_queue.put(result)
    finally:
        loop.close()

def scrape_multiprocess(urls, num_processes=None):
    """glowna funkcja scrapingu wieloprocesowego"""
    if not urls:
        return []
    if not num_processes:
        num_processes = min(2, len(urls))  # zmniejsz do max 2 procesow
    
    # podzial url-i na chunki
    chunk_size = max(1, len(urls) // num_processes)
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
    
    # kolejka wynikow
    result_queue = Queue()
    
    # uruchomienie procesow
    processes = []
    for i, chunk in enumerate(chunks):
        p = Process(target=worker, args=(chunk, result_queue, i))
        p.start()
        processes.append(p)
    
    # oczekiwanie i zbieranie wynikow
    for p in processes:
        p.join()
    
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    return results

def save_results(results, filename="results.json"):
    """zapisuje wyniki do json"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"zapisano {len(results)} wynikow do {filename}")

def main():
    """demo"""
    urls = [
        'https://www.uw.edu.pl',
        'https://www.pw.edu.pl', 
        'https://www.agh.edu.pl',
        'https://www.uj.edu.pl'
    ]
    
    print(f"scrapowanie {len(urls)} stron...")
    results = scrape_multiprocess(urls)
    
    save_results(results)
    
    # podsumowanie
    total_emails = sum(len(r['emails']) for r in results)
    total_phones = sum(len(r['phones']) for r in results)
    
    print(f"\nwyniki:")
    print(f"strony: {len(results)}")
    print(f"emaile: {total_emails}")
    print(f"telefony: {total_phones}")

if __name__ == "__main__":
    mp.freeze_support()
    main()
