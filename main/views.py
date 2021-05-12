from django.shortcuts import render,redirect,HttpResponseRedirect
from django.views import View
from django.contrib import messages
import requests
import os
import json
from djangoproject.settings import BASE_DIR
# Create your views here.
def bad_request(request, *args):
     return redirect('/')
class DeleteCard(View):
    def post(self, request, number):
         del request.session['cities'][number]
         request.session.modified = True
         return redirect('/')

class MainView(View):
    def day_or_night(self, currenttime, sunrisetime, sunsettime):
        if int(currenttime) < int(sunrisetime):
            return "night"
        elif int(currenttime) < int(sunsettime):
            return "day"
        else:
            return "evening-morning"

    def get(self, request):
        if request.session.get('cities'):
            sp = []
            for el in request.session.get('cities'):
                res = requests.get(
                    'http://api.openweathermap.org/data/2.5/weather?q={}&appid=34f118c924d172de600a728aacb501b6&units=metric'.format(
                        el))
                dict_with_weather_info = {'name': json.loads(res.content)['name'].upper(),
                                          'temp': int(json.loads(res.content)['main']['temp']),
                                          'weather': str(json.loads(res.content)['weather'][0]['description']).title(),
                                          'id': request.session.get('cities').index(el),
                                          'pic': self.day_or_night(json.loads(res.content)['dt'],
                                                              json.loads(res.content)['sys'].get('sunrise'),
                                                              json.loads(res.content)['sys'].get('sunset')
                                                              )}
                sp.append(dict_with_weather_info)
            return render(request, os.path.join(BASE_DIR,'main/templates/main/index.html'), {'weather':reversed(sp)})
        else:
            return render(request, os.path.join(BASE_DIR,'main/templates/main/index.html'))

    def post(self, request):
        if not request.session.get('cities'):
            request.session['cities'] = []
        city_name = request.POST.get('city_name')
        check = requests.get(
            'http://api.openweathermap.org/data/2.5/weather?q={}&appid=34f118c924d172de600a728aacb501b6&units=metric'.format(
                city_name))
        if city_name == '':
            return redirect('/')
        elif json.loads(check.content)['cod'] == '404':
            messages.error(request, "The city doesn't exist!")
            return redirect('/')
        elif json.loads(check.content)['name'].lower() in request.session.get('cities'):
            messages.error(request, "The city has already been added to the list!")
            return redirect('/')
        else:
            ct = request.session.get('cities')
            if not ct:
                ct = []
                ct.append(json.loads(check.content)['name'].lower())
                request.session['cities'] = ct
            else:
                request.session['cities'].append(json.loads(check.content)['name'].lower())
                request.session.modified = True
            return redirect('/')
