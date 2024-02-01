from dash.dependencies import Input, Output, State
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import geopandas as gpd
import pandas as pd
import dash_uploader as du
from zipfile import ZipFile
from glob import glob
import os
import shutil
from geopy.geocoders import Nominatim
import geocoder
import dash
import fiona
import ast

dash.register_page(__name__, title='Replace String', order=1)


def print_schema(shp):

    with fiona.open(shp, 'r') as source:


        return source,source.schema['properties']



header = html.Div(
    [
        html.Br(),
        html.Br(),

        html.Div(children=[
            dbc.Row([
                html.H1(children=['Alterar valor de string dentro do campo da tabela de atributo'],style = {'weight':'bold'}),
                # html.Img(src="assets/gisbanner.jpg"),
            ], justify='center',), #style = {'background-image':'url(assets/gisbanner.jpg)', 'heigth':'100 px','padding-top' : '5%'})
        ], className = 'col-12'),
        html.Hr(),
        html.Br(),

        html.Div(
            du.Upload(
                text='Solte aqui o arquivo .zip com os arquivos do shapefile',
                pause_button=False,
                cancel_button=True,
                filetypes=['zip', 'rar'],
                id='upload-files-div4',
            ),
            style={
                'textAlign': 'center',
                'padding': '10px',
                'display': 'inline-block'
            },
        ),

    html.Div([

    html.P('Preencha os campos abaixo conforme as alterações que deseja realizar'),

    html.Div([
        html.P("Qual campo voce deseja alterar?  \n", style = {'color':'red'}),
        dcc.Input(id = 'alt_field', type = 'text'),
        html.P("Ex: nome  \n"),
        html.P("String a ser alterada  \n", style = {'color':'red'}),
        dcc.Input(id = 'str_1', type = 'text'),
        html.P("Ex: APA  \n"),
        html.P("String que vai entrar no lugar da string alterada  \n", style = {'color':'red'}),
        dcc.Input(id = 'str_2', type = 'text'),
        html.P("Ex: Área de Proteção Ambiental  \n"),

    ], style={"border":"2px grey solid", "border-radius":"10px","overflow": "hidden", "display": "inline-block", "padding":"20px"}),

    # html.Div([
    # "String a ser alterada  ",
    #     dcc.Input(id = 'str_1', type = 'text'),
    # ]),

    # html.Div([
    # "String que vai entrar no lugar da string alterada  ",
    # dcc.Input(id = 'str_2', type = 'text'),
    # ]),

    ]),



        
        html.Br(),
        html.Br(),
        html.Br(),

        dcc.Loading(html.Div(id = 'msg_alt')),

        dbc.Button(id='btn3',
            children=[html.I(className="fa fa-download mr-1"), "Iniciar Processo / Download"],
            color="info",
            className="mt-1"
        ),
        dcc.Download(id="download_alt"),

    ],
    style={
        'textAlign': 'center',
    },
)


@callback(
    Output('download_alt', 'data'),
    Output('msg_alt', 'children'),
    Input("btn3", "n_clicks"),

    Input('str_1','value'),
    Input('str_2','value'),

    Input('alt_field','value'),
    [Input('upload-files-div4', 'isCompleted')],
    [Input('upload-files-div4', 'fileNames')],
    prevent_initial_call=True,
)
def alt_field_app(n_clicks, str_1: str, str_2: str, alt_field: str,isCompleted, fileNames):
    if n_clicks > 0:
        if not isCompleted:
            return 
        if fileNames is not None:

            dir = 'ref_data/'
            if os.path.exists(dir):
                shutil.rmtree(dir)
            os.makedirs(dir)

            folder_data = glob('raw_data/*')[0]
            zip_file = glob('raw_data/*/*.zip', recursive = True)[0]

            shutil.unpack_archive(zip_file, folder_data)

            shp_file = glob('raw_data/**/*.shp', recursive = True)
            if shp_file:
                shp_file = shp_file[0]
                try:

                    geo_df = gpd.read_file(shp_file,crs='4674')
                    ref_data_path = 'ref_data/{}/'.format(shp_file.split('/')[-1].split('.')[0])

                    os.mkdir(ref_data_path)

                    dest_file = ref_data_path + shp_file.split('/')[-1]


                    geo_df[alt_field] = geo_df[alt_field].str.replace(str_1,str_2).str.upper()


                    print('Salvando')
                    geo_df.to_file(dest_file,driver='ESRI Shapefile',
                                        encoding='UTF-8',index = False, 
                                        crs="EPSG:4674")
                    print('Salvo')
                    shutil.rmtree(folder_data)
                    shutil.make_archive(ref_data_path, 'zip', ref_data_path)

                    uri = glob('ref_data/*.zip')[0]

                    dir = 'raw_data/'
                    if os.path.exists(dir):
                        shutil.rmtree(dir)
                    os.makedirs(dir)

                    return dcc.send_file(uri), dbc.Card([dbc.CardBody([html.P("Download Realizado!!!")])])
                except:
                    return dbc.Card([dbc.CardBody([html.P('Algo deu errado 1  :/ .')])]), html.P("Algo deu errado! 1  :/")
            else:
                return dbc.Card([dbc.CardBody([html.P('Shapefile não esta completo.')])]), html.P("Algo deu errado! 2:/")
        else:
            return html.P('Algo deu errado! 3 :/'), html.P('Algo deu errado! 3 :/')


def layout():
    return html.Div([header])