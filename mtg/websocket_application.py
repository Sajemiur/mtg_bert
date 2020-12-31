# from .apps import MtgConfig
import json


class WebsocketClass:
    def __init__(self):
        self.cache = {}

    async def websocket_application(self, scope, receive, send):
        while True:
            event = await receive()
            print("RECEIVED")
            if event['type'] == 'websocket.connect':
                from .mtg_bert import Model
                predictor = Model()
                sum = {}
                it = 1
                await send({
                    'type': 'websocket.accept'
                })
                print("done")

            elif event['type'] == 'websocket.disconnect':
                print("diconnect")
                break

            elif event['type'] == 'websocket.receive':
                print("got here")
                if event['text'] in self.cache:
                    await send({'type': 'websocket.send',
                                'text': self.parse_to_html(self.cache[event['text']])})
                else:
                    buff = 0
                    async for batch in predictor.predict(event['text']):
                        sum.update(batch)
                        buff += 1
                        if buff == int(it):
                            await send({'type': 'websocket.send',
                                        'text': self.parse_to_html(sum, it)})
                            buff = 0
                            it += 0.67
                    await send({'type': 'websocket.send',
                                'text': self.parse_to_html(sum)})
                    self.cache[event['text']] = sum



    def parse_to_html(self, mtg_dict, load_div=-1):
        ret = ""
        highest = True
        for img, ch in sorted(mtg_dict.items(), key=lambda item: float(item[1]), reverse=True):
            if highest is True:
                print(ch)
                highest = False
            ret += '<div class="card_container"><img src="{}" loading="lazy"/>{}%</div>'.format(img, ch)
            if load_div != -1:
                ret += '<div class="card_container"><img src="https://media2.giphy.com/media/3oEjI6SIIHBdRxXI40/200.gif" loading="lazy"/></div>'\
                       * int(0.9 + 7 / load_div)
        return ret
