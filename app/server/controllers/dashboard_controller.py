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

# 連線mongodb
mongo_connector = MongoDBConnector()
comment_collection = mongo_connector.get_collection('comment')
drama_collection = mongo_connector.get_collection('drama')

dash.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
            <title>Dashboard</title>
            {%css%}
        </head>
        <body>
            <nav class="navbar navbar-expand-lg bg-body-tertiary" style="background-color: #00416A;" >
                <div class="container-fluid">
                    <a class="nav-link text-white" href="/" style="padding: 0px">
                        <h1 class="text-white", style="margin-bottom: 0px">Watch Next</h1>
                    </a>
                    <div class="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul class="navbar-nav me-auto mb-2 mb-lg-0 ml-auto">
                            <li class="nav-item">
                                <a class="nav-link active text-white" aria-current="page" href="/">回首頁</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            {%app_entry%}
            <footer class="text-center text-lg-start bg-light text-muted">
                {%config%}
                {%scripts%}
                {%renderer%}
                <div class="container text-center text-md-start mt-5">
                <div class="row mt-3">
                    <div class="col-md-3 col-lg-4 col-xl-3 mx-auto mb-3">
                    <h6 class="text-uppercase text-left fw-bold mb-4 mt-3">Watch Next</h6>
                    <p class="text-left">彙整戲劇資訊與評論的網站</p>
                    <p class="text-left">參考評論來決定你下一部要追的劇</p>
                    <p class="text-left">小提醒：這裡沒有電影喔ฅ^•ﻌ•^ฅ</p>
                    </div>
                    <div class="col-md-4 col-lg-3 col-xl-3 mx-auto mb-md-0 mb-4">
                    <h6 class="text-uppercase text-left fw-bold mb-4 mt-3">Contact</h6>
                    <a class="text-muted" href="mailto:hsuu816@gmail.com">
                        <p class="text-left">
                        <i class="fas fa-envelope me-3 text-left"></i>
                        hsuu816@gmail.com
                        </p>
                    </a>
                    <a class="text-muted" href="https://www.linkedin.com/in/shih-yun-hsu-8a3606277">
                        <p class="text-left"><i class="fab fa-linkedin"></i> Shih Yun Hsu</p>
                    </a>
                    <a class="text-muted" href="https://github.com/hsuu816">
                        <p class="text-left"><i class="fab fa-github"></i> hsuu816</p>
                    </a>
                    </div>
                </div>
                </div>
                <div class="text-center p-2" style="background-color: rgba(0, 0, 0, 0.05);">
                © 2023 Copyright:
                <a class="text-reset fw-bold" href="https://www.watchnexts.com">watchnexts.com</a>
                </div>
            </footer>
        </body>
    </html>
    '''

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
                value='7d',  # 預設七天
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
        labels={'count': '文章數量', '_id': '劇名'}
    )

    bar_fig.update_layout(
        title_text="熱門戲劇討論度排行",
        title_x=0.5,  # 標題置中
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

    pie_fig = px.pie(
        pie_chart_df,
        names='_id',
        values='count', 
    )

    pie_fig.update_layout(
        title_text="熱門戲劇類型",
        title_x=0.5  # 標題置中
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








