import streamlit as st
import pandas as pd
import numpy as np

import os
import requests

# Basic Page Configuration
st.set_page_config(page_title = 'Job Market Dashboard', layout='wide', page_icon='')

# Prepare Data #################################################################################################################################################

@st.cache(persist=True)
def data_loading():
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



@st.cache(persist=True)
def data_cleaning(df_lav_att, df_lav_ces, df_ateco):

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



@st.cache(persist=True)
def prepare_kpi_economic_sector(df_lav_att, df_lav_ces):
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

    df = pd.DataFrame()
    df["DATA"] = df_lav_att["DATA"]
    df["MacroDescrizione"] = df_att["MacroDescrizione"]
    df["DIFF"] = df_att["COUNT"] - df_ces["COUNT"]
    df.sort_values("DIFF", inplace=True, ascending=False)
    return df

def get_kpi_economic_sector(df_, start_date, end_date):
    df = df_.copy()

    df = df.loc[(df["DATA"]>=str(start_date)) & (df["DATA"]<=str(end_date))]
    df = df.groupby(['MacroDescrizione'])['MacroDescrizione'].count().to_frame()
    df.columns.values[0] = "DIFF" 
    df.reset_index(inplace = True)
    df.columns.values[0] = "MacroDescrizione"
    df.dropna(inplace=True)
    df.sort_values("DIFF", inplace=True, ascending=False)

    df_best3 = df.head(3)
    df_worst3 = df.tail(3)
    return df_best3, df_worst3

df_lav_att, df_lav_ces, df_ateco = data_loading()
df_lav_att_clean, df_lav_ces_clean, df_ateco_clean = data_cleaning(df_lav_att, df_lav_ces, df_ateco)
df_eco = prepare_kpi_economic_sector(df_lav_att_clean, df_lav_ces_clean)



# Streamlit Page ###############################################################################################################################################

def write_title(text):
    st.markdown(f"<p style='font-weight: bold; font-size: 30pt' align='center'>{text}</p>", unsafe_allow_html=True)

def apply_filter(df, start, end):
    df





# KPI1 --> Male / Female activated and ceased contracts
# KPI2 --> Medium Age of activated and ceased contracts
# KPI3 --> 3 Best sectors of the years and 3 worst sectors of the years
start, end = st.slider(label="", min_value=2011, max_value=2021, value=(2011, 2021))

df_best3, df_worst3 = get_kpi_economic_sector(df_eco, start, end)

value = 0

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    write_title("Created Job")
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #66c2ff' align='center'>{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #ff9999' align='center'>{value}</p>", unsafe_allow_html=True)
    

with kpi2:
    write_title("Medium Age Contracts")
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #66c2ff' align='center'>{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #ff9999' align='center'>{value}</p>", unsafe_allow_html=True)
    #st.selectbox(label="", options=["TIPO CONTRATTO 1", "TIPO CONTRATTO 2"])
    
with kpi3:
    eco1 = df_best3["MacroDescrizione"].iloc[0]
    value1 = df_best3["DIFF"].iloc[0]
    
    eco2 = df_best3["MacroDescrizione"].iloc[1]
    value2 = df_best3["DIFF"].iloc[1]
    
    eco3 = df_best3["MacroDescrizione"].iloc[2]
    value3 = df_best3["DIFF"].iloc[2]
    
    eco4 = df_worst3["MacroDescrizione"].iloc[0]
    value4 = df_worst3["DIFF"].iloc[0]
    
    eco5 = df_worst3["MacroDescrizione"].iloc[1]
    value5 = df_worst3["DIFF"].iloc[1]
    
    eco6 = df_worst3["MacroDescrizione"].iloc[2]
    value6 = df_worst3["DIFF"].iloc[2]

    write_title("Best / Worst Sector")
    st.markdown(f"<p style='font-weight: bold; font-size: 10pt; color: #009900' align='center'>{eco1}&nbsp;+{value1}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 10pt; color: #009900' align='center'>{eco2}&nbsp;+{value2}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 10pt; color: #009900' align='center'>{eco3}&nbsp;+{value3}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 10pt; color: #ff3333' align='center'>{eco4}&nbsp;+{value4}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 10pt; color: #ff3333' align='center'>{eco5}&nbsp;+{value5}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 10pt; color: #ff3333' align='center'>{eco6}&nbsp;+{value6}</p>", unsafe_allow_html=True)
    
st.markdown("""---""") 

first_chart, second_chart = st.columns(2)

with first_chart:
    write_title("Chart 1")
    chart_data = pd.DataFrame(np.random.randn(20, 3),columns=['a', 'b', 'c'])
    st.line_chart(chart_data)

with second_chart:
    write_title("Chart 2")
    chart_data = pd.DataFrame(np.random.randn(20, 3),columns=['a', 'b', 'c'])
    st.line_chart(chart_data)

