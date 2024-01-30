from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import yaml
from github.github_util import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import datetime as dt

with open('./config.yaml', 'r') as file:
    config = yaml.safe_load(file)

all_communities = config['all']


def initiate_dashboard():
    app = Dash(__name__)

    app.layout = html.Div([
        html.H1(children='Community Healthness Dashboard', style={'textAlign': 'center'}),
        html.Br(),

        html.Div([
            html.Div([
                html.Label('Community Name'),
                dcc.Dropdown(all_communities, id='llm_names_issue'),
                html.Br(),

                html.Button(children='Update Issue History', id='update_issues', n_clicks=0,
                            style={'verticalAlign': 'middle'}),

            ], style={'width': '30%', 'height': 500, 'padding-top': 150}),
            dcc.Graph(id='github-issue-sunburst', style={'width': '40%', 'height': 500})
        ], style={'display': 'flex', 'flexDirection': 'row'}),

        html.Div([
            html.Div([
                html.Label('Community Name'),
                dcc.Dropdown(all_communities, id='llm_names_metric', multi=True),
                html.Br(),

                html.Label('Interval'),
                dcc.Dropdown(['7 days', '14 days', 'all'], 'all', id='days'),
                html.Br(),

                html.Label('GitHub Metric'),
                dcc.RadioItems(['star', 'fork', 'clone'], 'star', id='metric'),
                html.Br(),

                html.Button(children='Update Metric History', id='update_metric', n_clicks=0, style={'verticalAlign': 'middle'}),

            ], style={'width': '30%', 'height': 500, 'padding-top': 150}),
            dcc.Graph(id='GitHub-bar-graph', style={'width': '70%', 'height': 500})
        ], style={'display': 'flex', 'flexDirection': 'row'}),
    ], style={'display': 'flex', 'flexDirection': 'column'})

    return app


@callback(
    Output('github-issue-sunburst', 'figure'),
    Input('llm_names_issue', 'value'))
def update_github_issue_figure(llm_names):
    df = load_issue_history_df(config[llm_names]['owner'], config[llm_names]['repo'])

    def filter_open_issues(df, days):
        base_dt = pd.to_datetime(datetime.today() - dt.timedelta(days=days))
        return len(df[df['created_at'] > base_dt])

    open_issues = df[df['state'] == 'open']
    less_than_two_days = filter_open_issues(open_issues, 2)
    less_than_four_days = filter_open_issues(open_issues, 4) - less_than_two_days
    more_than_four_days = len(open_issues) - less_than_four_days

    closed_issues = df[df['state'] == 'closed']
    closed_in_two_days = len(closed_issues[closed_issues['closed_time'] < 24 * 60 * 2])
    closed_in_four_days = len(closed_issues[closed_issues['closed_time'] < 24 * 60 * 4]) - closed_in_two_days
    closed_others = len(closed_issues) - closed_in_four_days

    data_df = pd.DataFrame(dict(
        respond_time=["<= 2 days", "<= 4 days", "> 4 days",
                      "<= 2 days", "<= 4 days", "> 4 days"],
        issue_type=["Open issues", "Open issues", "Open issues",
                    "Closed issues", "Closed issues", "Closed issues"],
        value=[less_than_two_days, less_than_four_days, more_than_four_days,
               closed_in_two_days, closed_in_four_days, closed_others],
    ))
    fig = px.sunburst(data_df, path=['issue_type', 'respond_time'], values='value', color='respond_time',
                      color_discrete_map={'<= 2 days': 'green', '<= 4 days': 'orange', '> 4 days': 'red'}
                      )

    fig.update_traces(textinfo="label+value")

    return fig

@callback(
    Output('update_issues', 'disabled', allow_duplicate=True),
    Input('update_issues', 'n_clicks'),
    prevent_initial_call=True,
)
def disable_button_metric(update):
    return True

@callback(
    [Output('update_issues', 'children'), Output('update_issues', 'disabled')],
    Input('update_issues', 'n_clicks'),
    Input('llm_names_issue', 'value'),
    prevent_initial_call=True,
)
def update_github_issue_history(n_clicks, llm_names_issue):
    if n_clicks == 0 or llm_names_issue not in config['all']:
        return ['Update Issue History', False]

    function_call('issues', config[llm_names_issue]['owner'], config[llm_names_issue]['repo'])

    return ['Success!', False]



@callback(
    Output('GitHub-bar-graph', 'figure'),
    Input('llm_names_metric', 'value'),
    Input('days', 'value'),
    Input('metric', 'value'))
def update_github_metric_figures(llm_names, days, metric):
    if llm_names == None:
        return make_subplots(specs=[[{"secondary_y": True}]])

    if days == '7 days':
        days = 7
    elif days == '14 days':
        days = 14

    if metric == 'clone':
        llm_names = ['Yi']

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if isinstance(llm_names, str):
        llm_names = [llm_names]

    for llm_name in llm_names:
        df = load_metric_history_df(owner=config[llm_name]['owner'], repo=config[llm_name]['repo'], metric=metric,
                                    days=days)
        fig.add_trace(go.Bar(
            x=df['dates'].tolist(),
            y=df['cumulative_counts'].tolist(),
            name=f'{llm_name} total',
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=df['dates'].tolist(),
            y=df['counts'].tolist(),
            name=f'{llm_name} daily',
            mode='lines'
        ), secondary_y=True)

    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Cumulative</b> Counts", secondary_y=False)
    fig.update_yaxes(title_text="<b>Increment</b> Counts", secondary_y=True)

    fig.update_layout(hovermode="x unified")
    return fig


@callback(
    Output('update_metric', 'disabled', allow_duplicate=True),
    Input('update_metric', 'n_clicks'),
    prevent_initial_call=True,
)
def disable_button_metric(n_clicks):
    return True


@callback(
    Output('update_metric', 'children'),
    Input('update_metric', 'n_clicks'),
    prevent_initial_call=True,
)
def update_github_metric_history(n_clicks):
    if n_clicks == 0:
        return 'Update Metric History'

    for llm_name in config['all']:
        metrics = ['star', 'fork']
        if llm_name == 'Yi':
            metrics.append('clone')

        for metric in metrics:
            function_call(metric, config[llm_name]['owner'], config[llm_name]['repo'])

    return 'Success!'
