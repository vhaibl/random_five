import requests
import vk_api
from django.http import HttpResponse
from django.shortcuts import render, redirect

from randomfive.forms import NameForm

client_id = '7637878'
client_secret = 'qw3PXN0wzJGwAbXLlRrO'
redirect_uri = 'http://127.0.0.1:8000/auth'


def auth(request):
    if request.method == 'GET':
        if 'code' in request.GET:  # 'code' in request means Oauth selected, obtaining token from VK with Oauth
            code = request.GET['code']
            query = f'https://oauth.vk.com/access_token?client_id={client_id}&client_secret={client_secret}' \
                    f'&redirect_uri={redirect_uri}&code={code} '
            response = requests.get(query)
            token = response.json()['access_token']
            html = HttpResponse('Password OK, redirecting<meta http-equiv="refresh" content="1;URL=/" />')
            html.set_cookie('randomfive', token)  # setting COOKIE with token  (logging in)
            return html

        form = NameForm()
        return render(request, 'randomfive/auth.html', {'form': form, 'client_id': client_id, 'host': redirect_uri})

    if request.method == 'POST':  # post method when login\pass form filled, obtaining token with VK_api
        form = NameForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            vk = vk_api.VkApi(login, password)
            try:
                vk.auth()
                token = vk.token['access_token']
                html = HttpResponse('Password OK, redirecting<meta http-equiv="refresh" content="1;URL=/" />')
                html.set_cookie('randomfive', token)  # setting COOKIE with token (logging in)
                return html
            except vk_api.BadPassword:
                return HttpResponse("Bad Password")


def showfriends(request):
    if request.COOKIES.get('randomfive'):
        token = request.COOKIES.get('randomfive')  # getting token from COOKIE
        vk = vk_api.VkApi(token=token)
        vk = vk.get_api()
        user = vk.users.get()
        name = user[0]['first_name'] + ' ' + user[0]['last_name']  # obtaining user name
        vk_data = vk.friends.get(order='random', count=5, fields='nickname, photo')['items']
        return render(request, 'randomfive/out.html', {'vk_data': vk_data, 'name': name})
    else:
        return redirect('/auth')


def delete_cookie(request):
    if request.COOKIES.get('randomfive'):
        response = HttpResponse('Logged out, redirecting<meta http-equiv="refresh" content="1;URL=/auth" />')
        response.delete_cookie('randomfive')  # deleting COOKIE (logging out)
    else:
        response = HttpResponse("Need to log in before log out")
    return response
