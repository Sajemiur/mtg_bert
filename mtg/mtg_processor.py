import pandas as pd
import json
import numpy as np
import random
from .models import Card


def card_concat(card):
    string = ' [NAME] ' + card.name
    string += ' [CLR] ' + "".join([c.name for c in card.colors.all()])
    string += ' [CMC] ' + str(card.cmc)
    string += ' [MANA] ' + card.manaCost
    string += ' [UTYP] ' + " ".join([c.name for c in card.subtypes.all()])
    string += ' [STYP] ' + " ".join([c.name for c in card.supertypes.all()])
    string += ' [TYP] ' + " ".join([c.name for c in card.types.all()])
    string += ' [PWR] ' + card.power
    string += ' [TGH] ' + card.toughness
    string += ' [TXT] ' + card.text
    return string


def prepare_prediction_data(card):
    card = Card.objects.get(name=card)

    df = pd.DataFrame()
    df["card_b"] = list(card_concat(elem) for elem in Card.objects.all())
    df["card_a"] = [card_concat(card)] * len(df)

    return [c.name for c in Card.objects.all()], [c.img for c in Card.objects.all()], df
