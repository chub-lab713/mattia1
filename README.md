# Monitor Spese di Coppia

Applicazione per gestire spese personali e condivise in una coppia con **backend Python + SQLite** e due interfacce disponibili:

- **Modalità consigliata:** frontend **React** + backend **FastAPI**
- **Modalità legacy:** interfaccia **Streamlit**

La business logic resta in Python e viene riutilizzata sia dalle API FastAPI sia dalla UI Streamlit legacy.

## Regole del prodotto

- Gli utenti sono esattamente 2
- Le spese `Personali`:
  - sono visibili solo al proprietario
  - non influenzano il saldo di coppia
- Le spese `Condivise`:
  - sono visibili a entrambi
  - sono divise di default `50/50`, con supporto anche a divisioni personalizzate
  - influenzano il saldo
- Le entrate sono private e visibili solo al proprietario

## Architettura attuale

- `database.py` gestisce inizializzazione e accesso al database SQLite
- `services.py` contiene la business logic principale: autenticazione, profilo, spese, entrate, dashboard, saldo coppia, permessi e visibilità
- `backend/main.py` espone le API HTTP tramite FastAPI
- `frontend/` contiene la nuova interfaccia React
- `app.py` resta disponibile come interfaccia Streamlit legacy per compatibilità e migrazione graduale

## Modalità consigliata

La modalità consigliata è oggi:

- **FastAPI + React**

Streamlit resta disponibile come interfaccia legacy/temporanea finché la migrazione frontend non sarà completata del tutto.

## Prerequisiti

- Python 3.x
- `pip`
- Node.js + `npm` per il frontend React
- dipendenze Python da `requirements.txt`

## Struttura

```text
.
├── app.py
├── backend/
│   ├── main.py
│   ├── schemas.py
│   └── serializers.py
├── database.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   └── src/
├── services.py
├── ui_helpers.py
├── requirements.txt
├── README.md
└── data/
    └── spese.db
```

## Installazione

### Dipendenze Python

```bash
cd "/Users/mattiabonuso/Documents/New project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Dipendenze frontend React

```bash
cd "/Users/mattiabonuso/Documents/New project/frontend"
npm install
```

## Avvio rapido

### A. Backend FastAPI

```bash
cd "/Users/mattiabonuso/Documents/New project"
source .venv/bin/activate
uvicorn backend.main:app --reload
```

### B. Frontend React

```bash
cd "/Users/mattiabonuso/Documents/New project/frontend"
npm run dev
```

### C. Streamlit legacy

```bash
cd "/Users/mattiabonuso/Documents/New project"
source .venv/bin/activate
streamlit run app.py
```

## URL locali

- Backend API: `http://127.0.0.1:8000`
- Frontend React: `http://127.0.0.1:5173` oppure la porta mostrata da Vite
- Streamlit legacy: URL mostrato da Streamlit nel terminale locale

## Funzionalità

Il backend/API gestisce le funzioni principali del prodotto:

- autenticazione e sessione
- profilo utente
- CRUD spese
- CRUD entrate
- dashboard e metriche
- saldo di coppia
- filtri, visibilità e ownership dei dati

La nuova UI React usa queste API come frontend principale in sviluppo.
La UI Streamlit resta disponibile come interfaccia legacy.

## Credenziali demo

- `admin` con password vuota
- `admin2` con password `demo123`

## Note pratiche

- Il database viene creato automaticamente al primo avvio
- Le migrazioni vengono applicate in automatico sul database locale esistente
- Se `reportlab` non è installato, l'esportazione PDF resta disattivata
- In sviluppo locale il frontend React usa il proxy `/api` verso FastAPI
- Se la porta `5173` è occupata, Vite userà un'altra porta: usa quella mostrata nel terminale
- FastAPI/React e Streamlit possono coesistere temporaneamente durante la migrazione
# rob.couple
# rob.couple
