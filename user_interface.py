# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 17:06:25 2023

@author: sofia
"""

import streamlit as st
#import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from utils_ui import *

# API = Backend + Frontend 

# Backend:
# le code contenant les fonctions/services (endpoints) + une documentation permettant
# d'expliquer ce que fait chaque fonction et comment les réutiliser pour une autre Application 
# utilisateur du backend -> souvent un développeur qui souhaite reprendre des fonctions pour sa 
# propre appli


# Frontend:
# on va créer une interface graphique pour l'utilisateur (UI) permettant 
# de simplifier l'utilisation de nos services (prédiction de la classe d'un client 
# et de l'interprétabilité)
# utilisateur frontend -> une personne sans quelconque

    
    

# Make page
st.set_page_config(page_title="Credit Customer Prediction Project")
#st.header("Credit Customer Prediction Project")


    
clients = pd.read_csv("clients_api.csv")

list_id_clients = clients["SK_ID_CURR"].unique()


# idx_client = st.sidebar.text_input("Enter the ID of the client : ")
idx_client = st.sidebar.selectbox('Select a client', list_id_clients)
idx_client = int(idx_client)


all_features = ["Age","Employment status", "Income", "Amount of the credit",
                "Amount of the annuity", "customer has other active credits in progress ?"]

# Allow user to select multiple features
selected_cust_features = st.sidebar.multiselect('Select Customer Information', all_features)


customer_res = create_data_customer(clients)


# display customer information
display_customer_info(customer_res, idx_client, selected_cust_features)


# Comparaison Customer Information
display_comparaison(customer_res, idx_client, selected_cust_features)




if st.sidebar.button('Run Prediction'):
    
    # url de l'API hébergé dans le cloud
    # root_url_backend = 'https://api-predict.onrender.com' 
    
    # url de l'API sur l'ordi
    root_url_backend = 'http://127.0.0.1:8000' 

    
    # url des endpoints
    url_endpoint_predict = root_url_backend + '/predict'
    
    response_predict = requests.post(url_endpoint_predict, json={'idx_client': idx_client})
    
    
    st.subheader('Results of the prediction')
    
    
    st.write("Class prediction of the customer: ",idx_client)
    display_prediction_class(response_predict)
    
    


    
    
    
    
