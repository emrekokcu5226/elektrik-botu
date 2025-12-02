import requests
import json
import datetime
import os
import random
import time

# --- AYARLAR ---
TOKEN = os.environ["TELEGRAM_TOKEN"]
# CHAT ID'ni buraya sabitliyorum (Senin verdiğin ID)
CHAT_ID = "1898111660"

def telegram_yolla(mesaj):
    try:
        url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        parametreler = {"chat_id": CHAT_ID, "text": mesaj}
        requests.post(url_send, json=parametreler, timeout=10)
        print("✅ Telegram mesajı gönderildi!")
    except Exception as e:
        print(f"❌ Telegram hatası: {e}")

# Ücretsiz Proxy Listesi Çeken Fonksiyon
def get_proxies():
    print("🌍 Proxy listesi aranıyor...")
    proxies = []
    try:
        # Hızlı ve güncel bir proxy listesi kaynağından veri çekiyoruz
        r = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps", timeout=10)
        data = r.json()
        for p in data['data']:
            ip = p['ip']
            port = p['port']
            protocol = p['protocols'][0]
            proxy_str = f"{protocol}://{ip}:{port}"
            proxies.append(proxy_str)
    except:
        # Yedek manuel liste (Ne olur ne olmaz)
        proxies = [
            "http://20.111.54.16:80",
            "http://20.111.54.16:8123"
        ]
    print(f"🌍 Toplam {len(proxies)} adet vekil sunucu (Proxy) bulundu.")
    return proxies

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

    # --- PROXY ROULETTE ---
    # Listeden rastgele proxy seçip deneyeceğiz
    proxy_listesi = get_proxies()
    basarili_oldu = False

    # En fazla 10 farklı proxy denesin
    for i in range(10):
        proxy_adresi = random.choice(proxy_listesi)
        proxy_ayari = {"http": proxy_adresi, "https": proxy_adresi}
        
        print(f"Attempt {i+1}: Bağlanılıyor... (Proxy: {proxy_adresi})")
        
        try:
            # Timeout'u kısa tutuyoruz (5 sn) ki hızlıca diğerine geçsin
            r = requests.post(url, json=payload, headers=headers, proxies=proxy_ayari, timeout=10)
            
            if r.status_code == 200:
                print("✅ BAŞARILI! Kapı açıldı.")
                veri = json.dumps(r.json(), ensure_ascii=False).upper()
                
                if ARANACAK_KELIME in veri:
                    print("🚨 KESİNTİ BULUNDU!")
                    telegram_yolla(f"🚨 DİKKAT!\n\nYarın ({tarih_norm}) Pınarbaşı'nda elektrik kesintisi görünüyor.")
                else:
                    print(f"✅ Temiz. Yarın ({tarih_norm}) kesinti yok.")
                
                basarili_oldu = True
                break # Döngüden çık
            else:
                print(f"❌ Site Hata Verdi: {r.status_code}")

        except Exception as e:
            print(f"❌ Bu proxy çalışmadı.")
            # Hata verirse döngü devam eder, bir sonraki proxy'i dener
            time.sleep(1)
    
    if not basarili_oldu:
        print("⚠️ Hiçbir Proxy bağlanamadı. DEDAŞ çok sıkı korunuyor.")
        # Eğer hepsi başarısız olursa bize haber versin
        # telegram_yolla("⚠️ Bot DEDAŞ'a bağlanamadı (IP Engeli).") 

if __name__ == "__main__":
    kontrol_et()
