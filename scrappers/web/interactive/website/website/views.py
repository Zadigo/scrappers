from django.core.files import File
from django.utils.dateformat import datetime
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings
import os
from django.views.generic import View
import json
import secrets
import requests

from website.base_volleyball import TeamPage


class HeroView(View):
    def get(self, request, *args, **kwargs):
        token = secrets.token_hex(4)
        return render(request, 'home/index.html', {'token': token})

    def post(self, request, *args, **kwargs):
        url = request.POST.get('url')
        page = TeamPage(url)
        players = page.get_team_page()
        cards = []
        for player in players:
            html = f"""
            <div class="col s12 m4 l4">
                <div class="card">
                    <div class="card-image">
                        <img src="https://www.fivb.org/Vis2009/Images/GetImage.asmx?No=81175&type=Press&height=800&width=400">
                        <span class="card-title">{player['name']}</span>
                    </div>
                    <div class="card-content">
                        <p>{player['name']}</p>
                    </div>
                </div>
            </div>
            """
            cards.append(html)

        path = os.path.join(settings.MEDIA_ROOT, 'template.json')

        # 1. Write file
        with open(path, 'w', encoding='utf-8') as f:
            wrapped_players = {
                'date': datetime.datetime.now().timestamp(),
                'tournament': 'tournament',
                'records': players
            }
            json.dump(wrapped_players, f, indent=4)

        return JsonResponse({'cards': cards})

class DownloadView(View):
    def get(self, request, *args, **kwargs):
        path = os.path.join(settings.MEDIA_ROOT, 'template.json')
        # 2. Dowload file
        with open(path, 'rb') as f:
            response = HttpResponse(content=f.read(), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)
        return response

url = 'https://raw.githubusercontent.com/Zadigo/scrappers/master/tennis/WTA/matches.json'
response = requests.get(url).json()

class TennisView(View):
    def get(self, request, *args, **kwargs):
        tournaments = []
        for tournament in response['records']:
            html = f"""
            <div class="col s12 m4 l4">
                <div class="card">
                    <div class="card-image">
                        <img src="https://materializecss.com/images/sample-1.jpg">
                        <span class="card-title">{tournament['tournament']}</span>
                    </div>
                    <div class="card-content">
                        <p>{tournament['tournament']}</p>
                    </div>
                    <div class="card-action">
                        <a href="http://127.0.0.1:8000/tennis/{tournament['id']}" 
                                data-id="{tournament['id']}">Detail</a>
                    </div>
                </div>
            </div>
            """
            tournaments.append(html)
        return render(request, 'pages/page.html', {'tournaments': tournaments})

class TennisDetailView(View):
    def get(self, request, *args, **kwargs):
        tour_id = kwargs['pk']
        for tournament in response['records']:
            if int(tour_id) == tournament['id']:
                break
        return render(request, 'pages/detail.html', {'tournament': tournament})
        