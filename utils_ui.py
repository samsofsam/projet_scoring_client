# -*- coding: utf-8 -*-


import streamlit as st
#import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go


def display_prediction_class(response_predict):
    
    
    
    class_pred = response_predict.json()["class"]
    proba_pred = response_predict.json()["proba"]

    class_pred_inverse = 1 - class_pred
    proba_pred_inverse = 1 - proba_pred
    df_res = pd.DataFrame({"class":[class_pred, class_pred_inverse], "proba":[proba_pred, proba_pred_inverse]})
    
    
    idx_to_labels = {0:"client remboursera son crédit",
                     1:"client ne remboursera pas son crédit"}
    df_res['class'] = df_res['class'].map(idx_to_labels)
    
    """
    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(df_res['class'], df_res['proba'])
    
    ax.set_xlabel('Classe')
    ax.set_ylabel('Probabilité')
    
    # Display the bar chart using Streamlit
    st.pyplot(fig)
    """
    #st.bar_chart(df_res, x="class", y="proba")*
    
    

    value = df_res[df_res["class"]=="client remboursera son crédit"]["proba"].values[0]
    value = int(100*value)
    
    fig = go.Figure(go.Indicator(
        mode = "number+gauge",
        gauge = {'shape': "bullet"},
        delta = {'reference': 100},
        number={'suffix': '%'},
        value = value,
        domain = {'x': [0.1, 0.8], 'y': [0.1, 0.5]}
        ))
    
    fig.update_layout(margin=dict(t=100))
    fig.update_xaxes(range=[0, 1])
    fig.update_layout(title_text="probability credit customer repayment", 
                      title_x=0.1, 
                      title_y=0.8,
                      margin = dict(t=0, b=200, l=0, r=0)
                     )


    st.plotly_chart(fig)
    
        

def process_one_hot_feats(customer_perso, cols):
    
    # pour chaque colonne qu'on veut convertir en categorielle 
    for c in cols:
        
        list_one_hot_feats = []
        
        # recherche des colonnes one-hot correspondante
        for col_cust in customer_perso.columns:
            if c in col_cust:
                list_one_hot_feats.append(col_cust)
        
        # conversion one-hot -> categorielle 
        for x in list_one_hot_feats:
            
            pattern = c+"_"
            value_cat = x.split(pattern)[1]
            
            mask = customer_perso[x]==1
            customer_perso.loc[mask,c] = value_cat
                
            
    return customer_perso



# process all clients with selected user features
def create_data_customer(clients):
    
    cols = ["NAME_FAMILY_STATUS","NAME_EDUCATION_TYPE","NAME_INCOME_TYPE"]
    customer = process_one_hot_feats(clients, cols)
    
    # personnal features 
    features_perso = ["SK_ID_CURR","DAYS_BIRTH", "CODE_GENDER", "NAME_FAMILY_STATUS", 
                       "NAME_EDUCATION_TYPE","AMT_INCOME_TOTAL", "NAME_INCOME_TYPE"]
    customer_perso = customer[features_perso]
    
    # encode Sexe as Female:0, Male:1
    idx_to_labels = {0:"Female",
                     1:"Male"}
    customer_perso['CODE_GENDER'] = customer_perso['CODE_GENDER'].map(idx_to_labels)
    
    # encode age to positive number in year
    customer_perso["DAYS_BIRTH"] = -customer_perso["DAYS_BIRTH"].values//365


    map_feat_perso = {"DAYS_BIRTH":"Age",
                      "CODE_GENDER":"Sexe",
                      "NAME_FAMILY_STATUS":"Marital status",
                      "NAME_EDUCATION_TYPE":"Highest education level",
                      "NAME_INCOME_TYPE": "Employment status",
                      "AMT_INCOME_TOTAL": "Income"
                      }
    
    customer_perso = customer_perso.rename(columns=map_feat_perso)
        
        
    ## INFO RELATIF AU CREDIT ##    
    
    # on veut les infos suivantes:
        
    # le montant total du crédit que le client a demandé
    # l'annuité du crédit i.e le montant mensuel a remboursé par le client
    # si le client à d'autres crédit actif en cours ou non
    
    
    # AMT_CREDIT: montant total du crédit
    # AMT_INCOME_PERC: AMT_ANNUITY / AMT_INCOME_TOTAL
    # BURO_CREDIT_ACTIVE_Active_MEAN: nombre moyen de crédit en cours que le client n'a pas encore remboursé)
    
    features_credit = ["SK_ID_CURR", "AMT_CREDIT", "ANNUITY_INCOME_PERC", "AMT_INCOME_TOTAL",
                       "BURO_CREDIT_ACTIVE_Active_MEAN"]
    
    customer_credit = customer[features_credit]
    
    customer_credit["AMT_ANNUITY"] = customer_credit["ANNUITY_INCOME_PERC"]*customer_credit["AMT_INCOME_TOTAL"]
    
    customer_credit["customer has other active credits in progress ?"] = customer_credit["BURO_CREDIT_ACTIVE_Active_MEAN"].apply(lambda s: "No" if s == 0 else "Yes")
    
    customer_credit = customer_credit.drop(columns=["AMT_INCOME_TOTAL","ANNUITY_INCOME_PERC",
                                                    "BURO_CREDIT_ACTIVE_Active_MEAN"]
                                                    )
    
    map_feat_credit = {"AMT_CREDIT":"Amount of the credit",
                      "AMT_ANNUITY":"Amount of the annuity"
                      }
    
    customer_credit = customer_credit.rename(columns=map_feat_credit)

    
    customer_res = pd.merge(customer_perso,customer_credit,on="SK_ID_CURR")
    
    
    return customer_res



def display_customer_info(customer_res, customer_id, user_selected_feats):
    
    customer_one_ = customer_res[customer_res["SK_ID_CURR"]==customer_id]
    
    st.subheader("Customer Information")
    for x in customer_one_.columns:
        if x in user_selected_feats:
            st.write(x + " : ", customer_one_[x].values[0])
        


def display_quanti(customer_res, current_customer, feat_quanti, num_fig):
    
    st.subheader("Distribution of "+ feat_quanti)

    # Display the histogram using Matplotlib
    fig1 = plt.figure(num= num_fig, figsize=(8, 6))
    sns.kdeplot(customer_res[feat_quanti], color='skyblue', fill=True, label='all customers')
    plt.axvline(current_customer[feat_quanti].values[0], color='red', linestyle='--', label='Selected customer')
    #plt.title('Distribution of '+feat_quanti)
    plt.xlabel(feat_quanti)
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig1)


def display_quali(customer_res, current_customer, feat_cat, num_fig):
    
    st.subheader('Distribution of '+ feat_cat)
    
    value_cust = current_customer[feat_cat].values[0]
    
    color_mapping = dict()
    
    for val in customer_res[feat_cat].unique():
        
        if val == value_cust:
            color = 'red'
        else:
            color = 'skyblue'
        
        color_mapping[val] = color
        
    legend_dict = {"Selected customer values":"red", "Others customers values":"skyblue"}
    
    fig2 = plt.figure(num=num_fig, figsize=(8, 6))
    sns.barplot(x=round(customer_res[feat_cat].value_counts(normalize=True)*100,3).index, 
                y =round(customer_res[feat_cat].value_counts(normalize=True)*100,3).values,
                palette=color_mapping.values())
    
    legend_labels = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label)
                 for label, color in legend_dict.items()]
    
    plt.legend(handles=legend_labels, title_fontsize='15')

    plt.xlabel(feat_cat)
    plt.ylabel("frequency %")
    #plt.title('Distribution of '+feat_cat)
    
    # Display the count plot using st.pyplot
    st.pyplot(fig2)
    


def display_comparaison(customer_res, idx_client, selected_cust_features):
        
    current_customer = customer_res[customer_res["SK_ID_CURR"]==idx_client]
    
    list_feats_quanti = ["Age", "Income", "Amount of the credit", "Amount of the annuity"]
    #list_feats_quali = ["Employment status", "customer has other active credits in progress ?"]
    
    
    for i in range(len(selected_cust_features)):
        feat = selected_cust_features[i]
        if feat in list_feats_quanti:
            display_quanti(customer_res, current_customer, feat, num_fig=i)
        else:
            display_quali(customer_res, current_customer, feat, num_fig=i)
