from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .models import Map

import json, csv

# Create your views here.
def index(request):
    map = Map(10, 10)

    return render(request, 'pathfinder/index.html', {
        'map': map,
        'state': map.get_state()
    })

def fetch_model(request):
    map_idx = request.GET.get('i')
    
    if map_idx:
        model_data = open(f'pathfinder/static/models/model_m{map_idx}.json')
        loaded = json.load(model_data)
        model_data.close()
        return JsonResponse(loaded)
    else:
        return HttpResponseBadRequest("Didn't find the model.")

def fetch_map(request):
    map_idx = request.GET.get('i')

    if map_idx:
        rows = []
        with open(f'pathfinder/static/maps/m{map_idx}.csv', newline='') as csvfile:
            map_file = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in map_file:
                rows.append([ int(val) for val in row])

        h = len(rows)
        w = len(rows[0])

        map = Map(h, w)
        for r in range(h):
            for c in range(w):
                if (r == 0 and c == 0) or (r == h - 1 and c == w - 1):
                    continue
                if rows[r][c] == 1:
                    map.toggle_wall(r, c)
                    
        return render(request, 'pathfinder/index.html', {
            'map': map,
            'state': map.get_state(),
            'shape': list(map.shape()),
        })
    else:
        return HttpResponseBadRequest("Didn't find the map.")

def greet(request, name):
    return HttpResponse(f"Hello, {name}")

def speak(request, content):
    return HttpResponse(f"Speak {content}")
