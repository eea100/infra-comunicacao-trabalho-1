# Trabalho I — Infraestrutura de Comunicação

Transporte confiável de dados na camada de aplicação. CESAR School.

## Checkpoint 1 — Handshake & Sockets

Conexão cliente-servidor via socket TCP com handshake inicial, negociando modo de
operação, tamanho máximo do texto e tamanho da janela.

Python 3, sem dependências externas.

## Como rodar

Dois terminais na pasta do projeto:

```
python3 servidor.py
python3 cliente.py
```

O cliente faz três perguntas; Enter aceita o padrão.

| Pergunta | Opções | Padrão |
|---|---|---|
| Modo de confirmação | GBN / SR | GBN |
| Modo de envio | IND / LOTE | IND |
| Tamanho máximo do texto | 30 a 400 | 30 |

Para rodar em máquinas distintas, alterar `HOST` nos dois arquivos para o IP do
servidor. Porta padrão: 5000.

## Arquivos

- `servidor.py` — escuta, valida o handshake e decide os parâmetros
- `cliente.py` — coleta as opções, propõe o handshake e exibe divergências
- `RELATORIO_CP1.md` — relatório da entrega

## Próximos checkpoints

- **CP2 (21/10)** — CRC-16, fragmentação em payloads de 4 caracteres, ACK/NAK, temporizador e janela
- **CP3 (23/11)** — simulador de erros e perdas, Go-Back-N, Repetição Seletiva e criptografia
