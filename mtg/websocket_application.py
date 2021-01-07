import json
from html import unescape


class WebsocketClass:
    def __init__(self):
        self.cache = {}
        # from .mtg_bert import Model
        # self.predictor = Model()

    async def websocket_application(self, scope, receive, send):
        while True:
            event = await receive()

            if event['type'] == 'websocket.connect':
                from .mtg_bert import Model
                predictor = Model()
                sum = {}
                it = 1
                await send({
                    'type': 'websocket.accept'
                })

            elif event['type'] == 'websocket.disconnect':
                break

            elif event['type'] == 'websocket.receive':
                if event['text'] in self.cache:
                    await send({'type': 'websocket.send',
                                'text': self.parse_to_html(self.cache[event['text']])})
                else:
                    buff = 0

                    async for batch in predictor.predict(unescape(event['text'])):
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

    @staticmethod
    def parse_to_html(mtg_dict, load_div=-1):
        ret = ""
        for name, (img, ch) in sorted(mtg_dict.items(), key=lambda item: float(item[1][1]), reverse=True):
            ret += '<div class="card_container"><div class="img_container">'\
                   '<img src="{}" loading="lazy" alt="{}"/></div></br>{}%</div>'.format(img, name, ch)
            if load_div != -1:
                ret += '<div class="card_container"><div class="lds-dual-ring"></div></div>'\
                       * (1 + int(7 / load_div))
        return ret
