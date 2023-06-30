from flask import Flask, render_template, request
import requests


app = Flask(__name__)
weather_data = {}

def get_weatherData(name):
    url = "https://weather-by-api-ninjas.p.rapidapi.com/v1/weather"

    querystring = {"city":name}

    headers = {
        "X-RapidAPI-Key": "b2201a8335msh67fe7547b34b586p196132jsn4b087bef3184",
        "X-RapidAPI-Host": "weather-by-api-ninjas.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
@app.route('/', methods = ['GET', 'POST'])
def fun():
    global weather_data
    if(request.method == 'POST'):
        name = request.form['city']
        weather = get_weatherData(name)
        
        if weather is not None:
            weather_data = weather
            return render_template("index.html", weather = weather, city = name)
        else:
            return render_template("index.html", error = "Unable to load get the data for the given city name")
    weather_data = {}                                                                                                                                                                                                                                                                                                                    
    return render_template('index.html')

app.run(debug=True)