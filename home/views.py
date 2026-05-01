import json
import os
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'home/home.html')

def weather(request):
    city = request.GET.get('city', 'Krommenie')
    api_key = settings.OPENWEATHER_API_KEY
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    return JsonResponse(data)

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