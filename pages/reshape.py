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

dash.register_page(__name__, title='Reshape', order=3)


def print_schema(shp):

    with fiona.open(shp, 'r') as source:


        return source,source.schema['properties']



header = html.Div(
    [
        html.Br(),
        html.Br(),

        html.Div(children=[
            dbc.Row([
                html.H1(children=['Reformatar o tamanho dos campos'],style = {'weight':'bold'}),
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
                id='upload-files-div3',
            ),
            style={
                'textAlign': 'center',
                'padding': '10px',
                'display': 'inline-block'
            },
        ),

    html.Div([

    html.P('Exemplo de como voce deve colocar o schema no input abaixo:'),

    html.P("{'id': 'int:10', 'nome': 'str:100', 'geocodigo': 'int:10', 'municipio': 'str:100', 'latitude': 'float:11.3', 'longitude': 'float:11.3'}"),

    ]),


    html.Div([
        "Input: ",
        dcc.Input(id = 'schema', type = 'text', style = {'width': '75%'}),
    ]),
        
        html.Br(),
        html.Br(),
        html.Br(),

        dcc.Loading(html.Div(id = 'mensagem_reshape1')),

        dbc.Button(id='btn2',
            children=[html.I(className="fa fa-download mr-1"), "Iniciar Processo / Download"],
            color="info",
            className="mt-1"
        ),
        dcc.Download(id="download_reshape"),

    ],
    style={
        'textAlign': 'center',
    },
)


@callback(
    Output('download_reshape', 'data'),
    Output('mensagem_reshape1', 'children'),
    Input("btn2", "n_clicks"),
    Input('schema','value'),
    [Input('upload-files-div3', 'isCompleted')],
    [Input('upload-files-div3', 'fileNames')],
    prevent_initial_call=True,
)
def change_schema(n_clicks, schema,isCompleted, fileNames):
    if n_clicks > 0:
        
        if not isCompleted:
            return 
        if fileNames is not None:
            schema = ast.literal_eval(schema)

            dir = 'ref_data/'
            if os.path.exists(dir):
                shutil.rmtree(dir)
            os.makedirs(dir)

            folder_data = glob('raw_data/*')[0]
            zip_file = glob('raw_data/*/*.zip', recursive = True)[0]

            shutil.unpack_archive(zip_file, folder_data)

            shp_file = glob('raw_data/**/*.shp', recursive = True)
            print(shp_file)
            if shp_file:
                shp_file = shp_file[0]
                try:
                    geo_df = gpd.read_file(shp_file,crs='4674')


                    ref_data_path = 'ref_data/{}/'.format(shp_file.split('/')[-1].split('.')[0])
                    os.mkdir(ref_data_path)
                    dest_file = ref_data_path + shp_file.split('/')[-1]



                    data_shape = gpd.read_file(shp_file,crs='4674') 



                    b_schema = gpd.io.file.infer_schema(data_shape)

                    b_schema['properties'] = schema


                    data_shape.to_file(dest_file,driver='ESRI Shapefile',
                                        encoding='UTF-8',index = False, 
                                        crs="EPSG:4674",schema = b_schema)


                    ffiles = glob(ref_data_path + '*')

                    shutil.rmtree(folder_data)
                    shutil.make_archive(ref_data_path, 'zip', ref_data_path)

                    uri = glob('ref_data/*.zip')[0]

                    dir = 'raw_data/'
                    if os.path.exists(dir):
                        shutil.rmtree(dir)
                    os.makedirs(dir)

                    return dcc.send_file(uri), dbc.Card([dbc.CardBody([html.P("Download Realizado!!!")])])
                except:
                    return dbc.Card([dbc.CardBody([html.P('Algo deu errado :/ .')])]), html.P("Algo deu errado! :/")
            else:
                return dbc.Card([dbc.CardBody([html.P('Shapefile não esta completo.')])]), html.P("Algo deu errado! :/")
        else:
            return html.P('Algo deu errado! :/'), html.P('Algo deu errado! :/')


def layout():
    return html.Div([header])