import socket

HOST, PORTA = "127.0.0.1", 5000
TEXTO_MINIMO = 30


def monta(tipo, seq, payload):
    return "%s|%02d|%d|0000|%s" % (tipo, seq, len(payload), payload)


def desmonta(linha):
    tipo, seq, tam, crc, payload = linha.split("|", 4)
    return tipo, int(seq), int(tam), crc, payload


def mostra(titulo, pacote):
    print("\n[%s] TIPO: %s | SEQ: %d | TAM: %d | CRC: %s | PAYLOAD: %s"
          % ((titulo,) + pacote))


def pergunta(texto, opcoes, padrao):
    while True:
        resposta = input("%s %s (padrao %s): " % (texto, opcoes, padrao)).strip().upper()
        if resposta == "":
            return padrao
        if resposta in opcoes:
            return resposta


def pergunta_tamanho():
    while True:
        resposta = input("Tamanho do texto (minimo %d): " % TEXTO_MINIMO).strip()
        if resposta == "":
            return TEXTO_MINIMO
        if resposta.isdigit() and int(resposta) >= TEXTO_MINIMO:
            return int(resposta)


modo = pergunta("Modo de confirmacao", ("GBN", "SR"), "GBN")
envio = pergunta("Modo de envio", ("IND", "LOTE"), "IND")
tamanho = pergunta_tamanho()

cliente = socket.socket()
try:
    cliente.connect((HOST, PORTA))
except ConnectionRefusedError:
    raise SystemExit("Servidor desligado. Rode servidor.py primeiro.")

canal = cliente.makefile("rw", encoding="utf-8", newline="\n")
pedido = monta("HSK", 0, "%s;%s;%d" % (modo, envio, tamanho))
canal.write(pedido + "\n")
canal.flush()
mostra("ENVIADO", desmonta(pedido))
try:
    resposta = desmonta(canal.readline().strip())
    mostra("RECEBIDO", resposta)
    print("\nConexao estabelecida: " + resposta[4])
except ValueError:
    print("Resposta invalida do servidor.")
cliente.close()
