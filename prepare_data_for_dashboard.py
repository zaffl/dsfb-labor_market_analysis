import pandas as pd
import numpy as np

import os
import requests

import warnings
warnings.filterwarnings("ignore")

path = "./datasets/"

def data_loading():

    print("Data Loading ...")

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
    ]

    # Create datasets dir
    if not os.path.exists(path):
        os.mkdir(path)

    # Retrive datasets
    for dataset in datasets:
        if not os.path.exists(path + dataset["filename"]):
            r = requests.get(dataset["url"], allow_redirects=True)
            open(path + dataset["filename"], 'wb').write(r.content)

    df_lav_att = pd.read_csv(path + "Rapporti_di_lavoro_attivati.csv")
    df_lav_ces = pd.read_csv(path + "Rapporti_di_lavoro_cessati.csv")
    df_ateco = pd.read_excel(path + "Struttura-ATECO-2007-aggiornamento-2022.xlsx", engine="openpyxl")

    return df_lav_att, df_lav_ces, df_ateco



def data_cleaning(df_lav_att, df_lav_ces, df_ateco):

    print("Data Cleaning ...")

    df_lav_att_clean = df_lav_att.copy()
    df_lav_ces_clean = df_lav_ces.copy()
    df_ateco_clean = df_ateco.copy()

    df_lav_att_clean['DATA'] = pd.to_datetime(df_lav_att_clean['DATA'], format="%d/%m/%Y", errors='coerce')
    df_lav_att_clean.dropna(subset=["DATA"], inplace=True)
    df_lav_att_clean['DATA'] = df_lav_att_clean['DATA'].apply(lambda x: x.strftime('%Y-%m'))

    df_lav_ces_clean['DATA'] = pd.to_datetime(df_lav_ces_clean['DATA'], format="%d/%m/%Y", errors='coerce')
    df_lav_ces_clean.dropna(subset=["DATA"], inplace=True)
    df_lav_ces_clean['DATA'] = df_lav_ces_clean['DATA'].apply(lambda x: x.strftime('%Y-%m'))

    # Remove record with Date < 01/2009 and Date > 12/2021
    from_date = "2009-01-01"
    to_date = "2021-12-31"
    df_lav_att_clean = df_lav_att_clean.loc[(df_lav_att_clean["DATA"]>=from_date) & (df_lav_att_clean["DATA"]<=to_date)]
    df_lav_ces_clean = df_lav_ces_clean.loc[(df_lav_ces_clean["DATA"]>=from_date) & (df_lav_ces_clean["DATA"]<=to_date)]

    # Remove punctuations
    df_lav_att_clean["SETTOREECONOMICODETTAGLIO"] = df_lav_att_clean["SETTOREECONOMICODETTAGLIO"].str.replace(r'[^\w\s]', '')
    df_lav_ces_clean["SETTOREECONOMICODETTAGLIO"] = df_lav_ces_clean["SETTOREECONOMICODETTAGLIO"].str.replace(r'[^\w\s]', '')

    # Fill null values of the column MODALITALAVORO
    df_lav_att_clean["MODALITALAVORO"].fillna("SCONOSCIUTO", inplace=True)
    # Drop null values
    df_lav_att_clean.dropna(inplace=True)
    df_lav_ces_clean.dropna(inplace=True)

    # Rename some columns
    df_ateco_clean.rename(columns={"Titolo Ateco 2007 aggiornamento 2022" : "DescrizioneAteco"}, inplace=True)  
    df_ateco_clean.columns.values[0] = "CodAteco"
    

    # Remove punctuations
    df_ateco_clean["DescrizioneAteco"] = df_ateco_clean["DescrizioneAteco"].str.replace(r'[^\w\s]', '')

    # Create new features
    df_ateco_clean.insert(2, "MacroAteco", "")
    df_ateco_clean.insert(3, "MacroDescrizione", "")
    df_ateco_clean["MacroAteco"] = df_ateco_clean.apply(lambda x: x["CodAteco"] if x["CodAteco"].isalpha() else "", axis=1)
    df_ateco_clean["MacroDescrizione"] = df_ateco_clean.apply(lambda x: x["DescrizioneAteco"] if x["CodAteco"].isalpha() else "", axis=1)

    macro_cod = ""
    macro_desc = ""
    for x in df_ateco_clean.index:
        if df_ateco_clean["MacroAteco"][x] == "":
            df_ateco_clean["MacroAteco"][x] = macro_cod
            df_ateco_clean["MacroDescrizione"][x] = macro_desc
        else:
            macro_cod = df_ateco_clean["MacroAteco"][x]
            macro_desc = df_ateco_clean["MacroDescrizione"][x]

    # Delete unwanted duplicates (e.g. CodAteco 90.1 and 90.1.0, are the same)
    df_ateco_clean.drop_duplicates(subset=['DescrizioneAteco'], inplace=True)

    # Merge
    df_lav_att_clean = pd.merge(df_lav_att_clean, df_ateco_clean, how="left", left_on="SETTOREECONOMICODETTAGLIO", right_on="DescrizioneAteco")
    df_lav_ces_clean = pd.merge(df_lav_ces_clean, df_ateco_clean, how="left", left_on="SETTOREECONOMICODETTAGLIO", right_on="DescrizioneAteco")

    return df_lav_att_clean, df_lav_ces_clean, df_ateco_clean


def prepare_kpi_economic_sector(df_lav_att, df_lav_ces):

    print("Preparing data for KPI Economic Sector ...")

    # Prepare Data
    df_att = df_lav_att.copy()
    df_att = df_att.groupby(['MacroDescrizione', 'DATA'])['MacroDescrizione'].count().to_frame()
    df_att.columns.values[0] = "COUNT" 
    df_att.reset_index(inplace = True)
    df_att.columns.values[0] = "MacroDescrizione"

    df_ces = df_lav_ces.copy()
    df_ces = df_ces.groupby(['MacroDescrizione', 'DATA'])['MacroDescrizione'].count().to_frame()
    df_ces.columns.values[0] = "COUNT" 
    df_ces.reset_index(inplace = True)
    df_ces.columns.values[0] = "MacroDescrizione"

    df_att.sort_values(["MacroDescrizione", "DATA"], inplace=True)
    df_ces.sort_values(["MacroDescrizione", "DATA"], inplace=True)

    df = pd.DataFrame()
    df["DATA"] = df_lav_att["DATA"]
    df["MacroDescrizione"] = df_att["MacroDescrizione"]
    df["DIFF"] = df_att["COUNT"] - df_ces["COUNT"]
    df.sort_values("DIFF", inplace=True, ascending=False)
    return df

def prepare_kpi_act_ces_contracts(df_att_, df_ces_):

    print("Preparing data for KPI Activated and Ceased Contracts ...")

    dfa = df_att_.copy()
    dfc = df_ces_.copy()

    group_activated = dfa.groupby(["GENERE", "DATA"])["GENERE"].count().to_frame()
    group_activated.columns.values[0] = "COUNT" 
    group_activated.reset_index(inplace = True)
    group_activated.columns.values[0] = "GENERE"

    group_ceased = dfc.groupby(["GENERE", "DATA"])["GENERE"].count().to_frame()
    group_ceased.columns.values[0] = "COUNT" 
    group_ceased.reset_index(inplace = True)
    group_ceased.columns.values[0] = "GENERE"

    return group_activated, group_ceased

def prepare_kpi_medium_age_contracts(df_att_):

    print("Preparing data for KPI Medium Age ...")

    dfa = df_att_.copy()

    age_activated = dfa.groupby(["GENERE", "DATA"])["ETA"].mean().to_frame()
    age_activated.columns.values[0] = "AVG" 
    age_activated.reset_index(inplace = True)
    age_activated.columns.values[0] = "GENERE"

    return age_activated

def prepare_charts(df_att_, df_ces_):

    print("Preparing data for Charts ...")

    dfa = df_att_.copy()
    dfc = df_ces_.copy()

    dfa = dfa.groupby(["DATA"])["DATA"].count().to_frame()
    dfa.columns.values[0] = "COUNT" 
    dfa.reset_index(inplace = True)
    dfa.columns.values[0] = "DATA"
    dfa.sort_values("DATA", inplace=True)

    dfc = dfc.groupby(["DATA"])["DATA"].count().to_frame()
    dfc.columns.values[0] = "COUNT" 
    dfc.reset_index(inplace = True)
    dfc.columns.values[0] = "DATA"
    dfc.sort_values("DATA", inplace=True)

    df = pd.DataFrame()
    df["DATA"] = dfa["DATA"]
    df["ACTIVATED"] = dfa["COUNT"]
    df["CEASED"] = dfc["COUNT"]
    df["DIFF"] = dfa["COUNT"] - dfc["COUNT"]

    return df


df_lav_att, df_lav_ces, df_ateco = data_loading()
df_lav_att_clean, df_lav_ces_clean, df_ateco_clean = data_cleaning(df_lav_att, df_lav_ces, df_ateco)
df_eco = prepare_kpi_economic_sector(df_lav_att_clean, df_lav_ces_clean)
group_activated, group_ceased = prepare_kpi_act_ces_contracts(df_lav_att_clean, df_lav_ces_clean)
age_activated = prepare_kpi_medium_age_contracts(df_lav_att_clean)
df_charts = prepare_charts(df_lav_att_clean, df_lav_ces_clean)


df_eco.to_csv(path + "kpi_eco.csv")
group_activated.to_csv(path + "activated.csv")
group_ceased.to_csv(path + "ceased.csv")
age_activated.to_csv(path + "kpi_age.csv")
df_charts.to_csv(path + "charts.csv")