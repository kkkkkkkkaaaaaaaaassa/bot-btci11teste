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

Thread(target=run_flask).start()
# =================================================

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def pegar_preco():
    try:
        url = "https://brapi.dev/api/quote/BTCI11"
        r = requests.get(url, timeout=10).json()
        if "results" in r and r["results"]:
            return r["results"][0]["regularMarketPrice"]
    except:
        pass
    return None

def dentro_do_pregao():
    agora = datetime.now()
    if agora.weekday() >= 5:  # sábado ou domingo
        r
