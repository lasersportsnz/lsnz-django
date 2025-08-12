from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.templatetags.static import static

def index(request):
    template = loader.get_template("lsnz/base.html")
    context = {}
    return HttpResponse(template.render(context, request))

def events(request):
    template = loader.get_template("lsnz/events.html")
    context = {}
    return HttpResponse(template.render(context, request))

def sites(request):
    template = loader.get_template("lsnz/sites.html")
    context = {}
    return HttpResponse(template.render(context, request))

def players(request):
    template = loader.get_template("lsnz/players.html")
    context = {}
    return HttpResponse(template.render(context, request))
