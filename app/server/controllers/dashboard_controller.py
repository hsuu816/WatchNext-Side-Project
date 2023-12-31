import os
from server import app
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from server.models.mongodb import MongoDBConnector
import jieba.analyse
from wordcloud import WordCloud
from io import BytesIO
import base64

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css', 
                        '/static/style.css']

dash = Dash(server=app, routes_pathname_prefix="/dashboard/", external_stylesheets=external_stylesheets)
dash.config.suppress_callback_exceptions = True

# connect to mongodb
mongo_connector = MongoDBConnector()
comment_collection = mongo_connector.get_collection('comment')
drama_collection = mongo_connector.get_collection('drama')

with open(os.path.join(os.path.dirname(__file__), "..", "templates", "dashboard.html"), "r", encoding="utf-8") as file:
    dash.index_string = file.read()

dash.layout = dbc.Container([
    html.Div([
        html.H1("戲劇討論趨勢", style={'text-align': 'center'}),
        html.Div(
            dcc.RadioItems(
                id='time-range-selector',
                options=[
                    {'label': '七天', 'value': '7d'},
                    {'label': '一個月', 'value': '1m'},
                    {'label': '三個月', 'value': '3m'},
                    {'label': '半年', 'value': '6m'},
                ],
                value='1m',
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            ),
            style={'text-align': 'center', 'margin': '20px'}
        ),
        dbc.Spinner(
            html.Div([
                dcc.Graph(id='bar-chart', style={'width': '50%', 'height': '50%', 'margin-right': 'auto', 'margin-left': '0px', 'display': 'block'}),
                dcc.Graph(id='pie-chart',style={'width': '50%', 'height': '50%', 'margin-right': '0px', 'margin-left': 'auto', 'display': 'block'}),
            ], style={'display': 'flex', 'margin-bottom': '40px'})
        ),
        dbc.Spinner(
            html.Img(id='wordcloud-image', style={'width': '80%', 'height': '80%', 'margin': 'auto', 'display': 'block'})
        )
    ])
], fluid=True)

@dash.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('wordcloud-image', 'src')],
    [Input('time-range-selector', 'value')]
)
def update_dashboard(selected_time_range):
    current_datetime = datetime.now()
    if selected_time_range == '7d':
        start_date = (current_datetime - timedelta(days=7)).strftime("%Y-%m-%d")
    elif selected_time_range == '1m':
        start_date = (current_datetime - timedelta(days=30)).strftime("%Y-%m-%d")
    elif selected_time_range == '3m':
        start_date = (current_datetime - timedelta(days=90)).strftime("%Y-%m-%d")
    elif selected_time_range == '6m':
        start_date = (current_datetime - timedelta(days=180)).strftime("%Y-%m-%d")
    end_date = current_datetime.strftime("%Y-%m-%d")
    
    # bar chart
    bar_chart_pipeline = [
        {"$match": {"release_time": {"$gte": start_date, "$lt": end_date}}},
        {"$group": {"_id": "$drama_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
        ]

    bar_chart_data = comment_collection.aggregate(bar_chart_pipeline)
    bar_chart_df = pd.DataFrame(list(bar_chart_data))
    bar_fig = px.histogram(
        bar_chart_df,
        x='_id',
        y='count',
        labels={'count': '文章數量', '_id': '劇名'},
        color_discrete_sequence=px.colors.sequential.Blues[::-1]
    )

    bar_fig.update_layout(
        title_text="熱門戲劇討論度排行",
        title_x=0.5,  # center the title
        xaxis_title='劇名',
        yaxis_title='文章數量',
        template='plotly_white'
    )
    
    # pie chart
    drama_name_list = bar_chart_df['_id'].tolist()
    pie_chart_pipeline = [
        {"$unwind": "$categories"},
        {"$match": {"name": {"$in": drama_name_list[1:]}}},
        {"$group": {"_id": "$categories", "count": {"$sum": 1}}}
    ]

    pie_chart_data = drama_collection.aggregate(pie_chart_pipeline)
    pie_chart_df = pd.DataFrame(list(pie_chart_data))
    pie_chart_df = pie_chart_df.rename(columns={'_id': '類型'})
    pie_chart_df = pie_chart_df.rename(columns={'count': '數量'})

    pie_fig = px.pie(
        pie_chart_df,
        names='類型',
        values='數量',
        color_discrete_sequence=px.colors.sequential.Blues[::-1]
    )

    pie_fig.update_layout(
        title_text="熱門戲劇類型",
        title_x=0.5 # center the title
    )
    
    # word cloud
    comments = comment_collection.find({"release_time": {"$gt": start_date, "$lt": end_date}})
    comment_list = [comment['title'] for comment in comments]
    comments_combined = " ".join(comment_list)
    jieba.set_dictionary('server/assets/dict.txt.big')
    jieba.load_userdict("server/assets/mydict.txt")
    jieba.analyse.set_stop_words('server/assets/stop_word.txt')
    extracted_keywords = jieba.analyse.extract_tags(comments_combined, topK=100, withWeight=False)
    wordcloud = WordCloud(max_words=100, font_path='server/assets/NotoSerifTC-Regular.otf', width=800, height=400, background_color='white').generate(" ".join(extracted_keywords))
    image_stream = BytesIO()
    wordcloud.to_image().save(image_stream, format='PNG')
    encoded_image = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    return bar_fig, pie_fig, f'data:image/png;base64,{encoded_image}'








