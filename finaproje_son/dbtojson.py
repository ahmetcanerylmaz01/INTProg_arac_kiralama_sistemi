import json
from app import app, db, User, Arac, Rezervasyon
from datetime import date, datetime

def json_converter(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    return str(o)

def main():
    with app.app_context():
        # Kullanıcılar
        users = User.query.all()
        users_list = [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'telefon': u.telefon,
            'ehliyet_no': u.ehliyet_no,
            'is_admin': u.is_admin
        } for u in users]

        # Araçlar
        araclar = Arac.query.all()
        araclar_list = [{
            'id': a.id,
            'marka': a.marka,
            'model': a.model,
            'yil': a.yil,
            'fiyat': a.fiyat,
            'uygun': a.uygun
        } for a in araclar]

        # Rezervasyonlar
        rezervasyonlar = Rezervasyon.query.all()
        rezervasyonlar_list = [{
            'id': r.id,
            'ad_soyad': r.ad_soyad,
            'email': r.email,
            'telefon': r.telefon,
            'baslangic': r.baslangic,
            'bitis': r.bitis,
            'teslim_yeri': r.teslim_yeri,
            'arac_id': r.arac_id,
            'kullanici_id': r.kullanici_id,
            'created_at': r.created_at
        } for r in rezervasyonlar]

        all_data = {
            'users': users_list,
            'araclar': araclar_list,
            'rezervasyonlar': rezervasyonlar_list
        }

        with open('database_dump.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4, default=json_converter)

        print("Veriler 'database_dump.json' dosyasına başarıyla aktarıldı.")

if __name__ == '__main__':
    main()
