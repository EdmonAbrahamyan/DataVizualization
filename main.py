from dash import dcc, Dash
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


def calcuate_points(data):
    df_rank = data.groupby(['Country', 'Year', 'Team 1'], as_index=False)['Team 1 (pts)'].sum().merge(
        data.groupby(['Country', 'Year', 'Team 2'], as_index=False)['Team 2 (pts)'].sum(),
        right_on=['Country', 'Year', 'Team 2'], left_on=['Country', 'Year', 'Team 1'])

    df_rank['Pts'] = df_rank['Team 1 (pts)'] + df_rank['Team 2 (pts)']
    df_rank.rename(columns={'Team 1': 'Team'}, inplace=True)
    df_rank = df_rank[['Country', 'Year', 'Team', 'Pts']]

    df_rank.sort_values(by=['Country', 'Year', 'Pts'], ascending=False, inplace=True)
    return df_rank


data = pd.read_csv('Data/BIG FIVE 1995-2019.csv')
data = calcuate_points(data)
app = Dash(__name__)


@app.callback(
    Output("graph", "figure"),
    Input("select_country", "value"))
def update_bar_chart(country='GER'):
    df_rank_new = data.groupby(['Year', 'Country'])[['Team', 'Pts']].max('Pts')
    df_rank_new['Winner'] = 1

    final_data = data.merge(df_rank_new, how='left', on=['Year', 'Country', 'Pts'])
    final_data['Winner'] = final_data['Winner'].fillna(0)

    winners = final_data[final_data.Winner == 1].groupby(['Country', 'Team']).count().reset_index()
    winners = winners[['Country', 'Team', 'Winner']]

    df = winners
    mask = df["Country"] == country
    fig = px.bar(df[mask], x="Team", y="Winner")
    return fig


@app.callback(
    Output('league_table', 'children'),
    Input('select_country', 'value'),
    Input('select_year', 'value'))
def generate_table(country='GER', year=2019):
    df = data[(data.Country == country) & (data.Year == year)]
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(len(df))
        ])
    ], id='league_table')


app.layout = html.Div(style={'backgroundColor': '#11111',
                             'display' : 'flex',
                             'flexDirection' : 'row'}, children=[
    html.Div(children=[
        html.H1(children='Top Five League',
                style={'textAlign': 'center',
                       'color': '#111111'}),
        html.Div([
            "Choose country",
            dcc.Dropdown(data.Country.unique(), 'ENG', id='select_country'),
            "Choose year",
            dcc.Dropdown(data.Year.unique(), 2019, id='select_year'),
        ], ),

        generate_table(),
    ]),

    html.Div([
        html.H2('Winners', style={'textAlign': 'center',
                                  'color': '#111111'}),
        dcc.Graph(id="graph"),
    ], style={'width': '75%'})
])

if __name__ == '__main__':
    app.run_server(port='8052', debug=True)
