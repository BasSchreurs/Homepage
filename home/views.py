import json
import os
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate
from datetime import datetime, timezone
from calendar import timegm
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render(request, 'home/home.html', {
        'api_base': '/home' if os.environ.get('FORCE_SCRIPT_NAME') else '',
    })


def weather(request):
    city = request.GET.get('city', 'Krommenie')
    api_key = settings.OPENWEATHER_API_KEY

    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&cnt=1'

    weather_response = requests.get(weather_url).json()
    forecast_response = requests.get(forecast_url).json()

    weather_response['pop'] = forecast_response['list'][0]['pop']

    return JsonResponse(weather_response)


def news(request):
    url = 'https://feeds.nos.nl/nosnieuwsalgemeen'
    response = requests.get(url, timeout=5)
    root = ET.fromstring(response.content)

    items = []
    for item in root.findall('./channel/item')[:8]:
        pub_date = item.findtext('pubDate')
        parsed = parsedate(pub_date)
        timestamp = timegm(parsed) if parsed else 0

        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        formatted_time = dt.strftime('%H:%M')

        items.append({
            'title': item.findtext('title'),
            'link': item.findtext('link'),
            'time': formatted_time,
            'timestamp': timestamp,
        })

    items.sort(key=lambda x: x['timestamp'], reverse=True)
    for item in items:
        del item['timestamp']

    return JsonResponse({'items': items})


@csrf_exempt
def favorites(request):
    fav_file = os.path.join(settings.BASE_DIR, 'favorites.json')

    if request.method == 'GET':
        if os.path.exists(fav_file):
            with open(fav_file) as f:
                return JsonResponse(json.load(f), safe=False)
        return JsonResponse([], safe=False)

    if request.method == 'POST':
        body = json.loads(request.body)
        favs = []
        if os.path.exists(fav_file):
            with open(fav_file) as f:
                favs = json.load(f)
        favs.append(body)
        with open(fav_file, 'w') as f:
            json.dump(favs, f)
        return JsonResponse({'success': True})

    if request.method == 'DELETE':
        body = json.loads(request.body)
        if os.path.exists(fav_file):
            with open(fav_file) as f:
                favs = json.load(f)
            favs = [f for f in favs if f['id'] != body['id']]
            with open(fav_file, 'w') as f:
                json.dump(favs, f)
        return JsonResponse({'success': True})


@csrf_exempt
def notes(request):
    notes_file = os.path.join(settings.BASE_DIR, 'notes.txt')

    if request.method == 'GET':
        if os.path.exists(notes_file):
            with open(notes_file) as f:
                return JsonResponse({'notes': f.read()})
        return JsonResponse({'notes': ''})

    if request.method == 'POST':
        body = json.loads(request.body)
        with open(notes_file, 'w') as f:
            f.write(body.get('notes', ''))
        return JsonResponse({'success': True})