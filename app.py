import requests
from flask import Flask, render_template, request
from datetime import datetime

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
METEO_URL = "https://api.open-meteo.com/v1/forecast"
GIORNI_SETTIMANA = [
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica",
]
MESI = [
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
]
CODICI_METEO = {
    0: "Sereno",
    1: "Prevalentemente sereno",
    2: "Parzialmente nuvoloso",
    3: "Coperto",
    45: "Nebbia",
    48: "Nebbia con brina",
    51: "Pioviggine leggera",
    53: "Pioviggine moderata",
    55: "Pioviggine intensa",
    56: "Pioviggine gelata leggera",
    57: "Pioviggine gelata intensa",
    61: "Pioggia debole",
    63: "Pioggia moderata",
    65: "Pioggia forte",
    66: "Pioggia gelata leggera",
    67: "Pioggia gelata intensa",
    71: "Neve debole",
    73: "Neve moderata",
    75: "Neve intensa",
    77: "Granelli di neve",
    80: "Rovesci di pioggia deboli",
    81: "Rovesci di pioggia moderati",
    82: "Rovesci di pioggia violenti",
    85: "Rovesci di neve deboli",
    86: "Rovesci di neve forti",
    95: "Temporale",
    96: "Temporale con grandine leggera",
    99: "Temporale con grandine forte",
}


def cerca_coordinate(citta):
    """
    Recupera latitudine, longitudine e regione di una città
    tramite l'API di geocoding di Open-Meteo.
    """

    params = {
        "name": citta,
        "language": "it",
        "count": 1,
    }

    try:
        risposta_geocoding = requests.get(GEOCODING_URL, params=params, timeout=5)
        risposta_geocoding.raise_for_status()

    except requests.exceptions.RequestException:
        return None

    dati_geocoding = risposta_geocoding.json()
    risultati = dati_geocoding.get("results")

    if not risultati:
        return None

    primo_risultato = risultati[0]

    latitudine = primo_risultato["latitude"]
    longitudine = primo_risultato["longitude"]
    regione = primo_risultato.get("admin1", "Regione sconosciuta")

    return latitudine, longitudine, regione


def ottieni_meteo(latitudine, longitudine):
    """
    Recupera temperatura, umidità e velocità del vento di una città
    tramite l'API meteo di Open-Meteo.
    """

    params = {
        "latitude": latitudine,
        "longitude": longitudine,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "temperature_2m_min,temperature_2m_max,weather_code",
    }

    try:
        risposta_meteo = requests.get(METEO_URL, params=params, timeout=5)
        risposta_meteo.raise_for_status()

    except requests.exceptions.RequestException:
        return None

    dati_meteo = risposta_meteo.json()

    corrente = dati_meteo.get("current")

    if not corrente:
        return None

    temperatura = corrente["temperature_2m"]
    umidita = corrente["relative_humidity_2m"]
    velocita_vento = corrente["wind_speed_10m"]
    codice_corrente = corrente["weather_code"]

    previsioni = dati_meteo.get("daily")

    if not previsioni:
        return None

    giorni = previsioni["time"]
    temperature_minime = previsioni["temperature_2m_min"]
    temperature_massime = previsioni["temperature_2m_max"]
    codici_previsioni = previsioni["weather_code"]

    return (
        temperatura,
        umidita,
        velocita_vento,
        codice_corrente,
        giorni,
        temperature_minime,
        temperature_massime,
        codici_previsioni,
    )


def ottieni_descrizione(codice_meteo):
    """Restituisce la descrizione associata a un codice meteo."""

    return CODICI_METEO.get(codice_meteo, "Meteo sconosciuto")


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    dati = None
    errore = None
    meteo = None
    citta = None
    regione = None

    latitudine = request.form.get("latitudine")
    longitudine = request.form.get("longitudine")

    if latitudine and longitudine:
        latitudine = float(latitudine)
        longitudine = float(longitudine)
        citta = "La tua posizione"

        meteo = ottieni_meteo(latitudine, longitudine)

        if meteo is None:
            errore = "Impossibile contattare il servizio meteo."

    elif request.method == "POST":
        citta = request.form["citta"]
        coordinate = cerca_coordinate(citta)

        if coordinate is None:
            errore = f'Impossibile localizzare "{citta}".'

        else:
            latitudine, longitudine, regione = coordinate
            meteo = ottieni_meteo(latitudine, longitudine)

            if meteo is None:
                errore = "Impossibile contattare il servizio meteo."

    if meteo is not None:

        (
            temperatura,
            umidita,
            velocita_vento,
            codice_corrente,
            giorni,
            temperature_minime,
            temperature_massime,
            codici_previsioni,
        ) = meteo

        previsioni = []

        for giorno, minima, massima, codice in zip(
            giorni, temperature_minime, temperature_massime, codici_previsioni
        ):
            data = datetime.strptime(giorno, "%Y-%m-%d")
            nome_giorno = GIORNI_SETTIMANA[data.weekday()]
            nome_mese = MESI[data.month - 1]
            giorno_formattato = f"{nome_giorno} {data.day} {nome_mese}"
            previsioni.append(
                {
                    "giorno": giorno_formattato,
                    "minima": minima,
                    "massima": massima,
                    "descrizione": ottieni_descrizione(codice),
                }
            )

        dati = {
            "citta": citta,
            "regione": regione,
            "temperatura": temperatura,
            "umidita": umidita,
            "velocita_vento": velocita_vento,
            "descrizione": ottieni_descrizione(codice_corrente),
            "previsioni": previsioni,
        }

    return render_template(
        "index.html",
        dati=dati,
        errore=errore,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
