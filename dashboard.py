import streamlit as st

# Basic Page Configuration
st.set_page_config(page_title = 'Job Market Dashboard', layout='wide', page_icon='')

# Title
#st.title("Job Market Dashboard")

# KPI1 --> Male / Female activated and ceased contracts
# KPI2 --> Medium Age of activated and ceased contracts
# KPI3 --> 3 Best sectors of the years and 3 worst sectors of the years
kpi1, kpi2, kpi3 = st.columns(3)

def slider():
    st.write("PROVA")
    
with kpi1:
    title = "Created Job"
    value= 1234
    st.markdown(f"<p style='font-weight: bold; font-size: 30pt' align='center'>{title}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #66c2ff' align='center'>{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #ff9999' align='center'>{value}</p>", unsafe_allow_html=True)

with kpi2:
    title = "Medium Age Contracts"
    value= 1234
    st.markdown(f"<p style='font-weight: bold; font-size: 30pt' align='center'>{title}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #66c2ff' align='center'>{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 25pt; color: #ff9999' align='center'>{value}</p>", unsafe_allow_html=True)
    st.selectbox(label="", options=["TIPO CONTRATTO 1", "TIPO CONTRATTO 2"])
    
with kpi3:
    title = "Best / Worst Sector"
    value= 1234
    st.markdown(f"<p style='font-weight: bold; font-size: 30pt' align='center'>{title}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 15pt; color: #009900' align='center'>Economic Sector 1&nbsp;+{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 15pt; color: #009900' align='center'>Economic Sector 2&nbsp;+{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 15pt; color: #009900' align='center'>Economic Sector 3&nbsp;+{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 15pt; color: #ff3333' align='center'>Economic Sector 4&nbsp;-{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 15pt; color: #ff3333' align='center'>Economic Sector 5&nbsp;-{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: bold; font-size: 15pt; color: #ff3333' align='center'>Economic Sector 6&nbsp;-{value}</p>", unsafe_allow_html=True)
    


st.select_slider(label="", options=[2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021], on_change=slider)