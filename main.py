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
        curs.execute('''SELECT imdbID FROM show WHERE imdbID=?''', (i['imdbID'],))
        row=curs.fetchone()
        if row!=None:
            print("Resim zaten var")
            continue            
        
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
        
        img = ImageTk.PhotoImage(im.resize((150,222)))
        print(f"PhotoImage başarıyla oluşturuldu: {imdbID}.jpg")
        return img
    except FileNotFoundError:
        print(f"Resim dosyası bulunamadı: {dizin}")
        return None
    
def get_data(film_adi):
    #türkçe karakterleri filtreliyoruz
    Tr2En = str.maketrans("ÇĞİÖŞÜçğıöşüâ", "CGIOSUcgiosua")
    film_adi=film_adi.translate(Tr2En)
    #boşlukları url olarak okunabilsin diye %20 ile değiştirilir
    film_adi=film_adi.replace(" ","%20")

    conn = http.client.HTTPSConnection("api.collectapi.com")
    headers = {
        'content-type': "application/json",
        'authorization': "apikey "+get_anahtar()
        }
    try:
        conn.request("GET", "/imdb/imdbSearchByName?query="+film_adi, headers=headers)
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)
        download_resim(data)

        root=get_baglanti()
        cursor=root.cursor()
        item_list=[]
        for i in data['result']:
            item_tuple = (
                i.get('Title'),   # values ? dict okuyamadığı için list içinde tuple lar oluşturuyoruz 
                i.get('Year'),     
                i.get('imdbID'),   
                i.get('Type'),     
                i.get('Poster'))
            item_list.append(item_tuple)
        try:
            cursor.executemany(
                '''INSERT INTO show(title, year, imdbID, type, poster) VALUES(?, ?, ?, ?, ?)''',
                item_list)
            root.commit()
            root.close()
            return data
        except sqlite3.IntegrityError:
            print("Veritabanında zaten mevcut")
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
            title TEXT ,
            year TEXT,
            imdbID TEXT UNIQUE,
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

def list_shows(name):
    data = get_data(name)
    download_resim(data)
    for idx, i in enumerate(data["result"]):
        lbl = Label(cerceve, font="Century 16", borderwidth=6, relief="solid",
                    text="İsim:" + i["Title"] + "\n" +
                         "Yıl:" + i["Year"] + "\n" +
                         "Tür:" + i["Type"])
        lbl.grid(row=idx, column=0)
        img = get_resim(i['imdbID'])
        lbl2 = Label(cerceve, image=img)
        lbl2.image = img  # keep a reference!
        lbl2.grid(row=idx, column=1)


pencere=Tk()
btn=Button(pencere, text="Ara", command=lambda: list_shows("cars"))
btn.pack(side=TOP)
pencere.title("Film Arama")
cerceve=Frame(pencere)
cerceve.pack(side=LEFT)

#ent=Entry(pencere, width=50)
#ent.pack(side=TOP)
#btn=Button(pencere, text="Ara", variable=data,value=lambda: get_data(ent.get()))
#btn.pack(side=TOP)
#************************

#************************
mainloop()  
pencere.mainloop()







