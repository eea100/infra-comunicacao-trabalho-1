import socket

HOST, PORTA = "127.0.0.1", 5000
JANELA, TEXTO_MINIMO, TEXTO_MAXIMO = 5, 30, 400


def monta(tipo, seq, payload):
    return "%s|%02d|%d|0000|%s" % (tipo, seq, len(payload), payload)


def desmonta(linha):
    tipo, seq, tam, crc, payload = linha.split("|", 4)
    return tipo, int(seq), int(tam), crc, payload


def mostra(titulo, pacote):
    print("\n[%s] TIPO: %s | SEQ: %d | TAM: %d | CRC: %s | PAYLOAD: %s"
          % ((titulo,) + pacote))


def negocia(payload):
    modo, envio, tamanho = payload.split(";")
    modo = modo if modo in ("GBN", "SR") else "GBN"
    envio = envio if envio in ("IND", "LOTE") else "IND"
    return modo, envio, min(max(int(tamanho), TEXTO_MINIMO), TEXTO_MAXIMO)


servidor = socket.socket()
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORTA))
servidor.listen(1)
print("Servidor no ar em %s:%d" % (HOST, PORTA))

while True:
    conexao, endereco = servidor.accept()
    print("\nCliente conectado: %s:%d" % endereco)
    canal = conexao.makefile("rw", encoding="utf-8", newline="\n")
    try:
        pedido = desmonta(canal.readline().strip())
        mostra("RECEBIDO", pedido)
        if pedido[0] != "HSK":
            raise ValueError("esperado HSK, recebido %s" % pedido[0])
        if pedido[2] != len(pedido[4]):
            raise ValueError("TAM %d nao corresponde ao payload" % pedido[2])
        modo, envio, tamanho = negocia(pedido[4])
        resposta = monta("HSK", 0, "OK;%s;%s;%d;%d" % (modo, envio, tamanho, JANELA))
        canal.write(resposta + "\n")
        canal.flush()
        mostra("ENVIADO", desmonta(resposta))
        print("\nConexao estabelecida: modo=%s envio=%s texto=%d janela=%d"
              % (modo, envio, tamanho, JANELA))
    except ValueError as erro:
        print("Pacote invalido (%s), conexao descartada." % erro)
    canal.close()
    conexao.close()
