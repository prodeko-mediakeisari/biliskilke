from django.shortcuts import render_to_response, redirect, render
from django.forms import ModelForm
from django.http import HttpResponse
from django.template import RequestContext
from bilis.models import Player, Game
from bilis.forms import PlayerForm, ResultForm, ImageUploadForm
from bilis import utils
import json

def index(request):
    form = ResultForm()
    players = Player.objects.all().order_by('-elo')[:20]
    latest_games = Game.objects.all().order_by('-datetime')[:20]
    return render_to_response('index.html',{
                'form': form,
                'players': players,
                'latest_games' : latest_games
        }, context_instance=RequestContext(request))

def add_result(request):
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bilis.views.index')
        else:
            players = Player.objects.all().order_by('-elo')[:20]
            latest_games = Game.objects.all().order_by('-datetime')[:20]
            return render_to_response('index.html',{
                 'form': form,
                 'players': players,
                 'latest_games' : latest_games
                 }, context_instance=RequestContext(request))
    return redirect('bilis.views.index')

def new_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.favorite_color = utils.html_color_to_int(form.cleaned_data['favorite_color_string'])
            player.save()
            return redirect('bilis.views.index')
    else:
        form = PlayerForm()
    return render_to_response('new_player.html',{
                'form': form,
        }, context_instance=RequestContext(request))

def players(request):
    players = Player.objects.all().order_by('-elo')
    return render_to_response('players.html',{
                'players': players
        }, context_instance=RequestContext(request))

def ajax_player_network(request):
    struct = {}
    nodes = []
    links = []
    for player in Player.objects.all().order_by('pk'):
        item = {}
        item['name'] = player.name
        nodes.append(item)
    link_dict = {}
    for game in Game.objects.all():
        winner_id = game.winner.pk
        loser_id = game.loser.pk
        t = (winner_id, loser_id)
        reverse_t = (loser_id, winner_id)
        if t in link_dict:
            link_dict[t] += 1
        elif reverse_t in link_dict:
            link_dict[reverse_t] += 1
        else:
            link_dict[t] = 1
    for link in link_dict:
        source = link[0]
        target = link[1]
        value = link_dict[link]
        item = {}
        item['source']=source
        item['target']=target
        item['value']=value
        links.append(item)
    struct['links'] = links
    struct['nodes'] = nodes
    return HttpResponse(json.dumps(struct, sort_keys=True,
                  indent=4, separators=(',', ': ')), content_type='application/json')
                  
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            #import pdb; pdb.set_trace()
            handle_image(request.FILES['image'])
            return redirect('bilis.views.index')
    else:
        form = ImageUploadForm()
    return render_to_response('file_form.html', {'form': form}, context_instance=RequestContext(request))
        
def handle_image(file):
    with open('bilis/static/uploads/image.jpg', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
