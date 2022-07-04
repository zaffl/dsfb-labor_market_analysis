import os
import requests

path = "./datasets/"

dataset1 = "Rapporti_di_lavoro_attivati.csv"
dataset2 = "6f0f7122-3312-47ac-a292-7a647986387e.csv"
dataset3 = "Rapporti_di_lavoro_cessati.csv"

if not os.path.exists(path):
    os.mkdir(path)

if not os.path.exists(path + dataset1):
    r = requests.get("https://dati.lombardia.it/api/views/qbau-cyuc/rows.csv?accessType=DOWNLOAD", allow_redirects=True)
    open(path + dataset1, 'wb').write(r.content)

if not os.path.exists(path + dataset2):
    r = requests.get("https://indicepa.gov.it/ipa-dati/datastore/dump/6f0f7122-3312-47ac-a292-7a647986387e?bom=True", allow_redirects=True)
    open(path + dataset2, 'wb').write(r.content)

if not os.path.exists(path + dataset3):
    r = requests.get("https://www.dati.lombardia.it/api/views/nwz3-p6vm/rows.csv?accessType=DOWNLOAD", allow_redirects=True)
    open(path + dataset1, 'wb').write(r.content)


