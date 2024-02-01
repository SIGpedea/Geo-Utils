import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
import dash_uploader as du

font_awesome = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
meta_tags = [{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
external_stylesheets = [
    font_awesome,
    dbc.themes.LUMEN
]

url_theme1 = dbc.themes.SANDSTONE
template_theme1 = "minty"
url_theme2 = dbc.themes.SUPERHERO
template_theme2 = "darkly"

app = dash.Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

UPLOAD_FOLDER = r"raw_data/"
du.configure_upload(app, UPLOAD_FOLDER)


server = app.server


theme_switch = ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(theme_switch,
        className="text-primary d-flex align-items-center m-2", style = {'align':'left'}),

        dbc.Nav([
            dbc.NavLink(page["name"], href=page["path"], style = {'font-weight':'bold'})
            for page in dash.page_registry.values()
        ],),

    ],
    brand="Geo-Utils",
    brand_href="/",
    color="secondary",
    dark=False,
    style = {'border-radius':'10px'}
)


app.layout = dbc.Container([navbar, dash.page_container], fluid=False)



if __name__ == '__main__':
	app.run_server(debug = False, port = '8050')
