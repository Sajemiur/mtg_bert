from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Card
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic.base import TemplateView
from django.shortcuts import render
import pandas as pd
import numpy as np
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from .apps import MtgConfig
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    context = {}
    query_set = Card.objects.all()

    if 'searched' in request.GET:
        context['searched'] = request.GET['searched']

        for elem in request.GET['searched'].split(" "):
            for attr in Card.attributes():
                if elem.startswith(attr + ":"):
                    for splitted in elem[len(attr) + 1:].split(";"):
                        query = {attr: splitted}
                        print(query)
                        query_set = query_set.filter(**query)
                    break
            else:
                query_set = query_set.filter(name__contains=elem)

    if 'lookup' in request.GET:
        if len(query_set) == 0:
            context['query_error'] = True
        else:
            context['card_lookup'] = query_set

    elif 'search' in request.GET:
        if len(query_set) == 1:
            context['synergy_card'] = query_set[0]
        else:
            context['query_error'] = True

    return render(request, 'mtg/index.html', context)


@csrf_exempt
def call_model(request):
    if 'searched' in request.POST:
        searched = request.POST.get('searched')
        return StreamingHttpResponse(MtgConfig.predictor.predict(searched))

