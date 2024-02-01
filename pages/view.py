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


dash.register_page(__name__, title='View', order=2)


def print_schema(shp):

    with fiona.open(shp, 'r') as source:


        return source,source.schema['properties']



header = html.Div(
    [

        html.Br(),
        html.Br(),

        html.Div(children=[
            dbc.Row([
                html.H1(children=['Visualize a configuração dos campos do seu Shapefile'],style = {'weight':'bold'}),
                # html.Img(src="assets/gisbanner.jpg"),
            ], justify='center',), 
        ], className = 'col-12'),
        html.Hr(),
        html.Br(),

        html.Div(
            du.Upload(
                text='Solte aqui o arquivo .zip com os arquivos do shapefile',
                pause_button=False,
                cancel_button=True,
                filetypes=['zip', 'rar'],
                id='upload-files-div2',
            ),
            style={
                'textAlign': 'center',
                'padding': '10px',
                'display': 'inline-block'
            },
        ),



        html.Br(),
        dcc.Loading(html.Div(id = 'msg_view1')),


        html.Center([
        dash_table.DataTable(
        id='table',
        columns=[],
        data=[],
        column_selectable="multi",
        style_header=dict(textAlign = 'center'),
        style_data=dict(width='auto', textAlign = 'center'),

        style_cell={'textAlign':'left'},
        style_table={
        'padding-top' : '1%',

        },
        ),
        ], style = {'width':'50%', 'align-itens':'center',"display": "inline-block"}),
        html.Br(),
        html.Br(),

        html.Div(id = 'msg_view2'),

        
        html.Br(),

        html.Div(id = 'msg_view3'),
    ],
    style={
        'textAlign': 'center',
    },
)
@callback(
    Output('msg_view1', 'children'),
    Output('table', 'columns'),
    Output('table', 'data'),
    Output('msg_view2', 'children'),
    Output('msg_view3', 'children'),

    [Input('upload-files-div2', 'isCompleted')],
    [State('upload-files-div2', 'fileNames')],
    prevent_initial_call=True,

)
def other(isCompleted, fileNames):

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
            geo_df = gpd.read_file(shp_file,crs='4674')
            a,b = print_schema(shp_file)

            col = b.keys()

            df = pd.DataFrame(zip(list(b.keys()),list(b.values())), columns = ['Campo','Tipo:Tamanho'])

            dir = 'raw_data/'
            if os.path.exists(dir):
                shutil.rmtree(dir)
            os.makedirs(dir)

        return [html.P('Configuração dos campos:'),
            [{"name": i.title(), "id": i, "deletable": False} for i in df.columns], 
            df.to_dict('records'),
            html.P('Faça a copia do dicionario abaixo e utilize esse formato para alterar o tamanho dos campos'),
            html.P(str(dict(b)))]


def layout():
    return html.Div([header

        ])