# Monitor Spese di Coppia

Web app in **Python + Streamlit + SQLite** per gestire spese personali e condivise in una coppia.

## Regole del prodotto

- Gli utenti sono esattamente 2
- Le spese `Personali`:
  - sono visibili solo al proprietario
  - non influenzano il saldo di coppia
- Le spese `Condivise`:
  - sono visibili a entrambi
  - sono divise sempre `50/50`
  - influenzano il saldo
- Le entrate sono private e visibili solo al proprietario

## Struttura

```text
.
├── app.py
├── database.py
├── services.py
├── ui_helpers.py
├── requirements.txt
├── README.md
└── data/
    └── spese.db
```

## Avvio

```bash
cd "/Users/mattiabonuso/Documents/New project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## Credenziali demo

- `io` con password vuota
- `compagna` con password `demo123`

## Note

- Il database viene creato automaticamente al primo avvio
- Le migrazioni vengono applicate in automatico sul database locale esistente
- Se `reportlab` non è installato, l'esportazione PDF resta disattivata
