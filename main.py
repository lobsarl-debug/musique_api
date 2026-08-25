from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DB_PATH = "data.db"

# -----------------------------
# INITIALISATION DE LA BASE
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Table instruments
    c.execute("""
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT,
            instrument TEXT,
            montant REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# MODELE POUR LES DONNEES
# -----------------------------
class Instrument(BaseModel):
    client: str
    instrument: str
    montant: float

# -----------------------------
# ENDPOINT : LIRE LES INSTRUMENTS
# -----------------------------
@app.get("/instruments")
def get_instruments():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rows = c.execute("SELECT client, instrument, montant FROM instruments").fetchall()
    conn.close()

    return [
        {"client": r[0], "instrument": r[1], "montant": r[2]}
        for r in rows
    ]

# -----------------------------
# ENDPOINT : AJOUTER UN INSTRUMENT
# -----------------------------
@app.post("/instruments")
def add_instrument(instrument: Instrument):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO instruments (client, instrument, montant) VALUES (?, ?, ?)",
        (instrument.client, instrument.instrument, instrument.montant),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}

import requests

PENNYLANE_TOKEN = "W2FnpJhdp-2s2dtC8edmRIL4uZrfbDBglC9aKcgpQ6k"  # à récupérer dans Pennylane > Connectivité > Développeurs

@app.get("/sync_pennylane")
def sync_pennylane():
    url = "https://api.pennylane.com/v1/instruments"
    headers = {"Authorization": f"Bearer {PENNYLANE_TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for item in data:
        c.execute(
            "INSERT OR REPLACE INTO instruments (client, instrument, montant) VALUES (?, ?, ?)",
            (item["client"], item["instrument"], item["montant"]),
        )
    conn.commit()
    conn.close()
    return {"status": "sync ok", "count": len(data)}

