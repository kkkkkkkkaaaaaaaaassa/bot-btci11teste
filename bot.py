import os
import requests
import time
from flask import Flask
from threading import Thread
from datetime import datetime

# ================= CONFIGURAÇÕES =================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PRECO_MIN = 9.50
PRECO_MAX = 11.00
VARIACAO_ALERTA = 3.0       # %
INTERVALO = 300             # segundos (5 min)

HORA_INICIO = 9
HORA_FIM = 18
# =================================================

# ================= VARIÁVEIS =====================
preco_abertura = None
alerta_preco = None
alerta_variacao = False
relatorio_enviado = False
data_atual = datetime.now().date()
# =================================================

# ================= FLASK (UPTIME) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot BTCI11 ativo"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run_flask, daemon=True).start()
# =================================================

def enviar(msg):
    if not TOKEN or not CHAT_ID:
        print("❌ ERRO: BOT_TOKEN ou CHAT_ID não carregado")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

    print("📨 Telegram:", r.status_code, r.text)

def pegar_preco():
    try:
        url = "https://brapi.dev/api/quote/BTCI11"
        r = requests.get(url, timeout=10).json()
        if "results" in r and r["results"]:
            return r["results"][0]["regularMarketPrice"]
    except Exception as e:
        print("❌ Erro ao buscar preço:", e)
    return None

def dentro_do_pregao():
    agora = datetime.now()
    if agora.weekday() >= 5:
        return False
    return HORA_INICIO <= agora.hour < HORA_FIM

# ================= INÍCIO =================
print("🚀 Bot iniciando...")
enviar("☁️ Bot BTCI11 iniciado na nuvem (100% ativo).")

while True:
    try:
        agora = datetime.now()

        # RESET DIÁRIO
        if agora.date() != data_atual:
            print("🔄 Reset diário")
            preco_abertura = None
            alerta_preco = None
            alerta_variacao = False
            relatorio_enviado = False
            data_atual = agora.date()

        if not dentro_do_pregao():
            print("⏸ Fora do pregão")
            time.sleep(INTERVALO)
            continue

        preco = pegar_preco()
        if preco is None:
            print("⚠️ Preço indisponível")
            time.sleep(INTERVALO)
            continue

        print(f"💰 Preço atual BTCI11: R$ {preco}")

        if preco_abertura is None:
            preco_abertura = preco
            print(f"📊 Preço de abertura definido: R$ {preco_abertura}")

        # ALERTA DE PREÇO
        if preco <= PRECO_MIN and alerta_preco != "baixo":
            enviar(f"🚨 BTCI11 caiu para R$ {preco}")
            alerta_preco = "baixo"

        elif preco >= PRECO_MAX and alerta_preco != "alto":
            enviar(f"📈 BTCI11 subiu para R$ {preco}")
            alerta_preco = "alto"

        # ALERTA DE VARIAÇÃO
        variacao = ((preco - preco_abertura) / preco_abertura) * 100
        if abs(variacao) >= VARIACAO_ALERTA and not alerta_variacao:
            enviar(f"⚠️ BTCI11 variou {variacao:.2f}% hoje")
            alerta_variacao = True

        # RELATÓRIO DE FECHAMENTO
        if agora.hour == 17 and agora.minute >= 55 and not relatorio_enviado:
            enviar(
                f"📅 Fechamento BTCI11\n"
                f"Abertura: R$ {preco_abertura}\n"
                f"Atual: R$ {preco}\n"
                f"Variação: {variacao:.2f}%"
            )
            relatorio_enviado = True

        time.sleep(INTERVALO)

    except Exception as e:
        print("🔥 ERRO NO LOOP:", e)
        time.sleep(INTERVALO)
