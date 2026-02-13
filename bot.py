import requests
import time
from datetime import datetime

TOKEN = "8298593371:AAG5n-XzJeg7ZHMdi5MMpDD1W7268AC2lWk"
CHAT_ID = "6546551357"

PRECO_MIN = 9.50
PRECO_MAX = 11.00
VARIACAO_ALERTA = 3.0
INTERVALO = 300

HORA_INICIO = 9
HORA_FIM = 18

preco_abertura = None
alerta_preco = None
alerta_variacao = False
relatorio_enviado = False

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def pegar_preco():
    url = "https://brapi.dev/api/quote/BTCI11"
    r = requests.get(url, timeout=10).json()
    if "results" in r and r["results"]:
        return r["results"][0]["regularMarketPrice"]
    return None

def dentro_do_pregao():
    agora = datetime.now()
    if agora.weekday() >= 5:
        return False
    return HORA_INICIO <= agora.hour < HORA_FIM

enviar("☁️ Bot BTCI11 iniciado na nuvem (100% ativo).")

while True:
    try:
        if not dentro_do_pregao():
            time.sleep(INTERVALO)
            continue

        preco = pegar_preco()
        if preco is None:
            time.sleep(INTERVALO)
            continue

        agora = datetime.now()

        if preco_abertura is None:
            preco_abertura = preco

        if preco <= PRECO_MIN and alerta_preco != "baixo":
            enviar(f"🚨 BTCI11 caiu para R$ {preco}")
            alerta_preco = "baixo"

        elif preco >= PRECO_MAX and alerta_preco != "alto":
            enviar(f"📈 BTCI11 subiu para R$ {preco}")
            alerta_preco = "alto"

        variacao = ((preco - preco_abertura) / preco_abertura) * 100

        if abs(variacao) >= VARIACAO_ALERTA and not alerta_variacao:
            enviar(f"⚠️ BTCI11 variou {variacao:.2f}% hoje")
            alerta_variacao = True

        if agora.hour == 17 and agora.minute >= 55 and not relatorio_enviado:
            enviar(
                f"📅 Fechamento BTCI11\n"
                f"Abertura: R$ {preco_abertura}\n"
                f"Atual: R$ {preco}\n"
                f"Variação: {variacao:.2f}%"
            )
            relatorio_enviado = True

        time.sleep(INTERVALO)

    except:
        time.sleep(INTERVALO)
