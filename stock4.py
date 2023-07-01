import streamlit as st
import requests
from alpha_vantage.timeseries import TimeSeries
import plotly.express as px
import folium
from streamlit_folium import folium_static
import pandas as pd
#market list link:
#https://stockmarketmba.com/listofstocksforanexchange.php
#to run file:
#python -m streamlit run stock4.py

st.write(f"<h1 style='text-align: center; color: #00F900; '>Stonks</h1>", unsafe_allow_html=True)
stonks_api_key = st.secrets["API_KEY"] #"stonks_api_key":st.secrets["API_Key"]

@st.cache_data
def getStockForTimeSeriesIntraday(url):
    response = requests.get(url)
    if "Error Message" in response.json():
        st.error("1. This ticker might not supported on Alpha Vantage, try using a different ticker like SPY or INTC. "
                 "If issues persist or you have any questions, please reach out to support69@yahoo.com")
        st.commands.execution_control.stop()
    else:
        return response.json()

#make a function for data here
@st.cache_data
def getChartData(stockInput, userInterval, stonks_api_key):
    ts = TimeSeries(key=stonks_api_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=stockInput, interval = userInterval, outputsize='compact')
    return data

#function to display the data
def DisplayChartData(stockInput, chartChoice, radioKey, colorKey):
    col1, col2 = st.columns(2)
    #option functions
    with col1:
        parameter = st.radio("Choose One", options=[
            "1. open",
            "2. high",
            "3. low",
            "4. close",
            "5. volume"
        ], key = radioKey)

    #color functions
    with col2:
        if (parameter and chartChoice == "line") or (parameter and chartChoice == "Area"):
            color = st.color_picker('Pick A Line Color', '#00f900', key = colorKey)

    #chart functions
    if parameter and chartChoice == "line":
        fig1 = px.line(data, x=data.index, y=parameter, title=parameter)
        if parameter == "5. volume":
            fig1.update_layout(title=f'{stockInput.upper()} Stock Volume Over Time', xaxis_title='Time',
                               yaxis_title='Volume')
        else:
            fig1.update_layout(title=f'{stockInput.upper()} Stock Price Over Time', xaxis_title='Time', yaxis_title='Price')
        fig1.update_traces(line_color=color)
        st.plotly_chart(fig1, use_container_width=True)
    elif parameter and chartChoice == "Area":
        fig2 = px.area(data, x=data.index, y=parameter, title=parameter)
        if parameter == "5. volume":
            fig2.update_layout(title=f'{stockInput.upper()} Stock Volume Over Time', xaxis_title='Time', yaxis_title='Volume')
        else:
            fig2.update_layout(title=f'{stockInput.upper()} Stock Price Over Time', xaxis_title='Time',
                               yaxis_title='Price')
        fig2.update_traces(line_color=color)
        st.plotly_chart(fig2, use_container_width=True)
    elif parameter and chartChoice == "Bar":
        fig3 = px.bar(data, x=data.index, y=parameter, title=parameter)
        if parameter == "5. volume":
            fig3.update_layout(title=f'{stockInput.upper()} Stock Volume Over Time', xaxis_title='Time',
                               yaxis_title='Volume')
        else:
            fig3.update_layout(title=f'{stockInput.upper()} Stock Price Over Time', xaxis_title='Time', yaxis_title='Price')
        #fig3.update_traces(line_color=color)
        st.plotly_chart(fig3, use_container_width=True)

def stockTable(userInterval, url):
    #taking and sorting data into a table
    #--------------------
    checkbox2 = st.checkbox("Questions about the table?")
    if checkbox2:
        st.info("Alpha Vantage APIs' Intraday feature only supports history spanning about a couple weeks back "
                "from the current date, as well as only viewing  30-60 minuet intervals in the table format")
    #--------------------
    #response = requests.get(url)
    try:
        data = getStockForTimeSeriesIntraday(url)["Time Series ({})".format(userInterval)]

    except KeyError:
        st.error("The table only supports 30-60 minute intervals, "
                 "wrong dates were picked, " 
                 "the order of dates are wrong, or the available options were selected too quickly. " 
                 "Please reach out to support69@yahoo.com if you have any additional issues or questions")
        st.commands.execution_control.stop()
    if userInterval == "30min" or userInterval == "60min":
        df = pd.DataFrame(data).transpose()
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        df.columns = ["open", "high", "low", "close", "volume"]
        df = df.astype(float)
        #date select boxes
        startDateTime = st.date_input("Start Date", df.index.min().date())
        end_date = st.date_input("End Date", df.index.max().date())
        #start_time = st.time_input("Start Time", value=df.index.min().time())
        #end_time = st.time_input("End Time", value=df.index.max().time())

        #Data to be filtered on date range
        start_datetime = pd.to_datetime(str(startDateTime))
        end_datetime = pd.to_datetime(str(end_date))
        #start_datetime = pd.to_datetime(str(startDateTime) + " " + str(start_time))
        #end_datetime = pd.to_datetime(str(end_date) + " " + str(end_time))
        filtered_df = df.loc[(df.index >= start_datetime) & (df.index <= end_datetime)]

        st.write(filtered_df)
    else:
        st.info("Please pick either the 30 or the 60 minute interval options")

#side bar tab for alpha vantage API's stock options
option = st.sidebar.selectbox("Please Choose One", options= ["Time Series Intraday", "Stock Exchange Locations",
                                                             "List of Supported Stocks"])

if option == "Time Series Intraday":
    #st.header = "Time Series Intraday"
    checkbox = st.checkbox("Can't Decide on a Ticker?")
    if checkbox:
        st.info("Try out the, List of Supported Stocks, feature located on the left side of this page -> 3rd option")
    stockInput = st.text_input('Please Enter A Ticker (Example Format: SPY, spy, Aapl, etc..)', '')
    # Display the search results
    if stockInput != "":
        userInterval = st.selectbox("Please select a stock time intraday data interval",
                                    options=["60min", "30min", "5min", "1min"])
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stockInput}&interval={userInterval}&apikey=stonks_api_key'

        if stockInput != "" and userInterval != "":
            getStockForTimeSeriesIntraday(url)
            st.write(f"<h1 style='text-align: center; color: #00F900; font-size: 20px; "
                     f"'>Time Series Intraday {stockInput.upper()} Information</h1>", unsafe_allow_html=True)
            data = getChartData(stockInput, userInterval, stonks_api_key)

            # The control center
            linePlot,  areaChart, barChart, table= st.tabs(["Line Chart", "Area Chart", "Bar Chart", "Table"])

            with linePlot:
                #st.subheader("Line Chart")
                chartChoice = "line"
                radioKey = "option1"
                colorKey = "option2"
                DisplayChartData(stockInput, chartChoice, radioKey, colorKey)

            with areaChart:
                #st.subheader("Area Chart")
                chartChoice = "Area"
                radioKey = "option3"
                colorKey = "option4"
                DisplayChartData(stockInput, chartChoice, radioKey, colorKey)

            with barChart:
                #st.subheader("Bar Chart")
                chartChoice = "Bar"
                radioKey = "option5"
                colorKey = "option6"
                DisplayChartData(stockInput, chartChoice, radioKey, colorKey)

            with table:
                #st.subheader("Stock Table")
                stockTable(userInterval, url)

    # elif stockInput:
    #     st.error('How did you get here?' +
    #              'please email support at support69@yahoo.com')
    #     st.commands.execution_control.stop()

if option == "Stock Exchange Locations":
    st.write(f"<h1 style='text-align: center; color: #00F900; '>Major Stock Exchange Locations</h1>", unsafe_allow_html=True)
    coll1, coll2, coll3 = st.columns(3)
    if coll1.button("New York Stock Exchange Location"):
        nyseLatitude, nyseLongitude = 40.7060, -74.0088
        map = folium.Map(location=[nyseLatitude, nyseLongitude], zoom_start=10)
        folium.Marker(location=[nyseLatitude, nyseLongitude], popup="NYSE").add_to(map)
        # Display the map in Streamlit using streamlit-folium
        folium_static(map)
    if coll3.button("Tokyo Stock Exchange Location"):
        tseLatitude, tseLongitude = 35.6895, 139.6917
        map = folium.Map(location=[tseLatitude, tseLongitude], zoom_start=10)
        folium.Marker(location=[tseLatitude, tseLongitude], popup="TSE").add_to(map)
        # Display the map using streamlit-folium
        folium_static(map)

if option == "List of Supported Stocks":
    st.write(f"<h1 style='text-align: center; color: #00F900; font-size: 24px; '>Try A Stock Out</h1>", unsafe_allow_html=True)
    st.write(pd.read_csv('./information/top_dow_list.csv'))
    st.info("Information pulled from Motley Fool at: " +
            "https://www.fool.com/investing/stock-market/indexes/dow-jones/companies-in-the-dow/")
