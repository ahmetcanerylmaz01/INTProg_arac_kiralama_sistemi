from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime
import os
from flask import send_from_directory
from werkzeug.utils import secure_filename



# ---------------------
# CONFIG
# ---------------------
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'Gelistirme_Anahtari')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



# ---------------------
# APP & EXTENSIONS
# ---------------------
app = Flask(__name__)

import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

db = SQLAlchemy(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'


# ---------------------
# MODELS
# ---------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    telefon = db.Column(db.String(20))
    ehliyet_no = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Arac(db.Model):
    __tablename__ = 'araclar'
    id = db.Column(db.Integer, primary_key=True)
    marka = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    vites = db.Column(db.String(20), nullable=False)
    yakit = db.Column(db.String(20), nullable=False)
    renk = db.Column(db.String(20), nullable=False)
    foto = db.Column(db.String(120))
    uygun = db.Column(db.Boolean, default=True)

    


    def __repr__(self):
        return f'<Arac {self.marka} {self.model} - {self.yil}>'


class Rezervasyon(db.Model):
    __tablename__ = 'rezervasyonlar'
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefon = db.Column(db.String(20), nullable=False)
    baslangic = db.Column(db.Date, nullable=False)
    bitis = db.Column(db.Date, nullable=False)
    teslim_yeri = db.Column(db.String(150), nullable=False)
    arac_id = db.Column(db.Integer, db.ForeignKey('araclar.id'), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    arac = db.relationship('Arac')
    kullanici = db.relationship('User')  # İsteğe bağlı: current_user ile bağ kurmak istersen


    def __repr__(self):
        return f'<Rezervasyon {self.ad_soyad} - {self.arac.marka} {self.arac.model}>'


# ---------------------
# YARDIMCI FONKSİYONLAR
# ---------------------
def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bu sayfaya erişim yetkiniz yok!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

car_images=['bmwm4.jpeg','c180.jpg']





# ---------------------
# ROUTE'LAR
# ---------------------

@app.route('/')
def index():
    araclar = Arac.query.filter_by(uygun=True).all()
    return render_template('index.html', araclar=araclar,images=car_images)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/dashboard')
@login_required
def dashboard():
    kullanici = current_user

    mevcut_rezervasyon_sayisi = Rezervasyon.query.filter(
        Rezervasyon.kullanici_id == kullanici.id,
        Rezervasyon.bitis >= datetime.today().date()
    ).count()

    gecmis_rezervasyon_sayisi = Rezervasyon.query.filter(
        Rezervasyon.kullanici_id == kullanici.id,
        Rezervasyon.bitis < datetime.today().date()
    ).count()

    favori_sayisi = 0  # Favori aracı tutuyorsan burayı güncelle

    yaklasan_rezervasyon = Rezervasyon.query.filter(
        Rezervasyon.kullanici_id == kullanici.id,
        Rezervasyon.bitis >= datetime.today().date()
    ).order_by(Rezervasyon.baslangic.asc()).first()

    aktiviteler = []  # Aktiviteler tablon varsa çek, yoksa boş bırak

    araclar = Arac.query.filter_by(uygun=True).all()

    return render_template('dashboard.html',
                           kullanici_ad=kullanici.name,
                           mevcut_rez=mevcut_rezervasyon_sayisi,
                           gecmis_rez=gecmis_rezervasyon_sayisi,
                           favoriler=favori_sayisi,
                           yaklasan=yaklasan_rezervasyon,
                           aktiviteler=aktiviteler,
                           araclar=araclar)




@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
         
        if not (name and email and password):
            flash('Lütfen tüm alanları doldurun.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalı.', 'danger')
            return render_template('register.html')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Bu e-posta zaten kayıtlı.', 'danger')
            return render_template('register.html')

        yeni_user = User(name=name, email=email)
        yeni_user.set_password(password)
        db.session.add(yeni_user)
        db.session.commit()
        login_user(yeni_user)
        flash('Kayıt başarılı, hoşgeldiniz!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not (email and password):
            flash('Lütfen e-posta ve şifre girin.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Giriş başarılı!', 'success')
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin_panel'))
            else:
                return redirect(next_page or url_for('dashboard'))
        else:
            flash('E-posta veya şifre hatalı!', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yapıldı.', 'success')
    return redirect(url_for('index'))



@app.route('/rezervasyon/<int:rezervasyon_id>')
@login_required
def rezervasyon_detay(rezervasyon_id):
    rezervasyon = Rezervasyon.query.get_or_404(rezervasyon_id)
    
    # Burada, kullanıcının sadece kendi rezervasyonlarını görmesini isteyebilirsiniz
    if rezervasyon.kullanici_id != current_user.id and not current_user.is_admin:
        flash('Bu rezervasyona erişim yetkiniz yok.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('rezervasyon_detay.html', rezervasyon=rezervasyon)

@app.route('/rezervasyon-iptal/<int:rezervasyon_id>', methods=['POST'])
@login_required
def rezervasyon_iptal(rezervasyon_id):
    rezervasyon = Rezervasyon.query.get_or_404(rezervasyon_id)
    
    if rezervasyon.kullanici_id != current_user.id and not current_user.is_admin:
        flash('Bu rezervasyonu iptal etme yetkiniz yok.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(rezervasyon)
    db.session.commit()
    flash('Rezervasyonunuz iptal edildi.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/export/json')
def export_json():
    users = User.query.all()
    data = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'araclar': []
        }

        user_araclar = Arac.query.filter_by(user_id=user.id).all()
        for arac in user_araclar:
            arac_data = {
                'id': arac.id,
                'marka': arac.marka,
                'model': arac.model,
                'fiyat': arac.fiyat,
                'durum': arac.durum
            }
            user_data['araclar'].append(arac_data)

        data.append(user_data)

    return jsonify(data)




# PROFİL SAYFASI (GET ile profil bilgilerini gösterir)
@app.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad', '').strip()
        email = request.form.get('email', '').strip()
        telefon = request.form.get('telefon', '').strip()
        ehliyet_no = request.form.get('ehliyet_no', '').strip()

        if not (ad_soyad and email):
            flash('Ad Soyad ve E-posta zorunludur.', 'danger')
            return redirect(url_for('profil'))

        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Bu e-posta başka bir kullanıcıya ait.', 'danger')
                return redirect(url_for('profil'))

        user = User.query.get(current_user.id)
        user.ad_soyad = ad_soyad
        user.email = email
        user.telefon = telefon
        user.ehliyet_no = ehliyet_no

        db.session.commit()
        flash('Profiliniz başarıyla güncellendi.', 'success')
        return redirect(url_for('profil'))

    # GET isteğinde en güncel kullanıcı bilgilerini veritabanından çekiyoruz
    user = User.query.get(current_user.id)
    return render_template('profil.html', user=user)



# ADMIN PANELİ

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_panel():
    if request.method == 'POST':
        marka = request.form['marka']
        model = request.form['model']
        yil = request.form['yil']
        fiyat = request.form['fiyat']
        vites = request.form['vites']
        yakit = request.form['yakit']
        renk = request.form['renk']

        foto = request.files.get('foto')
        foto_adi = None
        if foto and foto.filename != '':
            foto_adi = secure_filename(foto.filename)
            upload_klasoru = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_klasoru, exist_ok=True)
            foto.save(os.path.join(upload_klasoru, foto_adi))

        yeni_arac = Arac(
            marka=marka,
            model=model,
            yil=int(yil),
            fiyat=float(fiyat),
            vites=vites,
            yakit=yakit,
            renk=renk,
            foto=foto_adi,
            uygun=True
        )
        db.session.add(yeni_arac)
        db.session.commit()
        flash("Araç başarıyla eklendi", "success")
        return redirect(url_for('admin_panel'))

    araclar = Arac.query.all()
    return render_template("admin.html", araclar=araclar)



@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        # Zaten giriş yapılmışsa admin paneline ya da dashboard'a yönlendir
        if current_user.is_admin:
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not (email and password):
            flash('Lütfen e-posta ve şifre girin.', 'danger')
            return render_template('admin-login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Admin girişi başarılı!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_panel'))
        else:
            flash('E-posta veya şifre hatalı ya da admin değilsiniz!', 'danger')

    return render_template('admin-login.html')



from werkzeug.utils import secure_filename
import os

@app.route('/admin/arac-ekle', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_arac_ekle():
    if request.method == 'POST':
        marka = request.form.get('marka', '').strip()
        model = request.form.get('model', '').strip()
        yil = request.form.get('yil', '').strip()
        fiyat = request.form.get('fiyat', '').strip()
        vites = request.form.get('vites', '').strip()
        yakit = request.form.get('yakit', '').strip()
        renk = request.form.get('renk', '').strip()
        uygun = True

        # Zorunlu alan kontrolü
        if not all([marka, model, yil, fiyat, vites, yakit, renk]):
            flash('Lütfen tüm alanları eksiksiz doldurun.', 'danger')
            return render_template('admin_arac_ekle.html')

        if vites == 'Seçiniz' or yakit == 'Seçiniz':
            flash('Lütfen vites ve yakıt türünü seçiniz.', 'danger')
            return render_template('admin_arac_ekle.html')

        # Yıl ve fiyatın sayısal olması kontrolü
        try:
            yil = int(yil)
            fiyat = float(fiyat)
        except ValueError:
            flash('Yıl ve fiyat sayısal olmalı.', 'danger')
            return render_template('admin_arac_ekle.html')

        foto = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                foto = filename

        yeni_arac = Arac(
            marka=marka,
            model=model,
            yil=yil,
            fiyat=fiyat,
            vites=vites,
            yakit=yakit,
            renk=renk,
            foto=foto,
            uygun=uygun
        )

        try:
            db.session.add(yeni_arac)
            db.session.commit()
            flash('Araç başarıyla eklendi.', 'success')
            return redirect(url_for('admin_panel'))
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
            return render_template('admin_arac_ekle.html')

    return render_template('admin_arac_ekle.html')





@app.route('/admin/arac-sil/<int:arac_id>', methods=['POST'])
@login_required
@admin_required
def arac_sil(arac_id):
    arac = Arac.query.get_or_404(arac_id)
    db.session.delete(arac)
    db.session.commit()
    flash('Araç silindi.', 'success')
    return redirect(url_for('admin_panel'))


# KİRALAMA / REZERVASYON

@app.route('/kirala', methods=['GET', 'POST'])
@login_required
def kirala():
    araclar = Arac.query.filter_by(uygun=True).all()

    if request.method == 'POST':
        ad_soyad = request.form.get('ad_soyad', '').strip()
        email = request.form.get('email', '').strip()
        telefon = request.form.get('telefon', '').strip()
        baslangic = request.form.get('baslangic_tarihi', '').strip()
        bitis = request.form.get('bitis_tarihi', '').strip()
        teslim_yeri = request.form.get('teslim_yeri', '').strip()
        arac_id = request.form.get('arac_secimi', '').strip()

        if not (ad_soyad and email and telefon and baslangic and bitis and teslim_yeri and arac_id):
            flash('Lütfen tüm alanları eksiksiz doldurun.', 'danger')
            return render_template('kirala.html', araclar=araclar)

        if not arac_id.isdigit():
            flash('Lütfen geçerli bir araç seçin.', 'danger')
            return render_template('kirala.html', araclar=araclar)

        try:
            baslangic_date = datetime.strptime(baslangic, '%Y-%m-%d').date()
            bitis_date = datetime.strptime(bitis, '%Y-%m-%d').date()
        except ValueError:
            flash('Tarih formatı hatalı.', 'danger')
            return render_template('kirala.html', araclar=araclar)

        if baslangic_date > bitis_date:
            flash('Başlangıç tarihi bitiş tarihinden sonra olamaz.', 'danger')
            return render_template('kirala.html', araclar=araclar)

        arac = Arac.query.get(int(arac_id))
        if not arac or not arac.uygun:
            flash('Seçilen araç uygun değil.', 'danger')
            return render_template('kirala.html', araclar=araclar)

        rezervasyon = Rezervasyon(
            ad_soyad=ad_soyad,
            email=email,
            telefon=telefon,
            baslangic=baslangic_date,
            bitis=bitis_date,
            teslim_yeri=teslim_yeri,
            arac_id=arac.id,
            kullanici_id=current_user.id  # Eğer Rezervasyon modeli kullanıcıyla bağlıysa ekle
        )

        db.session.add(rezervasyon)
        db.session.commit()
        flash('Rezervasyonunuz başarıyla oluşturuldu!', 'success')
        return redirect(url_for('dashboard'))

    # GET ise formu göster
    return render_template('kirala.html', araclar=araclar)

@app.route('/arac-detay/<int:arac_id>')
def arac_detay(arac_id):
    # Veritabanı veya liste varsa ona göre aracı bul
    arac = Arac.query.get(arac_id)  # SQLAlchemy kullanıyorsan
    # Veya şöyle bir liste içinden çekiyorsan:
    # arac = next((a for a in araclar if a.id == arac_id), None)

    if not arac:
        return "Araç bulunamadı", 404

    return render_template('arac-detay.html', arac=arac)


@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        if not name or not email or not password:
            flash('Tüm alanları doldurun.', 'warning')
            return redirect(url_for('create_admin'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            existing_user.is_admin = True
            db.session.commit()
            login_user(existing_user)
            flash(f"{email} artık admin ve giriş yapıldı!", 'success')
            return redirect(url_for('admin_panel'))
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_admin = User(name=name, email=email, password=hashed_password, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
            login_user(new_admin)
            flash('Yeni admin oluşturuldu ve giriş yapıldı!', 'success')
            return redirect(url_for('admin_panel'))

    return '''
    <h2>Admin Oluştur</h2>
    <form method="post">
        <input type="text" name="name" placeholder="Ad Soyad"><br>
        <input type="email" name="email" placeholder="Email"><br>
        <input type="password" name="password" placeholder="Şifre"><br>
        <button type="submit">Admin Yap</button>
    </form>
    '''


@app.route('/gecmis')
@login_required
def gecmis():
    # Kullanıcının geçmiş rezervasyonlarını alıyoruz: bitiş tarihi bugünden önce olanlar
    rezervasyonlar = Rezervasyon.query.filter(
        Rezervasyon.email == current_user.email,
        Rezervasyon.bitis < datetime.today().date()
    ).order_by(Rezervasyon.bitis.desc()).all()

    # Her rezervasyon için 'sure' alanını hesaplayalım (gün cinsinden)
    gecmis_listesi = []
    for r in rezervasyonlar:
        sure = (r.bitis - r.baslangic).days
        arac_adi = f"{r.arac.marka} {r.arac.model}" if r.arac else "Bilinmiyor"
        gecmis_listesi.append({
            'arac': arac_adi,
            'baslangic': r.baslangic,
            'bitis': r.bitis,
            'sure': sure,
            'teslim_yeri': r.teslim_yeri
        })

    return render_template('gecmis.html', gecmis=gecmis_listesi)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

