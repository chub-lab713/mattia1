<<<<<<< HEAD
# Monitor Spese Personali e di Coppia

Web app semplice in **Python + Streamlit + SQLite** per gestire spese personali e condivise in modo chiaro.

## Funzionalita principali

- Inserimento di spese personali o condivise
- Divisione condivisa `50/50` oppure personalizzata in percentuale
- Elenco spese con filtri nella sidebar
- Dashboard con riepilogo mensile
- Modifica ed eliminazione delle spese
- Grafici per categoria e andamento mensile
- Esportazione CSV dei dati filtrati
- Dati di esempio caricati automaticamente al primo avvio
- Login locale con utenti demo

## Struttura del progetto

```text
.
├── app.py
├── database.py
├── services.py
├── requirements.txt
├── README.md
└── data/
    └── spese.db   (creato automaticamente al primo avvio)
```

## Requisiti

- Python 3.10 o superiore

## Avvio passo per passo

1. Apri il terminale nella cartella del progetto.
2. Crea un ambiente virtuale:

```bash
python3 -m venv .venv
```

3. Attiva l'ambiente virtuale:

Su macOS o Linux:

```bash
source .venv/bin/activate
```

Su Windows:

```bash
.venv\Scripts\activate
```

4. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

5. Avvia l'app:

```bash
streamlit run app.py
```

6. Apri il browser all'indirizzo mostrato da Streamlit, di solito:

```text
http://localhost:8501
```

## Credenziali demo

Puoi accedere con uno di questi utenti:

- Username: `io`
  Password: `demo123`
- Username: `compagna`
  Password: `demo123`

## Note di progetto

- Il database SQLite viene salvato in `data/spese.db`.
- Se il database e vuoto, l'app inserisce alcune spese demo per facilitare i test.
- Anche gli utenti demo vengono creati automaticamente al primo avvio.
- Il saldo di coppia considera solo le **spese condivise**:
  - valore positivo: la compagna deve soldi a te
  - valore negativo: tu devi soldi a lei
- Nella divisione personalizzata, la percentuale inserita rappresenta **la tua quota**.
- Il login protegge l'accesso all'app, ma al momento non separa le spese per utente: entrambi gli account vedono lo stesso archivio.

## Possibili miglioramenti futuri

- Gestione di piu persone
- Budget mensili per categoria
- Login utente
- Backup automatico del database
# https-github.com-mattia-monitor-spese
=======
# https-github.com-chub-lab713-monitor-spese
>>>>>>> 84642d86f72d5b38d2d9ec7537d0173b8368f41c
