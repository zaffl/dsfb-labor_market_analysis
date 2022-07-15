import os
import requests

# Retriving all dataset from online sources if we don't have them

path = "./datasets/"

dataset_att = "Rapporti_di_lavoro_attivati.csv"
dataset2 = "6f0f7122-3312-47ac-a292-7a647986387e.csv"
dataset3 = "Rapporti_di_lavoro_cessati.csv"
dataset_geojson = "limits_IT_provinces.geojson"

# Create dataset dir
if not os.path.exists(path):
    os.mkdir(path)

# Get Activated Contracts Dataset
if not os.path.exists(path + dataset_att):
    r = requests.get("https://dati.lombardia.it/api/views/qbau-cyuc/rows.csv?accessType=DOWNLOAD", allow_redirects=True)
    open(path + dataset_att, 'wb').write(r.content)

# Get Ceased Contracts Dataset
if not os.path.exists(path + dataset3):
    r = requests.get("https://www.dati.lombardia.it/api/views/nwz3-p6vm/rows.csv?accessType=DOWNLOAD", allow_redirects=True)
    open(path + dataset1, 'wb').write(r.content)

# Get ATECO Code Dataset
if not os.path.exists(path + dataset2):
    r = requests.get("https://indicepa.gov.it/ipa-dati/datastore/dump/6f0f7122-3312-47ac-a292-7a647986387e?bom=True", allow_redirects=True)
    open(path + dataset2, 'wb').write(r.content)

# Get GeoJSON border coordinates of Italy provinces from github
if not os.path.exists(path + dataset_geojson):
    r = requests.get('https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_provinces.geojson', allow_redirects=True)
    open(path + dataset_geojson, 'wb').write(r.content)
