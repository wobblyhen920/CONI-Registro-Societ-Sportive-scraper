
#!/usr/bin/env python3
"""
Scraper Registro BAS 2.0 (CONI)

- Estrae tutte le schede
- Backup ogni 300 record
- Output: coni_bas.xlsx
"""

import logging
import sys
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://www.coni.it/it/registro-societa-sportive/home/registro-bas-2-0/RegistroBas.html"
PAGE_SIZE = 30
BACKUP_STEP = 300
OUTPUT_FILE = "coni_bas.xlsx"
BACKUP_TPL = "coni_bas_backup_{:04d}.xlsx"
LOG_FILE = "scrape_coni_bas.log"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, "w", "utf-8"), logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_page(session: requests.Session, start: int) -> BeautifulSoup:
    url = BASE_URL if start == 0 else f"{BASE_URL}?start={start}"
    logging.debug("GET %s", url)
    r = session.get(url, headers={"User-Agent": "Mozilla/5.0 (BAS-Scraper)"}, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def parse_record(div) -> Dict[str, str]:
    nome = div.find("div", class_=lambda c: c and "nome-soc" in c)
    data: Dict[str, str] = {"Nome associazione": nome.get_text(strip=True) if nome else ""}
    for row in div.find_all("p", class_=lambda c: c and "riga" in c):
        l = row.find("span", class_=lambda c: c and "label" in c)
        v = row.find("span", class_=lambda c: c and "value" in c)
        if l and v:
            data[l.get_text(strip=True).rstrip(":")] = v.get_text(" ", strip=True)
    return data


def backup(rows: List[Dict[str, str]]) -> None:
    if rows and len(rows) % BACKUP_STEP == 0:
        df = pd.DataFrame(rows)
        df.insert(0, "id", range(1, len(df) + 1))
        filename = BACKUP_TPL.format(len(rows))
        df.to_excel(filename, index=False)
        logging.info("Backup a %d record: %s", len(rows), filename)


def save_final(rows: List[Dict[str, str]]) -> None:
    df = pd.DataFrame(rows)
    df.insert(0, "id", range(1, len(df) + 1))
    df.to_excel(OUTPUT_FILE, index=False)


def scrape() -> None:
    setup_logging()
    session = requests.Session()
    rows: List[Dict[str, str]] = []
    start = 0
    while True:
        soup = get_page(session, start)
        records = soup.find_all("div", class_=lambda c: c and "societa_elem_int" in c) or                   soup.find_all("div", class_=lambda c: c and "societa_elem" in c)
        logging.debug("start=%d -> %d record", start, len(records))
        if not records:
            break
        for div in records:
            rows.append(parse_record(div))
            backup(rows)
        start += PAGE_SIZE
        time.sleep(1)
    save_final(rows)
    logging.info("Completato: %d righe in %s", len(rows), OUTPUT_FILE)


if __name__ == "__main__":
    scrape()
