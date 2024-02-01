import dash
from dash import html
import dash_bootstrap_components as dbc

def sidebar():
    nav_links = []
    for page in dash.page_registry.values():
        if page["path"].startswith("/app"):
            nav_links.append(
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                    color = 'secondary'
                )
            )
        elif page["path"]=="/projetos":
            nav_links.append(
                dbc.NavLink(
                    [
                        html.Div("App 1", className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
            )
    return dbc.Nav(children=nav_links,
                   vertical=False,
                   pills=False,
                   color = 'secondary')