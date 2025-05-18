import requests
import http.client
import json
import sqlite3
from tkinter import *
from PIL import Image, ImageTk
def get_anahtar():
    dosya=open('anahtar.txt',encoding='UTF-8', mode='r')
    anahtar=dosya.read()
    dosya.close()
    return str(anahtar)

def download_resim(data):
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
def get_resim(imdbID):
    
    try:
        im = Image.open('./resim/' + imdbID + '.jpg')
        img = ImageTk.PhotoImage(im.resize((64,64)))
        return img
    except:
        print("Resim bulunamadı")
        return None
def get_data(film_adi):
    conn = http.client.HTTPSConnection("api.collectapi.com")
    headers = {
        'content-type': "application/json",
        'authorization': "apikey "+get_anahtar()
        }
    try:
        conn.request("GET", "/imdb/imdbSearchByName?query="+film_adi.replace(" ","%20"), headers=headers)
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)
        return data
    except Exception as e:
        print("Hata:", e)
        exit(1)
def set_veritabani():
    #veritabanı bağlantısı ve tablo oluşturma
    root = sqlite3.connect('veri.db',isolation_level = None)
    cursor = root.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS show (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year TEXT,
            imdbID TEXT NOT NULL,
            type TEXT,
            poster TEXT
        )
    ''')
    root.commit()
conn=set_veritabani
data=get_data("cars")

img = get_resim("tt0071282")
pencere = Tk()
pencere.title("Film Arama")
yazi = Label(pencere, text="Film Adı", bg="blue", anchor="w", image=img)
yazi.image = img  # Keep a reference to the image

yazi.pack(anchor="w")
pencere.mainloop()







