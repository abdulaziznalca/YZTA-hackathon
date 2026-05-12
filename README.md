# ShopPilot AI - KOBI ve Kooperatifler Icin Musteri Iletisimi Otomasyonu

ShopPilot AI, KOBI ve kooperatiflerin siparis, kargo, stok ve politika sorularini dogal dilde yonetmek icin gelistirilmis coklu-agent tabanli bir prototiptir.

## Problem
Kucuk ve orta olcekli isletmelerde musteri iletisimi genellikle manuel yurutulur:
- "Siparisim nerede?"
- "Bu urun stokta var mi?"
- "Iade kosullari nedir?"

Bu surec operasyonel zaman kaybi, insan hatasi ve tutarsiz musteri deneyimi olusturur.

## Cozum Ozeti
ShopPilot AI, gelen mesaji anlayip uygun uzman agent'a yonlendirir, veritabanindan ve politika dokumanindan bilgi ceker, tek ve tutarli bir yanit uretir.

- Agent-based mimari (Supervisor + Specialist Agents + Synthesizer)
- Dogal dil anlama/uretme (Gemini)
- Veri ile etkilesim (siparis/kargo/stok)
- RAG benzeri politika arama (embedding + retrieval)

## Sistem Mimarisi

```text
Frontend (Next.js)
  -> /api/chat (FastAPI)
    -> Supervisor Agent (intent routing)
      -> Order Agent -----> order_tools (DB)
      -> Shipment Agent --> shipment_tools (DB)
      -> Stock Agent ----> stock_tools (DB)
      -> Policy Agent ---> rag_tools -> policy.md (RAG)
      -> Complaint Agent (escalation)
      -> Manager Agent --> dashboard_tools (DB)
    -> Synthesizer Agent (tek final cevap)
  <- Chat response
```

### Bilesenler
- `frontend/`: Next.js tabanli chat, dashboard ve analytics arayuzu
- `backend/app/api`: REST endpointleri
- `backend/app/agents`: LangGraph ile agent orkestrasyonu
- `backend/app/tools`: Agentlarin veri/servis araclari
- `backend/app/services`: Gemini, RAG, analytics servisleri
- `backend/app/models`: SQLAlchemy veri modelleri
- `docs/policy.md`: iade/hasar/garanti/kargo politikalari

## Agent Akisi
1. Kullanici mesaji `/api/chat` endpointine gelir.
2. `supervisor` intentleri cikarir (`order_status`, `shipment_status`, `stock_query`, `policy_question`, `complaint`, `manager_summary`).
3. Uygun specialist agent(lar) ilgili tool'u cagirir.
4. Birden fazla sonuc varsa `synthesizer` tek ve akici cevapta birlestirir.
5. Sonuc `ChatLog` tablosuna intent ve cikarilan parametrelerle kaydedilir.

## Yapay Zeka Yaklasimi

### 1) Intent Routing
- Model, mesaji siniflandirir ve JSON formatinda intent + parametre cikarir.
- Ornek parametreler: `order_number`, `product_name`.

### 2) Specialist Agent Yanit Uretimi
- Her agent alan-ozel bir system prompt ile calisir.
- Yanitlar sadece araclardan (tool) gelen veriye dayandirilir.

### 3) RAG Benzeri Politika Cevaplama
- `docs/policy.md` chunk'lanir ve embedding'lenir.
- Politika sorularinda benzer parcalar retrieval ile cekilir.

### 4) Coklu Cevap Sentezi
- Birden fazla agent sonucu tek bir musteri yanitina donusturulur.

## Veri Modeli (Ozet)
- `Product`: urun, stok, fiyat
- `Order`: siparis no, durum, tahmini teslim, tutar
- `Shipment`: kargo firmasi, takip no, konum, durum
- `ChatLog`: kullanici mesaji, AI yaniti, intent, urun/siparis parametreleri

## Kurulum ve Calistirma

## Gereksinimler
- Python 3.11+
- Node.js 18+
- Gemini API key

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# .env icine GEMINI_API_KEY ekleyin
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`  
Backend: `http://localhost:8000`

## Ortam Degiskenleri
`.env` (backend icin):
- `GEMINI_API_KEY`
- `DATABASE_URL` (varsayilan: `sqlite:///./shoppilot.db`)
- `CORS_ORIGINS` (varsayilan: `http://localhost:3000`)

## API Endpointleri (Ozet)
- `POST /api/chat` -> Agent orkestrasyonlu sohbet
- `GET /api/orders` -> Siparis listesi
- `GET /api/orders/by-number/{order_number}` -> Siparis detayi
- `GET /api/shipments/by-order/{order_id}` -> Kargo bilgisi
- `GET /api/stock` -> Stok listesi
- `GET /api/stock/search?q=...` -> Urun arama
- `GET /api/dashboard/summary` -> Yonetici ozet metrikleri
- `GET /api/analytics/summary?hours=24` -> Etkilesim analitigi

## Demo Senaryosu
Asagidaki sorularla kisa demo yapilabilir:

1. `128 numarali siparisim nerede?`
- Beklenen: Siparis/kargo durumu + tahmini teslim

2. `Lavanta sabunu stokta var mi?`
- Beklenen: Stok adedi, durum (kritik/mevcut/tukendi), fiyat

3. `Iade politikaniz nedir?`
- Beklenen: Politika dokumanindan retrieval tabanli yanit

4. `Bugunku yonetici ozeti ver`
- Beklenen: Toplam siparis, geciken, kritik stok ozetleri

5. `Urun hasarli geldi`
- Beklenen: Sikayet karsilama + yoneticiye escalasyon bilgisi

## Hackathon Kriterlerine Hizalama
- Yapay zeka kullanimi: Intent routing + response generation
- Agent mimarisi: Supervisor + specialist yapisi
- Veri ile calisma: Siparis, kargo, stok, chat log
- Aksiyon alabilen sistem: Sikayet escalasyonu ve yonetici akisi
- Otomasyon seviyesi: Uctan uca otomatik mesaj isleme
- Kullanici deneyimi: Basit ve akici chat arayuzu

## Sinirliliklar (MVP)
- WhatsApp/e-posta gibi dis kanal entegrasyonlari sonraki adim
- Gercek operasyonel aksiyonlar (iptal, ticket lifecycle) gelistirilebilir
- Test kapsami ve gozlemlenebilirlik (monitoring) arttirilabilir

## Guvenlik Notu
Gercek API anahtarlari repoya commit edilmemelidir. Yalnizca `.env.example` takip edilmeli, gercek anahtarlar ortam degiskeni olarak yonetilmelidir.
