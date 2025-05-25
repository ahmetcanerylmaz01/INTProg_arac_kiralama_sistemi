# 📌 Proje Başlığı

> Araç Kiralama Takip Sistemi

## 🧾 Proje Tanıtımı  
Bu uygulama, kullanıcıların araç kiralama işlemlerini yapabildiği bir web uygulamasıdır. Flask framework’ü ile geliştirilmiştir.  
Kullanıcılar kayıt olabilir, giriş yapabilir, araçları inceleyebilir, rezervasyon yapabilir ve geçmiş kiralama bilgilerini görüntüleyebilirler.

## 🚀 Proje Özellikleri  
- 🔐 Kullanıcı kayıt ve giriş işlemleri  
- 🚗 Araç listesi görüntüleme ve detay sayfası  
- 📝 Araç kiralama rezervasyonu yapabilme  
- 📅 Kiralama geçmişi görüntüleme  
- ⚙️ Veritabanı ile kalıcı veri saklama  

## 📦 Kurulum ve Çalıştırma

### ✅ Gereksinimler  

Bu projeyi çalıştırmak için bilgisayarınızda aşağıdaki yazılımlar kurulu olmalıdır:

- Python 3.x    

Aşağıdaki Python kütüphaneleri (requirements.txt dosyasından yüklenebilir):  
  - flask  
  - flask_sqlalchemy  
  - Flask-Login
  - Werkzeug

### 🚀 Uygulamayı Başlatma  
Projeyi çalıştırmak için terminalde şu komutu kullanın:

    python app.py

Ardından tarayıcıdan:  
http://127.0.0.1:5000/ adresine gidin.

## 📂 Proje Dosya Yapısı

---
├── app.py               # Ana Python uygulama dosyası
├── database_dump.json   # Veritabanı yedeği dosyası
├── dbtojson.py          # Veritabanını JSON'a çeviren script
├── requirements.txt     # Gerekli Python paketlerini içeren dosya
├── templates/           # HTML şablonlarının bulunduğu klasör
│   ├── admin-login.html # Admin girişi sayfası
│   ├── admin.html       # Admin paneli
│   ├── arac-detay.html  # Araç detay sayfası
│   ├── base.html        # Tüm sayfalar için temel şablon
│   ├── dashboard.html    # Kullanıcı kontrol paneli
│   ├── gecmis.html      # Kullanıcının geçmiş rezervasyonları
│   ├── index.html       # Anasayfa
│   ├── kirala.html      # Araç kiralama formu
│   ├── login.html       # Giriş formu
│   ├── profil.html      # Kullanıcı profili
│   └── register.html    # Kayıt formu
└── static/              # Statik dosyalar (CSS, JS, resimler)
    ├── uploads/         # Yüklenen araç fotoğraflarının bulunduğu klasör
    │   ├── bmwm4.jpeg   # Araç fotoğrafı
    │   ├── c180.jpg     # Araç fotoğrafı
    │   └── passat.jpg   # Araç fotoğrafı

---
