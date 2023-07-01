from flask import Flask, render_template, request
import requests
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from datetime import datetime, timedelta

import pandas as pd
from sklearn.model_selection import train_test_split

app = Flask(__name__)

def get_prediction(history_data):
    time_steps = 2
    dataX = []
    dataY = []

    for i in range(len(history_data) - time_steps):
        dataX.append(history_data[i:i+time_steps])
        dataY.append(history_data[i+time_steps])
    model = LinearRegression()
    model.fit(dataX, dataY)
    cur_day = history_data[len(history_data)-1]
    fore_day = history_data[len(history_data)-2]
    return model.predict(np.array([cur_day,fore_day]).reshape(1, -1))[0]

def get_type_prediction(next_high, next_low, high_data, low_data, type_data):
    #combining the data into a dictionary
    data = {
        'high':high_data,
        'low':low_data,
        'text':type_data
    }
    #loading in to the data frame
    df = pd.DataFrame(data)
    
    #Splitting into two sets - features and target
    X = df[['high', 'low']]
    y = df['text']
    
    #splitting into training and testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    #loading the model
    model = LogisticRegression()

    #fitting the training data
    model.fit(X_train, y_train)
    
    #making prediction
    prediction = model.predict([[next_high, next_low]])

    return prediction[0]    
    

def predict_weather(history):
    high_temp_data = []
    low_temp_data = []
    weather_type = []
    for i in range (len(history)):
        high_temp_data.append(history[i]['high'])
        low_temp_data.append(history[i]['low'])
        weather_type.append(history[i]['text'])
    high_pred = get_prediction(high_temp_data)
    low_pred = get_prediction(low_temp_data)
    type_pred = get_type_prediction(high_pred, low_pred, high_temp_data, low_temp_data, weather_type)
    return [high_pred, low_pred, type_pred]

def get_weatherData(name):
    url = "https://yahoo-weather5.p.rapidapi.com/weather"

    querystring = {"location":name,"format":"json","u":"f"}

    headers = {
        "X-RapidAPI-Key": "b2201a8335msh67fe7547b34b586p196132jsn4b087bef3184",
        "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/weatherReport', methods = ['GET', 'POST'])
def showWeatherReport():
    if(request.method == 'POST'):
        city_name = request.form['city']
        
        weather_data = get_weatherData(city_name)
        
      
        forecast_data = weather_data['forecasts']
        
        #current days weather
        day = forecast_data[0]['day']
        high = round((forecast_data[0]['high'] -  32)*5/9, 1)
        low = round((forecast_data[0]['low'] -  32)*5/9, 1)
        weather_type = forecast_data[0]['text']
        
        cur_day_temp = [day, high, low, weather_type]
        
        #Tomorrow's weather prediction
        next_day_temp = predict_weather(forecast_data)
    
        next_day_temp[0] = round((next_day_temp[0]-32)*5/9, 1)  #changing high to celsius
        next_day_temp[1] = round((next_day_temp[1]-32)*5/9, 1)  #changing low to celsius
        today = datetime.now().date() #extracting the next day
        next_day = (today + timedelta(days=1)).strftime('%a')
        next_day_temp.append(next_day) #adding the next day to the next_day_temp list to diplay in the result
        
        if forecast_data is not None:
            return render_template("index.html", weather = forecast_data, cur_day = cur_day_temp,  next_day = next_day_temp,city = city_name)
        else:
            return render_template("index.html", error = "Unable to load get the data for the given city name")
        
@app.route('/')
def fun():                                                                                                                                                                                                                                                                                                                  
    return render_template('index.html', error = "")

app.run(debug=True)