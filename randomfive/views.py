import requests
import vk_api

from django.http import HttpResponse
from django.shortcuts import render, redirect

from randomfive.forms import NameForm


client_id = '7637878'
client_secret = 'qw3PXN0wzJGwAbXLlRrO'
redirect_uri = 'http://127.0.0.1/auth'


def auth(request):
    if request.method == 'GET':
        if 'code' in request.GET:
            code = request.GET['code']

            query = f'https://oauth.vk.com/access_token?client_id={client_id}&client_secret={client_secret}' \
                    f'&redirect_uri=http://127.0.0.1:8000/auth&code={code} '
            response = requests.get(query)
            token = response.json()['access_token']
            login = response.json()['user_id']
            html = HttpResponse('Password OK, redirecting<meta http-equiv="refresh" content="1;URL=/" />')
            html.set_cookie('randomfive', token)
            html.set_cookie('login', login)
            return html

        form = NameForm()
        return render(request, 'randomfive/template.html', {'form': form})

    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            VK = vk_api.VkApi(login, password)
            try:
                VK.auth()
                token = VK.token['access_token']
                login = VK.login
                html = HttpResponse('Password OK, redirecting<meta http-equiv="refresh" content="1;URL=/" />')
                html.set_cookie('randomfive', token)
                html.set_cookie('login', login)
                return html
            except vk_api.BadPassword:
                return HttpResponse("Bad Password")


def showfriends(request):
    if request.COOKIES.get('randomfive'):
        # запрос френдов
        token = request.COOKIES.get('randomfive')
        login = request.COOKIES.get('login')
        vk = vk_api.VkApi(token=token)
        vk = vk.get_api()
        vk_data = vk.friends.get(order='random', count=5, fields='nickname, photo')['items']
        return render(request, 'randomfive/out.html', {'vk_data': vk_data})
    else:
        return redirect('/auth')


def delete_cookie(request):
    if request.COOKIES.get('randomfive'):
        response = HttpResponse("Logged out")
        response.delete_cookie('randomfive')
    else:
        response = HttpResponse("Need to log in before log out")
    return response
