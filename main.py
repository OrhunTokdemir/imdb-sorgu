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
    
    conn.request("GET", "/imdb/imdbSearchByName?query="+film_adi, headers=headers)
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)
    print("data:", data)
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
    # Clear previous results from cerceve
    for widget in cerceve.winfo_children():
        widget.destroy()

    data = get_data(name)
    if not data or not data.get("result"): # Check if data or data["result"] is None or empty
        print("No results found or error in fetching data.")
        # Optionally, display a message in the UI
        lbl = Label(cerceve, text="No results found.")
        lbl.grid(row=0, column=0)
        # Update canvas scrollregion in case cerceve is empty
        cerceve.update_idletasks() # Ensure widgets are processed
        my_canvas.config(scrollregion=my_canvas.bbox("all"))
        return

    download_resim(data)
    for idx, i in enumerate(data["result"]):
        lbl = Label(cerceve, font="Century 16", borderwidth=6, relief="solid",
                    text="İsim:" + i["Title"] + "\n" +
                         "Yıl:" + i["Year"] + "\n" +
                         "Tür:" + i["Type"])
        lbl.grid(row=idx, column=0, sticky="ew", padx=5, pady=5) # Added sticky and padding
        img = get_resim(i['imdbID'])
        if img: # Check if image was loaded successfully
            lbl2 = Label(cerceve, image=img)
            lbl2.image = img  # keep a reference!
            lbl2.grid(row=idx, column=1, padx=5, pady=5) # Added padding

    # Update canvas scrollregion after adding new widgets
    cerceve.update_idletasks() # Ensure widgets are processed before getting bbox
    my_canvas.config(scrollregion=my_canvas.bbox("all"))


pencere=Tk()
yazi=Label(pencere, text="Film Arama")
yazi.pack(side=TOP, pady=5) # Added padding
ent = Entry(pencere, width=50)
ent.pack(side=TOP, pady=5) # Added padding
btn=Button(pencere, text="Ara", command=lambda: list_shows(ent.get()))
btn.pack(side=TOP, pady=5) # Added padding
pencere.title("Film Arama")

# Create a main frame to hold the canvas and scrollbar
main_scroll_frame = Frame(pencere)
main_scroll_frame.pack(fill=BOTH, expand=1, padx=10, pady=10) # Added padding and expand

# Create a canvas
my_canvas = Canvas(main_scroll_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Add a scrollbar to the main frame
scrollbar = Scrollbar(main_scroll_frame, orient=VERTICAL, command=my_canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

# Configure the canvas
my_canvas.configure(yscrollcommand=scrollbar.set)
# Bind canvas resizing to update scrollregion of the inner frame
# It's often better to bind to the inner frame's configure event if its size dictates the scrollregion
# However, for simplicity with grid, updating after list_shows and on canvas configure can work.

def on_canvas_configure(event):
    # Update the scrollregion to encompass the cerceve frame
    # This ensures that if the canvas itself is resized (e.g. window resize),
    # the scrollregion is correctly set based on cerceve's current content.
    # We use cerceve.winfo_reqwidth() to get the required width for cerceve.
    my_canvas.configure(scrollregion=my_canvas.bbox("all"))
    # If you want the canvas to only scroll vertically and cerceve to expand horizontally:
    # my_canvas.itemconfig(cerceve_window, width=event.width)


my_canvas.bind('<Configure>', on_canvas_configure)


# Create ANOTHER frame INSIDE the canvas - this is our cerceve
cerceve = Frame(my_canvas) # cerceve is now a child of my_canvas

# Add that new frame to a window in the canvas
# This window item on the canvas will hold our cerceve frame
cerceve_window = my_canvas.create_window((0,0), window=cerceve, anchor="nw")


#ent=Entry(pencere, width=50)
#ent.pack(side=TOP)
#btn=Button(pencere, text="Ara", variable=data,value=lambda: get_data(ent.get()))
#btn.pack(side=TOP)
#************************

#************************
#mainloop() # Removed one of the mainloop calls
pencere.mainloop()







