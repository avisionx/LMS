from books import bookJson
import json
import random

data = []

for book in bookJson:
    try:
        k = book['thumbnailUrl']
        if(len(book['authors']) != 0):
            obj = {}
            # obj['_id'] = book['_id']
            obj['title'] = book['title']
            obj['thumbnailUrl'] = book['thumbnailUrl']
            obj['shortDescription'] = book['shortDescription']
            obj['longDescription'] = book['longDescription']
            obj['authors'] = ",".join(book['authors'])
            obj['isbn'] = book['isbn']
            obj['categories'] = ",".join(book['categories'])
            obj['rack'] = book['title'][0] + '-' + book['isbn'][0:4]
            obj['issued'] = 'none'
            data.append(obj)
    except:
        pass

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)