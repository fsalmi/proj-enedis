import dash
import dash_table
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pathlib
import os
import pandas as pd
import numpy as np
import re
import pickle 
from dash_table import DataTable

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
app.config["suppress_callback_exceptions"] = True

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
df = pd.read_csv("block_tot_2.csv")


#df = pd.read_csv('dataset_final.csv')

markdown_text1 = '''
##### Prédiction de la consommation d\'électricité pour différents profils avec un pas de 30 minutes
Nous avons utilisé un jeu de [données] (https://www.kaggle.com/jeanmidev/smart-meters-in-london) contenant la consommation électrique de 5567 résidences à Londres avec un pas de 30 minutes. 
Le but de notre étude était de prédire cette consommation pour chaque profil avec une grande précision. Pour cela, nous avons d'abord extrait la tendance et la saisonnalité de la série temporelle. Ensuite nous avons traité les deux composantes séparément: un réseau de neurones LSTM pour prédire la tendance et une décomposition de Fourier pour recomposer la saisonnalité. 
Une modulation en amplitude a été détectée dans la saisonnalité, nous l'avons rajoutée à la saisonnalité recomposée, elle correspond sûrement aux différentes saisons climatiques. 
Le modèle a été entraîné sur une période de 14 mois et a été testé sur une période de 6 mois. 
Cette démarche a été réalisée pour trois profils différents de clients (Classe riche, classe moyenne et classe défavorisée). 

Ci-dessous, sont représentées les valeurs réelles et les prédictions correspodantes pour les trois profils différents. 
Une fenêtre glissante permet d'observer de manière particulière avec une échelle journalière, hebdomadaire ou mensuelle. 
A titre de comparaison, nous avons aussi proposé les prédictions sans les modulations d'amplitudes sur la saisonnalité qui sont moins bonnes qu'avec la modulation. 

Cette étude pourra être améliorée en prenant en compte certaines particularités de la vie quotidienne comme par exemple les congés annuels.
'''

markdown_text2 = '''
#### Insight on the database used  

'''
liste_col_a_plot=['Date','Energy [KWh]','Average daily apparent temperature','The cloud cover', 'Humidity','The daily sum energy','Profil_fr', 'Day of the week','The day type', 'The wind speed']


def generate_table(dataframe, max_rows=5):

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in liste_col_a_plot])] +

        # Body
        [html.Tr([
           html.Td(dataframe.iloc[i][col]) for col in liste_col_a_plot
        ]) for i in range(min(len(dataframe), max_rows))]
    )



colors = {
    'background': 'black',
    'text': 'white'
}

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Prédiction de la consommation d'électricité"),
                ],
            ),
            
            html.Div(
                id="banner-logo",
                children=[
                    html.Img(id="logo_cap", src=app.get_asset_url("logo_Capgemini.jpg")),
                    html.Img(id="logo_enedis", src=app.get_asset_url("Logo-Enedis.jpg")),
                ],
            ),
        ],
    )


app.layout = html.Div(
        id="big-app-container",
        children=[
            build_banner(),
            # header
            html.Div([
            dcc.Markdown(children=markdown_text1)
            ],style= {'color':'white'}),
            
            html.Div([
            dcc.Dropdown(id='yaxis',
            options = [{'label': 'Prédiction de la consommation d\'électricité en utilisant un LSTM (tendance) et une décomposition de Fourier (saisonnalité) multipliée par une modulation', 'value': 'Prediction using trend (LSTM) and seasonality (Fourier with modulation) test'},
                                    {'label': 'Prédiction de la consommation d\'électricité en utilisant un LSTM (tendance) et une décomposition de Fourier (saisonnalité)', 'value': 'Prediction using trend (LSTM) and seasonality (trend) test'}],
                         value = 'Prediction using trend (LSTM) and seasonality (Fourier with modulation) test')#
            ],style={'width':'100%'}),#
           
            
            dcc.Graph(id='feature-graphics')])

           
            
@app.callback(Output('feature-graphics','figure'),
[Input('yaxis','value')])

def update_graph(yaxis_column_name):
    traces = []
    for i in df.Profil_fr.unique():
        print(df[yaxis_column_name].tail())
        df_by_profile = df[df['Profil_fr'] == i]
        traces.append(dict(
            x=df_by_profile['Date'],
            y=df_by_profile['Energy [KWh]'],
            #text=df_by_continent['country'],
            mode='lines',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name='Profil: '+i
        ))
        traces.append(dict(
            x=df_by_profile['Date'],
            y=df_by_profile[yaxis_column_name],
            mode='lines',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name='Prédictions pour '+i
        ))



    return {
        'data': traces ,
        
        'layout':go.Layout(
                xaxis=dict(title='Date',
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                label="jour",
                                step="day",
                                stepmode="backward"),
                            dict(count=7,
                                label="semaine",
                                step="day",
                                stepmode="backward"),  
                            dict(count=1,
                                label="mois",
                                step="month",
                                stepmode="backward"), 
                            dict(label="total",step="all")
                        ])
                ),
                rangeslider=dict(
                visible=True
                ),
                type="date"
                ),
                yaxis={'title': 'Consommation d\'électricité [kWh]'},
                height=700, # px
                width=1150
    )}






if __name__ == '__main__':
    app.run_server(debug=False, port=8053)