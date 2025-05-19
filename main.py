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
        curs=conn.cursor()
        row=curs.execute('''SELECT * FROM show WHERE imdbID=?''', (i['imdbID'],))
        if row==None:
            continue
        
        else:
            print("Film zaten veritabanında mevcut")
        response = requests.get(i['Poster'])
        if response.status_code == 200:
            try:
                with open('./resim/' + i['imdbID'] + '.jpg', 'wb') as file:
                    file.write(response.content)
            except:
                print("Resim kaydedilemedi")
                return 0
def get_resim(imdbID):
    try:
        dizin = './resim/' + imdbID + '.jpg'
        im = Image.open(dizin)
        
        img = ImageTk.PhotoImage(im.resize((64,64)))
        print(f"PhotoImage başarıyla oluşturuldu: {imdbID}.jpg")
        return img
    except FileNotFoundError:
        print(f"Resim dosyası bulunamadı: {dizin}")
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
def get_baglanti():
    #veritabanı bağlantısı
    try:
        conn = sqlite3.connect('veri.db', isolation_level=None)
        print("Veritabanına bağlanıldı")
        return conn
    except sqlite3.Error as e:
        print("Veritabanı bağlantı hatası:", e)
        exit(1) 
set_veritabani()
conn=get_baglanti()
data=get_data("cars")
download_resim(data)

pencere=Tk()
pencere.title("Film Arama")
canvas = Canvas(pencere, width = 100, height = 100)      
canvas.pack()      
imdbID = "tt0071282"
img=get_resim("tt0071282")
lbl=Label(pencere, text="Film Arama", font=("Arial", 20),image=img)  
lbl.image=img
lbl.pack(side=TOP)
mainloop()  
pencere.mainloop()







