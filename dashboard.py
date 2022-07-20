import streamlit as st
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

import os
import requests

path = './datasets/'

# Basic Page Configuration
st.set_page_config(page_title = 'Job Market Dashboard', layout='wide', page_icon='')

# Prepare Data #################################################################################################################################################

@st.cache(persist=True)
def data_loading():
    df_eco = pd.read_csv(path + "kpi_eco.csv")
    group_activated = pd.read_csv(path + "activated.csv")
    group_ceased = pd.read_csv(path + "ceased.csv")
    age_activated = pd.read_csv(path + "kpi_age.csv")
    df_charts = pd.read_csv(path + "charts.csv")

    return df_eco, group_activated, group_ceased, age_activated, df_charts

def get_kpi_economic_sector(df_, start_date, end_date):
    df = df_.copy()
    df = df.loc[(df["DATA"]>=str(start_date)) & (df["DATA"]<=str(end_date))]
    
    df = df.groupby(['MacroDescrizione'])['DIFF'].sum().to_frame()
    #df.columns.values[0] = "DIFF" 
    df.reset_index(inplace = True)
    df.columns.values[0] = "MacroDescrizione"
    df.dropna(inplace=True)
    df.sort_values("DIFF", inplace=True, ascending=False)

    df_best3 = df.head(3)
    df_worst3 = df.tail(3)
    return df_best3, df_worst3

def get_kpi_act_ces_contracts(df_att_, df_ces_, start_date, end_date):
    dfa = df_att_.copy()
    dfc = df_ces_.copy()

    dfa = dfa.loc[(dfa["DATA"]>=str(start_date)) & (dfa["DATA"]<=str(end_date))]
    dfc = dfc.loc[(dfc["DATA"]>=str(start_date)) & (dfc["DATA"]<=str(end_date))]

    dfa = dfa.groupby(["GENERE"])["COUNT"].sum().to_frame()
    dfa.columns.values[0] = "COUNT" 
    dfa.reset_index(inplace = True)
    dfa.columns.values[0] = "GENERE"
    male_activated = dfa.loc[(dfa["GENERE"] == "M")]
    male_activated = male_activated["COUNT"].values[0]
    female_activated = dfa.loc[(dfa["GENERE"] == "F")]
    female_activated = female_activated["COUNT"].values[0]

    dfc = dfc.groupby(["GENERE"])["COUNT"].sum().to_frame()
    dfc.columns.values[0] = "COUNT" 
    dfc.reset_index(inplace = True)
    dfc.columns.values[0] = "GENERE"
    male_ceased = dfc.loc[(dfc["GENERE"] == "M")]
    male_ceased = male_ceased["COUNT"].values[0]
    female_ceased = dfc.loc[(dfc["GENERE"] == "F")]
    female_ceased = female_ceased["COUNT"].values[0]

    return male_activated, male_ceased, female_activated, female_ceased

def get_kpi_medium_age_contracts(df_att_, start_date, end_date):
    dfa = df_att_.copy()

    dfa = dfa.loc[(dfa["DATA"]>=str(start_date)) & (dfa["DATA"]<=str(end_date))]

    dfa = dfa.groupby(["GENERE"])["AVG"].mean().to_frame()
    dfa.columns.values[0] = "AVG" 
    dfa.reset_index(inplace = True)
    dfa.columns.values[0] = "GENERE"

    medium_male_age = dfa.loc[(dfa["GENERE"] == "M")]
    medium_male_age = round(medium_male_age["AVG"].values[0], 2)
    medium_female_age = dfa.loc[(dfa["GENERE"] == "F")]
    medium_female_age = round(medium_female_age["AVG"].values[0], 2)

    return medium_male_age, medium_female_age


def get_charts(df_charts, start_date, end_date):
    df_chart = df_charts.copy()
    df_chart = df_chart.loc[(df_chart["DATA"]>=str(start_date)) & (df_chart["DATA"]<=str(end_date))]
    return df_chart


if not os.path.exists(path + "kpi_eco.csv") or not os.path.exists(path + "activated.csv") or not os.path.exists(path + "ceased.csv") or not os.path.exists(path + "kpi_age.csv") or not os.path.exists(path + "charts.csv"):
    os.system("prepare_data_for_dashboard.py")

df_eco, group_activated, group_ceased, age_activated, df_charts = data_loading()

# Streamlit Page ###############################################################################################################################################

def write_title(text):
    st.markdown(f"<p style='font-weight: bold; font-size: 30pt' align='center'>{text}</p>", unsafe_allow_html=True)


# KPI1 --> Male / Female activated and ceased contracts
# KPI2 --> Medium Age of activated contracts
# KPI3 --> 3 Best sectors of the years and 3 worst sectors of the years
start, end = st.slider(label="", min_value=2011, max_value=2021, value=(2011, 2021), step=1)
    
try:
    df_best3, df_worst3 = get_kpi_economic_sector(df_eco, start, end)
    male_activated, male_ceased, female_activated, female_ceased = get_kpi_act_ces_contracts(group_activated, group_ceased, start, end)
    medium_male_age, medium_female_age = get_kpi_medium_age_contracts(age_activated, start, end)
    df_chart = get_charts(df_charts, start, end)


    value = 0

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        write_title("Activated / Ceased Contracts")
        st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #66c2ff' align='center'>+{male_activated}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-{male_ceased}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #ff9999' align='center'>+{female_activated}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-{female_ceased}</p>", unsafe_allow_html=True)
        
    with kpi2:
        write_title("Medium Age Activated Contracts")
        st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #66c2ff' align='center'>{medium_male_age}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #ff9999' align='center'>{medium_female_age}</p>", unsafe_allow_html=True)
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
        st.markdown(f"<p style='font-weight: bold; font-size: 12pt; color: #009900' align='center'>{eco1}&nbsp;{value1}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight: bold; font-size: 12pt; color: #009900' align='center'>{eco2}&nbsp;{value2}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight: bold; font-size: 12pt; color: #009900' align='center'>{eco3}&nbsp;{value3}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight: bold; font-size: 12pt; color: rgb(255, 75, 75)' align='center'>{eco4}&nbsp;{value4}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight: bold; font-size: 12pt; color: rgb(255, 75, 75)' align='center'>{eco5}&nbsp;{value5}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight: bold; font-size: 12pt; color: rgb(255, 75, 75)' align='center'>{eco6}&nbsp;{value6}</p>", unsafe_allow_html=True)
        
    st.markdown("""---""") 

    first_chart, second_chart = st.columns(2)

    with first_chart:
        write_title("Activated / Ceased Contracts")
        df_chart1 = pd.DataFrame()
        df_chart1["DATA"] = df_chart["DATA"]
        df_chart1["ACTIVATED"] = df_chart["ACTIVATED"]
        df_chart1["CEASED"] = df_chart["CEASED"]

        fig = px.line(        
            df_chart1,
            x = "DATA",
            y = ["ACTIVATED", "CEASED"],
            width = 900,
            height = 400
        )
        st.plotly_chart(fig)

        #df_chart1.set_index("DATA", inplace=True)
        #st.line_chart(df_chart1)

    with second_chart:
        write_title("New Jobs Created")
        df_chart2 = pd.DataFrame()
        df_chart2["DATA"] = df_chart["DATA"]
        df_chart2["DIFF"] = df_chart["DIFF"]

        fig = px.line(        
            df_chart2,
            x = "DATA",
            y = "DIFF",
            width = 900,
            height = 400
        )
        st.plotly_chart(fig)

        #st.line_chart(df_chart2)
        #df_chart2.set_index("DATA", inplace=True)

    st.markdown("""---""")

except:
    st.error("Please select start date different from end date")