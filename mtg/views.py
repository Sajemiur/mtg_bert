from .models import Card
from django.shortcuts import render


def index(request):
    query_set = Card.objects.all()
    context = {'amount': len(query_set)}

    if 'searched' in request.GET:
        context['searched'] = request.GET['searched']

        for elem in request.GET['searched'].split(" "):
            for k, v in Card.query_attributes():
                if elem.startswith(k + ":"):
                    for splitted in elem[len(k) + 1:].split(";"):
                        query_set = query_set.filter(**{v: splitted})
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
