import requests
import http.client
import json
import sqlite3
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
#bu ödevi nesneye yönelik oluşturmak isterdim ama başa çıkamadım
#onun yerine fonksiyonel ve birbirleri içinde fonksiyonlar çağıran karmaşık projeye döndü
#bu projedede error handling haricinde ai dan yardım alınmamıştır. bütün özellikler elle ve lab örneklerinden alıntılar alınıp yapılmıştır
def get_anahtar():
    dosya=open('anahtar.txt',encoding='UTF-8', mode='r')
    anahtar=dosya.read()
    dosya.close()
    return str(anahtar)
#bu fonksiyonun kendim ayrıntılı bir şekilde oluşturdum
#bazen girdiğim filim isimleri hata veriyor ve bilgilerini db ye kaydetmiyordu
# aşağıda ****** ve ------- lar arasına aldığım kısımlar ai'ın eklediği ile hata ayıklama ve çözüm bulma kısımlarıdır.

def download_resim(data):
    if not data.get('success'): 
        print("çağrı başarısız. İndirme atlandı.")
        return 0
#*********    
    if 'result' not in data or not isinstance(data['result'], list):
        print("No 'result' list in data, skipping image download.")
        return 0
#---------
    for i in data['result']:
#*********
        # Ensure 'i' is a dictionary and has 'imdbID' and 'Poster'
        if not isinstance(i, dict):
            print(f"Skipping item, not a dictionary: {i}")
            continue
#-------------    
        imdb_id = i.get('imdbID')
        poster_url = i.get('Poster')

        if not imdb_id:
            print(f"Skipping item due to missing imdbID: {i}")
            continue

        if not poster_url or poster_url == "N/A":
            print(f"Skipping image download for {imdb_id} due to missing or N/A poster URL: {poster_url}")
            continue

        #show bilgileri veritabanında kayıtlı ise resmi tekrar indirmeye gerek yok
        curs=conn.cursor() 
        curs.execute('''SELECT imdbID FROM show WHERE imdbID=?''', (imdb_id,))
        row=curs.fetchone()
        
        #row none dönmezse db de kayıtlıdır ve resim indirilmesine gerek yok 
        if row!=None:
            print(f"Show {imdb_id} already in database, assuming poster is handled.")
            continue            
        #row none değilde dict olarak dönerse db de kayıtlı değildir. bağlantı kurulur ve resimler api ile çekilir
        print(f"Attempting to download poster for {imdb_id} from {poster_url}")
        
        #hata kontrol için ai in eklediği kısım. resme ulaşmak için bekliyor 
        #ulaşamazsa resmin kaydedilemediğini bildiriyor. bu şekilde kod execute edilmeye devam ediyor
        #bu da download_resim fonksiyonunun get_data içinde çağırıldığında resim indirilemesede kodun devam etmesini sağlıyor
        try:
            response = requests.get(poster_url, timeout=10) # Added timeout
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
            if response.status_code == 200:
                # Ensure resim directory exists
                # import os
                # if not os.path.exists('./resim'):
                #     os.makedirs('./resim')
                
                #ai in eklediği hata kontrol
                file_path = f'./resim/{imdb_id}.jpg'
                try:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Successfully downloaded and saved {file_path}")
                except IOError as e:
                    print(f"Resim kaydedilemedi ({file_path}): {e}")
            # No explicit return 0 here, let the loop continue
        except requests.exceptions.MissingSchema:
            print(f"Invalid URL for poster ({imdb_id}): {poster_url}. Skipping.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading poster for {imdb_id} ({poster_url}): {e}. Skipping.")
        # Removed the general "except:" that could hide errors.
        # The "return 0" on failure was causing the whole download process to stop.
        # Now it just skips the problematic image.
#canvasa scrollbar ekle
def kaydirma_cubugu(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def get_resim(imdbID):
    try:
        dizin = './resim/' + imdbID + '.jpg'
        im = Image.open(dizin)
        
        img = ImageTk.PhotoImage(im.resize((150,222)))
        print(f"PhotoImage başarıyla oluşturuldu: {imdbID}.jpg")
        return img
    except FileNotFoundError:
        print(f"Resim dosyası bulunamadı: {dizin}")
        dizin = './resim/image.png'
        im = Image.open(dizin)
        
        img = ImageTk.PhotoImage(im.resize((150,222)))
       
        return img
    
def get_data(film_adi):
    print(f"Original film_adi: {film_adi}")
    #türkçe karakterleri filtreliyoruz
    Tr2En = str.maketrans("ÇĞİÖŞÜçğıöşüâ", "CGIOSUcgiosua")
    film_adi_tr = film_adi.translate(Tr2En)
    print(f"After Tr2En translation: {film_adi_tr}")
    #boşlukları url olarak okunabilsin diye %20 ile değiştirilir
    film_adi_url = film_adi_tr.replace(" ","%20")
    print(f"URL encoded film_adi: {film_adi_url}")

    conn = http.client.HTTPSConnection("api.collectapi.com")
    headers = {
        'content-type': "application/json",
        'authorization': "apikey "+get_anahtar()
        }
    try:
        print(f"Requesting API with: /imdb/imdbSearchByName?query={film_adi_url}")
        conn.request("GET", "/imdb/imdbSearchByName?query="+film_adi_url, headers=headers)
        res = conn.getresponse()
        print(f"API Response Status: {res.status} {res.reason}")
        raw_data = res.read()
        print(f"Raw API Response Data: {raw_data.decode(errors='ignore')}")
        data = json.loads(raw_data)
        print(f"Parsed JSON data: {data}")

        if not data.get('success'):
            print(f"API call was not successful. Message: {data.get('message', 'No message provided.')}")
            messagebox.showinfo("Hata","Arama \""+ film_adi+ "\" başarısız.\n Tekrar değer giriniz.")    
            return data 

        download_resim(data) 

        #burda benzer bir kodum vardı ama ai biraz değiştirmiş benim kodum dict['success'] içindeki bool çağrı başarılımı değilmi kontrol ediyordu
        #ai gelen verinin dict olup olmadığını kontrol eden bir kısım eklemiş
        if 'result' not in data or not isinstance(data['result'], list):
            print(f"API response does not contain a 'result' list or it's not a list. Data: {data}")
            return data 
        
        root=get_baglanti()
        cursor=root.cursor()
        item_list=[]
        print(f"Processing data['result']: {data['result']}")
        for i in data['result']:
            #burda if kontrolü ai eklemiş
            if not isinstance(i, dict):
                print(f"Skipping item, not a dictionary: {i}")
                continue
            #values ? dict değer kabul etmiyor o yüzden dicti tuple ve liste kullanarak itemize ettim
            item_tuple = (
                i.get('Title'),
                i.get('Year'),
                i.get('imdbID'),
                i.get('Type'),
                i.get('Poster'))
            print(f"Prepared item_tuple: {item_tuple}")
            item_list.append(item_tuple)
        
        if not item_list:
            print("No items prepared for database insertion.")
            # root.close() # Close connection if we are not inserting
            return data

        try:
            print(f"Attempting to insert item_list into database: {item_list}")
            cursor.executemany(
                '''INSERT INTO show(title, year, imdbID, type, poster) VALUES(?, ?, ?, ?, ?)''',
                item_list)
            root.commit()
            print("Data successfully inserted/committed to database.")
        except sqlite3.IntegrityError:
            print("Veritabanında zaten mevcut (IntegrityError). Data not inserted again.")
        finally: # Ensure connection is closed
            root.close()
            print("Database connection closed.")
        return data
    except json.JSONDecodeError as je:
        print(f"JSON Decode Error: {je}")
        print(f"Problematic raw data was: {raw_data.decode(errors='ignore')}") # Show the data that failed to parse
        # Potentially return None or a specific error structure
        return None # Or an error dict: {'success': False, 'error': 'JSONDecodeError', 'message': str(je)}
    except Exception as e:
        print(f"Hata (get_data): {e}")
        print(f"Error type: {type(e)}")
        
        try:
            print(f"Raw data at point of generic error (if available): {raw_data.decode(errors='ignore')}")
        except NameError:
            print("Raw data not available at point of generic error.")
        exit(1) # Original behavior
    
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

    #tekrar arama yapınca eski yazılar kalıyordu. bu eski öğeleri siliyor.
    for widget in cerceve.winfo_children():
        widget.destroy()

    data = get_data(name)
    download_resim(data)
    for idx, i in enumerate(data["result"]):
        lbl = Label(cerceve, font="Century 16", borderwidth=6, relief="solid",justify=LEFT,
                    text="İsim:" + i["Title"] + "\n" +
                         "Yıl:" + i["Year"] + "\n" +
                         "Tür:" + i["Type"])
        lbl.grid(row=idx, column=0)
        img = get_resim(i['imdbID'])
        lbl2 = Label(cerceve, image=img)
        lbl2.image = img  #referans alınmazsa garbage collector siler
        lbl2.grid(row=idx, column=1)


pencere=Tk()
pencere.geometry("1200x600")
yazi=Label(pencere, text="Film Arama")
yazi.pack(side=TOP)
ent = Entry(pencere, width=50)
ent.pack(side=TOP)
ent.bind("<Return>", lambda event: list_shows(ent.get()))
btn=Button(pencere, text="Ara", command=lambda: list_shows(ent.get()))
btn.pack(side=TOP)
pencere.title("Film Arama")

#scrollbar eklemek için canvas oluştur
canvas = Canvas(pencere)
scrollbar = Scrollbar(pencere, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

cerceve=Frame(canvas)
canvas.create_window((0, 0), window=cerceve, anchor='nw')


cerceve.bind("<Configure>", kaydirma_cubugu)


#ent=Entry(pencere, width=50)
#ent.pack(side=TOP)
#btn=Button(pencere, text="Ara", variable=data,value=lambda: get_data(ent.get()))
#btn.pack(side=TOP)

mainloop()  
pencere.mainloop()







