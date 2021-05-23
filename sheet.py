import streamlit as st
import pandas as pd
import math

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="ID4D", layout="wide"
)

def readfile(uploaded_file):
    uploaded_file.seek(0)
    df = pd.read_excel(uploaded_file,sheet_name=None, engine='openpyxl')
    return df
    
def typehash(sheet):
    #st.write(str(sheet.iloc[0:1].values))
    return hash(str(sheet.iloc[0:1,0:20].values))

st.sidebar.header('Performix Event Viewer')
logo = st.sidebar.empty()
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    f=readfile(uploaded_file)
    settings_map = f["Settings"]
    settings = {}
    for v in settings_map.fillna('').iloc[:,0:2].values:
        settings[str(v[0])]=str(v[1])
    logo.image(settings['Image'])
    st.sidebar.header(settings['Title'])
    st.sidebar.subheader(settings['SubTitle'])
    st.sidebar.write(settings['Description'])
 
    col_map = f["Col_Map"]
    header = [' '.join(v1).strip() for v1 in col_map.fillna('').iloc[:,2:4].values]
    
    group_names = col_map.columns[5:]
    group_dict = {}
    groups = [[' '.join(v1[2:4]).strip(),v1[5:]] for v1 in col_map.fillna('').iloc[:,:].values]
    for g in groups:
        for i,gn in enumerate(g[1]):
            if gn=='y':
                name= group_names[i]
                if name not in group_dict:
                    group_dict[name]=[]
                group_dict[name].append(g[0])

    #st.write(group_dict)
    #sheets=st.sidebar.multiselect("Sheets",list(f.keys()))



    header = [' '.join(v1).strip() for v1 in col_map.fillna('').iloc[:,2:4].values]
    #cols=st.multiselect("Cols",list(header[1:]))
    #idxs = [i-1 for i,v in enumerate(header) if v in cols]

    group_sel = st.selectbox("group",group_names)
    idxs = [i-1 for i,v in enumerate(header) if v in group_dict[group_sel]]
    #st.write(idxs)
    #st.write(group_dict[group_sel])

    #st.write(idxs)
    allsheets=pd.DataFrame()
    s_hash = None
    if True:
        for sheet_key in f.keys():
            sheet = f[sheet_key] 
            if not s_hash:      
                s_hash = typehash(sheet)
            else:
                if s_hash != typehash(sheet):
                    continue
    
            diff = len(sheet.columns)-len(header)
            sheet.columns = header + ['' for d in range(diff)]

            sheet['Date'] = pd.to_datetime(sheet['Date'], errors='coerce')
            sheet = sheet.dropna(subset=['Date'])
            sheet = sheet.set_index('Date')
            #sheet = sheet.iloc[1:,idxs]
            allsheets = allsheets.append(sheet)
        #st.date_input()
        min_d=min(allsheets.index)
        max_d=max(allsheets.index)
        dcol=st.beta_columns(2)
        start_date=dcol[0].date_input("start",min_d,min_d,max_d)
        end_date=dcol[1].date_input("end",max_d,min_d,max_d)
        #st.bar_chart(allsheets.loc[start_date:end_date].dropna())
        fig = go.Figure()
        df = allsheets.loc[start_date:end_date]#.dropna()
        df = df.iloc[1:,idxs]
        df = df.replace(0, np.nan)
        #df = df.set_index('Date')
        trend=st.checkbox('trend')
        #,['','ols','lowess'])
        
        df = df.replace('-',np.nan).applymap(float)
        #st.write(df)

        fig = px.scatter(df, trendline='lowess' if trend else '')
        st.plotly_chart(fig, use_container_width=True)
        lookdate=st.date_input("specific date",start_date,start_date,end_date)
        if lookdate:
            st.write(allsheets.loc[str(lookdate)].replace(np.nan,'').replace(0,''))
        #st.write(df)
        #results = px.get_trendline_results(fig)
        #st.write(results.iloc[0,1].model)

        

