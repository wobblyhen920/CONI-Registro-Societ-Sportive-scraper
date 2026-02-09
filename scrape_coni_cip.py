
#!/usr/bin/env python3

import logging
import os
import sys
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://www.coni.it/it/registro-societa-sportive/home/registro-cip-2-0/RegistroCip.html"
PAGE_SIZE = 30               # record per pagina (verificato sul sito)
BACKUP_STEP = 300            # backup ogni 300 righe
OUTPUT_FILE = "coni.xlsx"
BACKUP_TPL = "coni_backup_{:04d}.xlsx"
LOG_FILE = "scrape_coni.log"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.WARNING)


def get_page(session: requests.Session, start: int = 0) -> BeautifulSoup:
    url = BASE_URL if start == 0 else f"{BASE_URL}?start={start}"
    logging.debug("GET %s", url)
    resp = session.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; CIP-Scraper/1.0)"},
        timeout=30,
    )
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def parse_record(div) -> Dict[str, str]:
    # Nome società
    nome_tag = div.find("div", class_="nome-soc")
    nome = nome_tag.get_text(strip=True) if nome_tag else ""

    # Campi etichetta/valore
    data: Dict[str, str] = {"Nome società": nome}
    for row in div.find_all("p", class_="riga"):
        label_tag = row.find("span", class_="label")
        value_tag = row.find("span", class_="value")
        if not label_tag or not value_tag:
            continue
        label = label_tag.get_text(strip=True).rstrip(":").strip()
        value = value_tag.get_text(' ', strip=True)
        data[label] = value
    return data


def scrape() -> None:
    setup_logging()
    session = requests.Session()

    all_rows: List[Dict[str, str]] = []
    start = 0
    while True:
        soup = get_page(session, start)
        records = soup.find_all("div", class_="societa_elem_int")
        logging.debug("Pagina start=%s -> %d record", start, len(records))
        if not records:
            break

        for div in records:
            all_rows.append(parse_record(div))

            # backup periodico
            if len(all_rows) % BACKUP_STEP == 0:
                write_excel(all_rows, BACKUP_TPL.format(len(all_rows)))
                logging.info("Backup intermedio a %d record", len(all_rows))

        start += PAGE_SIZE
        time.sleep(1.0)

    write_excel(all_rows, OUTPUT_FILE)
    logging.info("Terminato: %d record totali salvati in %s", len(all_rows), OUTPUT_FILE)


def write_excel(rows: List[Dict[str, str]], filename: str) -> None:
    df = pd.DataFrame(rows)
    df.insert(0, "id", range(1, len(df) + 1))
    df.to_excel(filename, index=False)


if __name__ == "__main__":
    scrape()
