import requests
import json
import datetime
import os

# --- AYARLAR ---
# Token'ı GitHub'ın kasasından alıyoruz
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = "1898111660" # Senin ID

def telegram_yolla(mesaj):
    try:
        url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        parametreler = {"chat_id": CHAT_ID, "text": mesaj}
        requests.post(url_send, json=parametreler)
        print("✅ Telegram mesajı gönderildi!")
    except Exception as e:
        print(f"❌ Telegram hatası: {e}")

def kontrol_et():
    ARANACAK_KELIME = "PINARBAŞI"
    
    # Tarih: YARIN (+1)
    bugun = datetime.date.today()
    yarin = bugun + datetime.timedelta(days=1)
    tarih_str = yarin.strftime("%Y-%m-%d")
    tarih_norm = yarin.strftime("%d.%m.%Y")
    
    print(f"⏳ Yarın ({tarih_norm}) kontrol ediliyor...")
    
    url = "https://api.dedas.com.tr/api/interruptions/getplannedqutages?api-version=2"
    
    payload = {
        "request": {
            "cityId": 6, "districtId": 58, 
            "interruptStartDate": tarih_str,
            "interruptStartDateEnd": None, "installationId": None
        }
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json",
        "Referer": "https://www.dedas.com.tr/",
        "Origin": "https://www.dedas.com.tr"
    }

    try:
        r = requests.post(url, json=payload, headers=headers)
        
        if r.status_code == 200:
            veri = json.dumps(r.json(), ensure_ascii=False).upper()
            
            if ARANACAK_KELIME in veri:
                print("🚨 KESİNTİ BULUNDU!")
                telegram_yolla(f"🚨 DİKKAT!\n\nYarın ({tarih_norm}) Pınarbaşı'nda elektrik kesintisi görünüyor.")
            else:
                print(f"✅ Temiz. Yarın ({tarih_norm}) kesinti yok.")
        else:
            print(f"❌ Site Hatası: {r.status_code}")
            
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    kontrol_et()
