import json
from mtg.models import Color, Subtype, Supertype, Type, Card
from requests import get
from tqdm import tqdm

def data_fill():
    with open('../ShortenedPioneerCards.json', 'r', encoding="utf8") as f:
        cards = json.load(f)

    for name, card in tqdm(cards.items()):
        c = Card.objects.filter(name=name)
        # print("-----NEXT CARD------")
        if len(c) == 0:
            # print("New card")

            addr = "https://api.scryfall.com/cards/named?exact=" + name.replace(" ", "+")
            response = get(addr)
            struct = json.loads(response.text)
            if "card_faces" in struct and "image_uris" not in struct:
                struct = struct[ "card_faces" ][ 0 ]

            # print(struct[ "image_uris" ][ "normal" ])

            c = Card(name,
                     cmc=card['convertedManaCost'],
                     manaCost=card['manaCost'] if 'manaCost' in card else "",
                     text=card[ 'text' ] if 'text' in card else "",
                     power=card['power'] if 'power' in card else "",
                     toughness=card['toughness'] if 'toughness' in card else "",
                     img=struct["image_uris"]["normal"])
            c.save()

            for color in card['colors']:
                q = Color.objects.filter(name=color)
                if len(q) == 0:
                    q = [Color.objects.create(name=color)]
                c.colors.add(q[0])

            for type in card['types']:
                q = Type.objects.filter(name=type)
                if len(q) == 0:
                    q = [Type.objects.create(name=type)]
                c.types.add(q[0])

            for subtype in card['subtypes']:
                q = Subtype.objects.filter(name=subtype)
                if len(q) == 0:
                    q = [Subtype.objects.create(name=subtype)]
                c.subtypes.add(q[0])

            for supertype in card['supertypes']:
                q = Supertype.objects.filter(name=supertype)
                if len(q) == 0:
                    q = [Supertype.objects.create(name=supertype)]
                c.supertypes.add(q[0])
        else:
            try:
                c = c[0]
                # print("Existing card", c)
                addr = "https://api.scryfall.com/cards/named?exact=" + name.replace(" ", "+")
                response = get(addr)
                struct = json.loads(response.text)
                if "card_faces" in struct and "image_uris" not in struct:
                    struct = struct["card_faces"][0]
                # print(struct["image_uris"]["normal"])
                c.img = struct["image_uris"]["normal"]
                c.save()
            except Exception:
                print("Error for following address:", addr)


def synergies_fill():
    from mtg.mtg_processor import prepare_test_data
    from mtg.mtg_bert import predict

    with open('../ShortenedPioneerCards.json', 'r', encoding="utf8") as f:
        cards = json.load(f)

    for name in tqdm(cards.keys()):
        df = prepare_test_data(Card.objects.get(name=name))
        result = predict(df)


        df = prepare_test_data(get_object_or_404(Card, name=request.GET[ 'searched' ]))
        df = np.split(df.sample(frac=1, random_state=42), [ 100, 350, 1550 ])
        result = predict(df)

        result.to_csv('data/result.csv', index=None)

        c = Card.objects.filter(name=name)
        # print("-----NEXT CARD------")
        if len(c) == 0:
            # print("New card")

            addr = "https://api.scryfall.com/cards/named?exact=" + name.replace(" ", "+")
            response = get(addr)
            struct = json.loads(response.text)
            if "card_faces" in struct and "image_uris" not in struct:
                struct = struct[ "card_faces" ][ 0 ]

            # print(struct[ "image_uris" ][ "normal" ])

            c = Card(name,
                     cmc=card['convertedManaCost'],
                     manaCost=card['manaCost'] if 'manaCost' in card else "",
                     text=card[ 'text' ] if 'text' in card else "",
                     power=card['power'] if 'power' in card else "",
                     toughness=card['toughness'] if 'toughness' in card else "",
                     img=struct["image_uris"]["normal"])
            c.save()

            for color in card['colors']:
                q = Color.objects.filter(name=color)
                if len(q) == 0:
                    q = [Color.objects.create(name=color)]
                c.colors.add(q[0])

            for type in card['types']:
                q = Type.objects.filter(name=type)
                if len(q) == 0:
                    q = [Type.objects.create(name=type)]
                c.types.add(q[0])

            for subtype in card['subtypes']:
                q = Subtype.objects.filter(name=subtype)
                if len(q) == 0:
                    q = [Subtype.objects.create(name=subtype)]
                c.subtypes.add(q[0])

            for supertype in card['supertypes']:
                q = Supertype.objects.filter(name=supertype)
                if len(q) == 0:
                    q = [Supertype.objects.create(name=supertype)]
                c.supertypes.add(q[0])
        else:
            try:
                c = c[0]
                # print("Existing card", c)
                addr = "https://api.scryfall.com/cards/named?exact=" + name.replace(" ", "+")
                response = get(addr)
                struct = json.loads(response.text)
                if "card_faces" in struct and "image_uris" not in struct:
                    struct = struct["card_faces"][0]
                # print(struct["image_uris"]["normal"])
                c.img = struct["image_uris"]["normal"]
                c.save()
            except Exception:
                print("Error for following address:", addr)
