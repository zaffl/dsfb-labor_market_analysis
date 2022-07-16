import os
import requests

# Retriving all dataset from online sources if we don't have them

path = "./datasets/"

# Retriving all datasets from online sources if we don't have them
import os
import requests

path = "./datasets/"

datasets = [
    {# Activated Contracts Dataset
        'url' : 'https://dati.lombardia.it/api/views/qbau-cyuc/rows.csv?accessType=DOWNLOAD',
        'filename' : 'Rapporti_di_lavoro_attivati.csv'
    },
    {# Ceased Contracts Dataset
        'url' : 'https://www.dati.lombardia.it/api/views/nwz3-p6vm/rows.csv?accessType=DOWNLOAD',
        'filename' : 'Rapporti_di_lavoro_cessati.csv'
    },
    {# ATECO Code Dataset
        'url' : 'https://www.istat.it/it/files//2022/03/Struttura-ATECO-2007-aggiornamento-2022.xlsx',
        'filename' : 'Struttura-ATECO-2007-aggiornamento-2022.xlsx'
    },
    {# GeoJSON border coordinates of Italy provinces from github
        'url' : 'https://dati.lombardia.it/api/views/qbau-cyuc/rows.csv?accessType=DOWNLOAD',
        'filename' : 'limits_IT_provinces.geojson'
    },   
]

# Create datasets dir
if not os.path.exists(path):
    os.mkdir(path)

# Retrive datasets
for dataset in datasets:
    if not os.path.exists(path + dataset["filename"]):
        r = requests.get(dataset["url"], allow_redirects=True)
        open(path + dataset["filename"], 'wb').write(r.content)