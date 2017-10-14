from flask import Flask, send_from_directory, jsonify
from datetime import datetime, timedelta
import json
import requests
from flask.globals import request
import operator
import isodate
import duration

"""
TODO
1. Checks to see if there are no items returned.
"""

app = Flask(__name__, static_url_path='')
api_key = ''

def parse_results(results):
    items = []
    for result in results:
        for item in result['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
            obj = {
                'title': item['title'][0],
                'link' : item['viewItemURL'][0],
                'price' : item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                'timeLeft' : isodate.parse_duration(item['sellingStatus'][0]['timeLeft'][0]),
                'listingType' : item['listingInfo'][0]['listingType'][0]
                }
            items.append(obj)  
    items.sort(key=operator.itemgetter('timeLeft'))
    for item in items:
        item['timeLeft'] = duration.to_iso8601(item['timeLeft']) 
    return items

def check_response(res):
    if (res['findItemsAdvancedResponse'][0]['ack'][0] == 'Success' and 
    res['findItemsAdvancedResponse'][0]['searchResult'][0]['@count'] != '0'):
        return True
    else:
        return False 
    
 
@app.route("/")
def hello():
    return send_from_directory('./views', 'home.html')

@app.route("/node_modules/<path:path>")
def node_modules(path):
    return send_from_directory('./node_modules/', path)
 
@app.route("/controllers/<path:path>")
def controllers(path):
    return send_from_directory('./controllers/', path)

@app.route("/views/<path:path>")
def views(path):
    return send_from_directory('./views/', path)

@app.route("/getCurrentProducts")
def get_current_products():
    with open('files/movies.json') as movie_file:
        json_data = json.load(movie_file)
        return jsonify(json_data)
    
@app.route("/saveCurrentProducts", methods = ['POST'])
def save_current_products():
    with open('files/movies.json', 'w') as movie_file:
        movie_file.write(request.data)
    return "Ok"

@app.route("/findItems")
def find_items():
    items = []
    date = datetime.utcnow() + timedelta(hours=5)
    date = date.isoformat()
    
    call_obj = {
        'url' : 'http://svcs.ebay.com/services/search/FindingService/v1?',
        'op-name': 'OPERATION-NAME=findItemsAdvanced&', 
        'service-ver': 'SERVICE-VERSION=1.0.0&',
        'api_key': 'SECURITY-APPNAME=' + api_key + '&',
        'response': 'RESPONSE-DATA-FORMAT=JSON&',
        'rest': 'REST-PAYLOAD&',
        'itemFilter0' : 'itemFilter(0).name=ListingType&' + 'itemFilter(0).value(0)=',
        'itemFilter0Fixed' : 'itemFilter(0).name=ListingType&' + 'itemFilter(0).value(0)=FixedPrice&',
        'itemFilter1' : 'itemFilter(1).name=Currency&' + 'itemFilter(1).value=USD&',
        'itemFilter2' : 'itemFilter(2).name=FeedbackScoreMin&' + 'itemFilter(2).value=4&', 
        'itemFilter3' : 'itemFilter(3).name=MaxPrice&' + 'itemFilter(3).value=',
        'itemFilter4' : 'itemFilter(4).name=EndTimeTo&' + 'itemFilter(4).value=' + str(date) + '&',
        'sort' : 'sortOrder=PricePlusShippingLowest'
    }
    
    with open('files/movies.json', 'r') as movie_file:
        movies = json.load(movie_file)
        for movie in movies:
            r = requests.get(call_obj['url'] + 
                             call_obj['op-name'] + 
                             call_obj['service-ver'] + 
                             call_obj['api_key'] + 
                             call_obj['response'] + 
                             call_obj['rest'] + 
                             'keywords=' + movie['upc'] + '&' + 
                             call_obj['itemFilter0'] + 'Auction&' + 
                             call_obj['itemFilter1'] + 
                             call_obj['itemFilter2'] + 
                             call_obj['itemFilter3'] + movie['maxPrice'] + '&' +
                             call_obj['itemFilter4'] + 
                             call_obj['sort']
                             )
            
            if check_response(json.loads(r.content)):
                items.append(json.loads(r.content))
    
            r = requests.get(call_obj['url'] + 
                             call_obj['op-name'] + 
                             call_obj['service-ver'] + 
                             call_obj['api_key'] + 
                             call_obj['response'] + 
                             call_obj['rest'] + 
                             'keywords=' + movie['upc'] + '&' + 
                             call_obj['itemFilter0'] + 'FixedPrice&' +
                             call_obj['itemFilter1'] + 
                             call_obj['itemFilter2'] + 
                             call_obj['itemFilter3'] + movie['maxPrice'] + '&' + 
                             call_obj['sort']
                             )
            
            if check_response(json.loads(r.content)):
                items.append(json.loads(r.content))

        if len(items) == 0:
            return 'NoResults'
        else:
            results = parse_results(items)
            return jsonify(results)

if __name__ == "__main__":
    app.run()