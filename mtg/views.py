from .models import Card
from django.shortcuts import render
# from django.db import OperationalError
# from sqlite3 import OperationalError
from sqlalchemy.exc import OperationalError

def index(request):
    query_set = Card.objects.all()
    context = {'amount': len(query_set)}

    class OverqueriedException(Exception):
        pass

    if 'searched' in request.GET:
        context['searched'] = request.GET['searched']
        block = 0
        try:
            for elem in request.GET['searched'].split(" "):
                for k, v in Card.query_attributes():
                    if elem.startswith(k + ":"):
                        for splitted in elem[len(k) + 1:].split(";"):
                            block += 1
                            if block == 100:
                                raise OverqueriedException
                            else:
                                query_set = query_set.filter(**{v: splitted})
                        break
                else:
                    block += 1
                    if block == 100:
                        raise OverqueriedException
                    else:
                        query_set = query_set.filter(name__contains=elem)
        except OverqueriedException:
            context['query_error'] = "Too long query! Only first 100 query elements were processed..."

    if 'lookup' in request.GET:
        if len(query_set) > 0:
            context['card_lookup'] = query_set
        elif 'query_error' in context:
            context['query_error'] += "No cards found for given query."
        else:
            context['query_error'] = "No cards found for given query."

    elif 'search' in request.GET:
        if len(query_set) == 1:
            context['synergy_card'] = query_set[0]
        elif 'query_error' in context:
            context['query_error'] += "No cards found for given query, or too many cards found for searching" \
                                      "synergy.\nUse 'Lookup a card' to find a single card of choice."
        else:
            context['query_error'] = "No cards found for given query, or too many cards found for searching" \
                                     "synergy.\nUse 'Lookup a card' to find a single card of choice."

    return render(request, 'mtg/index.html', context)
