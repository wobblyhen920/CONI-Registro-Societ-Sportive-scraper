# CONI Registro Società Sportive Scraper

[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Questo repository contiene due script Python per lo scraping automatico di dati dal Registro Società Sportive del CONI (Comitato Olimpico Nazionale Italiano). Gli script estraggono informazioni su società sportive dilettantistiche dal Registro BAS 2.0 e dal Registro CIP 2.0, disponibili sul sito ufficiale del CONI (`www.coni.it`). 

- `scrape_coni_bas.py`: scraping del Registro BAS 2.0.
- `scrape_coni_cip.py`: Scrapa del Registro CIP 2.0.

I dati includono dettagli come nome società, data inserimento, CAP, comune, regione, codice fiscale, affiliazioni, discipline praticate e altro.

Il web scraping potrebbe violare i termini di servizio del sito target. Assicurati di rispettare le norme sul rate limiting. Questo script è fornito a scopo educativo e di ricerca; l'autore non si assume responsabilità per usi impropri. Il sito potrebbe cambiare struttura, rendendo gli script obsoleti.

## Funzionalità Principali

- **Scraping paginato:** naviga automaticamente le pagine del registro (30 record per pagina) fino a esaurimento.
- **Parsing dettagli:** estrae campi come nome società, data, CAP, comune, regione, codice fiscale, affiliazioni e discipline usando BeautifulSoup.
- **Backup periodici:** salva backup intermedi in file Excel ogni 300 record per evitare perdite in caso di interruzioni.
- **Output:** produce file Excel (.xlsx) con i dati estratti, inclusa una colonna ID sequenziale.
- **Logging:** registra operazioni dettagliate in file log e su stdout per debugging.
- **Ritardo tra richieste:** aggiunge un sleep di 1 secondo tra le pagine per ridurre il carico sul server.

## Dipendenze

Gli script richiedono Python 3.x e le seguenti librerie:

- `requests`
- `beautifulsoup4` (bs4)
- `pandas`
- `lxml` (parser per BeautifulSoup)

Installale con:

```bash
pip install requests beautifulsoup4 pandas lxml
```

## Installazione

1. Clona il repository:

   ```bash
   git clone https://github.com/tuo-username/coni-scraper.git
   cd coni-scraper
   ```

2. Crea un ambiente virtuale (opzionale ma raccomandato):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. Installa le dipendenze come sopra.

## Uso

Gli script non richiedono input esterni; effettuano lo scraping dell'intero registro automaticamente. Esegui ciascuno separatamente.

### Per Registro BAS 2.0

```bash
python scrape_coni_bas.py
```

- Output: `coni_bas.xlsx` (file finale), backup come `coni_bas_backup_XXXX.xlsx`.
- Log: `scrape_coni_bas.log`.

### Per Registro CIP 2.0

```bash
python scrape_coni_cip.py
```

- Output: `coni.xlsx` (file finale), backup come `coni_backup_XXXX.xlsx`.
- Log: `scrape_coni.log`.

Nota: L'esecuzione potrebbe richiedere tempo a seconda della dimensione del registro (es. migliaia di record). Interrompi con Ctrl+C se necessario; i backup permettono di riprendere manualmente.

### Esempio di Output

Il file Excel prodotto ha colonne come:

- `id` (sequenziale, aggiunto dallo script)
- `Nome società`
- `Numero inserimento`
- `Data`
- `CAP`
- `Comune (PR)` (o simile, a seconda del registro)
- `Regione`
- `Codice Fiscale (CIP)` (per CIP)
- `Affiliata a (CIP)`
- `Codice di affiliazione (CIP)`
- `Discipline/specialità praticate (CIP)`
- E campi specifici per BAS come `Organismo di appartenenza (BAS)`, `Codice identificativo (BAS)`, ecc.

Un file di esempio (`CONI Registro Società Sportive - scraping dataset.xlsx`) è incluso nel repository, con sheet "Sheet1" contenente dati campione (es. righe su società CIP e BAS con dettagli su paraclimb, calcio, ecc.).

## Come funzionano gli script

1. **Inizializzazione:** configura logging e sessione requests.
2. **Paginazione:** inizia da `start=0`, incrementa di `PAGE_SIZE` (30) fino a quando non ci sono più record.
3. **Estrazione:** per ogni pagina, trova div con classi specifiche (`societa_elem_int` o `societa_elem`), parsifica nome e campi etichetta/valore.
4. **Backup:** ogni 300 record, salva un file Excel intermedio.
5. **Finale:** alla fine, salva il dataset completo in Excel.
6. **Error Handling:** gestisce errori HTTP con `raise_for_status`; logging per debug.

Gli script sono simili, con differenze minime nei selettori CSS e nomi file.

## Contributi

Pull request benvenute! Per bug o feature, apri un'issue.

## Licenza

MIT License. Vedi [LICENSE](LICENSE) per dettagli.
