import requests
import http.client
import json
def get_anahtar():
    dosya=open('anahtar.txt',encoding='UTF-8', mode='r')
    anahtar=dosya.read()
    dosya.close()
    return str(anahtar)


def get_resim(data):
    if not data['success']:
        print("Arama başarısız")
        return 0
    for i in data['result']:
        response = requests.get(i['Poster'])
        print(i['Poster'])
        if response.status_code == 200:

            try:
                with open('./resim/' + i['imdbID'] + '.jpg', 'wb') as file:
                    file.write(response.content)
            except:
                print("Resim kaydedilemedi")
                return 0

conn = http.client.HTTPSConnection("api.collectapi.com")
headers = {
     'content-type': "application/json",
     'authorization': get_anahtar()
     }
try:
    conn.request("GET", "/imdb/imdbSearchByName?query=cars", headers=headers)
except Exception as e:
    print("Hata:", e)
    exit(1)

res = conn.getresponse()
data = res.read()
data = json.loads(data)
print(data)
get_resim(data)






