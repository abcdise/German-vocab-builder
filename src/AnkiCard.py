import json
import requests
import urllib.request

class AnkiCommunicator:

    def __get_request(self, action, params):
        return {'action': action, 'params': params, 'version': 6}
    

    def __invoke(self, action, params):
        requestJson = json.dumps(self.__get_request(action, params)).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
        if 'error' not in response or response['error'] is not None:
            raise Exception('Failed to fetch card info: {}'.format(response.get('error')))
        return response['result']
    

    def __get_cards_id_in_n_days(self, n:int, deck_name:str):
        param = dict()
        param['query'] = f'prop:due<{n} deck:"{deck_name}"'
        
        data = self.__get_request('findNotes', param)
        response = requests.post('http://localhost:8765', json=data)
        notes = response.json().get('result', [])
        return notes
    

    def get_words_in_n_days(self, n:int, deck_name:str, item:str):
        '''
        Get the card content from the cards that are due in `n` days.
        For `item`, possible options are `Front`, `Back`.
        '''
        card_ids = self.__get_cards_id_in_n_days(n=n, deck_name=deck_name)
        result = self.__invoke('cardsInfo', {'cards': card_ids})
        info_list = []
        for elem in result:
            info = elem['fields'][item]['value']
            info_list.append(info)

        return list(set(info_list))
