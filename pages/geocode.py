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

dash.register_page(__name__, path = '/', title='Geocodigo', order=0)

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

def geocod_add(geo_df):

    geolocator = Nominatim(user_agent="MyApp")

    geocod = pd.read_table('geocod_ibge.csv', sep=';')

    a = []
    b = []
    for index, row in geo_df.iterrows(): 
        if geo_df.type[0] == 'Point':
            lat,lon = row.geometry.y,row.geometry.x
        else:
            lat,lon = row.geometry.centroid.y,row.geometry.centroid.x
        coordinates = lat,lon
        city = geocoder.osm(coordinates, method='reverse').town
        
        lat_busca = lat

        while city == None:
            lat_busca = lat_busca - 0.01
            location = geolocator.reverse([lat_busca,lon])

            if location == None:
                city = geocoder.osm([lat_busca,lon], method='reverse').town
            else:
                address = location.raw['address']
                city = address.get('city')


            if city == None:
                city = address.get('town')
                if city == None:
                    city = geocoder.osm([lat_busca,lon], method='reverse').town
                    if city == None:

                        city = address.get('village')

        a.append(city)
        if city == None:
            b.append(99999)
        else:
            try:
                geocod_aprox = geocod[geocod['municipio2'] == city].geocodigo.values[0]
                b.append(geocod_aprox)
            except:
                b.append(99999)
    geo_df['municipio'] = a

    geo_df['geocodigo'] = b


    return geo_df


header = html.Div(
    [
        html.Br(),
        html.Br(),

        html.Div(children=[
            dbc.Row([
                html.H1(children=['Adicionar Geocodigo e Municipio ao Shapefile'],style = {'weight':'bold'}),
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
                id='upload-files-div',
            ),
            style={
                'textAlign': 'center',
                'padding': '10px',
                'display': 'inline-block'
            },
        ),
        html.Br(),
        dcc.Loading(html.Div(id = 'msg_geocode1')),


        dbc.Button(id='btn',
            children=[html.I(className="fa fa-download mr-1"), "Iniciar Processo / Download"],
            color="info",
            className="mt-1"
        ),
        dcc.Download(id="download_geocode"),


        html.Br(),
        html.Br(),

    ],
    style={
        'textAlign': 'center',
    },
)

@callback(
    Output('download_geocode', 'data'),
    Output('msg_geocode1', 'children'),
    
    Input("btn", "n_clicks"),
    [Input('upload-files-div', 'isCompleted')],
    [Input('upload-files-div', 'fileNames')],
    prevent_initial_call=True,

)
def display_files(n_clicks, isCompleted, fileNames):

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
                    geo_df = geocod_add(geo_df)


                    ref_data_path = 'ref_data/{}/'.format(shp_file.split('/')[-1].split('.')[0])
                    os.mkdir(ref_data_path)
                    dest_file = ref_data_path + shp_file.split('/')[-1]
                    geo_df.to_file(dest_file,driver='ESRI Shapefile',encoding='UTF-8',index = False, crs="EPSG:4674")
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