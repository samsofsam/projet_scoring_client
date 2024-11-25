# -*- coding: utf-8 -*-



from fastapi import FastAPI
import uvicorn
import pandas as pd
import pickle
import lime.lime_tabular  
import numpy as np    

from pydantic import BaseModel

# Declaring our FastAPI instance
app = FastAPI()
 
# Defining path operation for root endpoint
@app.get('/')
def main():
    return {'message': 'Welcome to my API'}
 
# Defining path operation for /name endpoint
#@app.get('/{name}')
#def hello_name(name : str): 
    # Defining a function that takes only string as input and output the
    # following message. 
    #return {'message': f'Welcome to GeeksforGeeks!, {name}'}



class request_body(BaseModel):
    idx_client : int
    

clients = pd.read_csv("clients_api.csv")

path_model = "model_finale.pkl"

best_model = pickle.load(open(path_model, 'rb'))

best_seuil = 0.16
    

@app.post('/predict')
def predict(data : request_body):
    
    test_data = clients[clients["SK_ID_CURR"]==data.idx_client].drop(columns="SK_ID_CURR")
    test_data = test_data.to_numpy()
        
    # probabilité des classes 0 et 1
    #y_pred_proba = best_model.predict_proba(test_data)
    
    proba_class_0 = best_model.predict_proba(test_data)[0][0]   
    proba_class_1 = best_model.predict_proba(test_data)[0][1]
    
    if proba_class_1 >= best_seuil:
        class_idx = 1
        class_proba = proba_class_1
    else:
        class_idx = 0
        class_proba = proba_class_0
    
    class_proba = round(class_proba,2)
    
    # prédiction de la classe selon le seuil
    # class_idx = proba_to_class(y_pred_proba, best_seuil)
    #class_idx =  class_idx[0]
    
    # probabilité de la classe prédite
    #proba_class = y_pred_proba[class_idx]
    
    return { 'class' : class_idx, 'proba': class_proba}
    



