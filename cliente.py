import socket

HOST, PORTA = "127.0.0.1", 5000
TEXTO_MINIMO, TEXTO_MAXIMO = 30, 400


def monta(tipo, seq, payload):
    return "%s|%02d|%d|0000|%s" % (tipo, seq, len(payload), payload)


def desmonta(linha):
    tipo, seq, tam, crc, payload = linha.split("|", 4)
    return tipo, int(seq), int(tam), crc, payload


def mostra(titulo, pacote):
    print("\n[%s] TIPO: %s | SEQ: %d | TAM: %d | CRC: %s | PAYLOAD: %s"
          % ((titulo,) + pacote))


def le(texto):
    try:
        return input(texto).strip()
    except EOFError:
        raise SystemExit("\nEntrada encerrada.")


def pergunta(texto, opcoes, padrao):
    while True:
        resposta = le("%s %s (padrao %s): " % (texto, opcoes, padrao)).upper()
        if resposta == "":
            return padrao
        if resposta in opcoes:
            return resposta
        print("Opcao invalida.")


def pergunta_tamanho():
    while True:
        resposta = le("Tamanho do texto (%d a %d): " % (TEXTO_MINIMO, TEXTO_MAXIMO))
        if resposta == "":
            return TEXTO_MINIMO
        if resposta.isdigit() and TEXTO_MINIMO <= int(resposta) <= TEXTO_MAXIMO:
            return int(resposta)
        print("Valor invalido.")


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
    if resposta[0] != "HSK":
        raise ValueError("esperado HSK, recebido %s" % resposta[0])
    if resposta[2] != len(resposta[4]):
        raise ValueError("TAM %d nao corresponde ao payload" % resposta[2])
    status, modo_ok, envio_ok, tamanho_ok, janela = resposta[4].split(";")
    print("\nConexao estabelecida: modo=%s envio=%s texto=%s janela=%s"
          % (modo_ok, envio_ok, tamanho_ok, janela))
    for nome, meu, dele in (("modo", modo, modo_ok), ("envio", envio, envio_ok),
                            ("texto", str(tamanho), tamanho_ok)):
        if meu != dele:
            print("Divergencia em %s: pedi %s, servidor adotou %s" % (nome, meu, dele))
except ValueError as erro:
    print("Resposta invalida do servidor (%s)." % erro)
cliente.close()
