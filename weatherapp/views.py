from django.shortcuts import render
from django.contrib.gis.geoip2 import GeoIP2
import requests
from .models import City
from .forms import CityForm
import time

# Create your views here.
def index(request):
    url= 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&appid=a37ca4bee258beb72cf54b2b5cf190f3'
    city = "Las Vegas"
    city_weather = ""

    if request.method == 'POST': #only true if form is submited
        # form = CityForm(request.POST)
        # form.save() # will validate and save if validate
        print(request.POST.items());
        city_weather = requests.get(url.format(request.POST["lat"], request.POST["lon"])).json()
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = None
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        g = GeoIP2()

        try:
            print(ip)
            lat_lon = g.lat_lon(ip)
            city_weather = requests.get(url.format(lat_lon[0], lat_lon[1])).json()
        except:
            url= 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=a37ca4bee258beb72cf54b2b5cf190f3'
            city_weather = requests.get(url.format(city)).json()

    weather_data = []

    weather = {
        'city': city_weather['name'],
        'temperature': city_weather['main']['temp'],
        'description': city_weather['weather'][0]['description'],
        'lat': city_weather['coord']['lat'],
        'lon': city_weather['coord']['lon'],
        'icon': city_weather['weather'][0]['icon'],
    }
    context = weather
    return render(request, 'weatherapp/index.html', context) #returns the index.html template

def forecast(request):
    url = "http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid=a37ca4bee258beb72cf54b2b5cf190f3"
    city_forecast = requests.get(url.format(request.GET['lat'], request.GET['lon'])).json()
    weather_forecast = [{"city": city_forecast['city']['name']}]
    for weather in city_forecast['list']:
        datetime = time.strftime('%b %d %I:%M:%S %p', time.localtime(weather['dt']))
        day = {
            'dt': datetime,
            'description': weather['weather'][0]['description'],
            'icon': weather['weather'][0]['icon'],
            'main': weather['weather'][0]['main'],
            'temperature': {
                'min': weather['main']['temp_min'],
                'max': weather['main']['temp_max'],
            },
        }
        weather_forecast.append(day)

    context = {'weather_forecast': weather_forecast}
    return render(request, 'weatherapp/forecast.html', context)
