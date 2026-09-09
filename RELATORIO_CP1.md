# Relatório — Checkpoint 1: Handshake & Sockets

**Disciplina:** Infraestrutura de Comunicação — CESAR School
**Trabalho I:** Transporte confiável de dados na camada de aplicação
**Grupo:**
- Eduardo Esteves de Albuquerque
- Gabriel Gueiros Tabosa
- Gustavo Rogério Soares Filho
- Julio Cesar Coutinho Holanda Cavalcanti
- Caio Augusto Machado de Melo
- João Luiz de Lima Bacelar
- Maria Clara Albuquerque Targino
- Guilherme Melo Caldas de Lira

**Monitores:** Pedro e Henrique
**Data:** 09/09/2026

---

## 1. Escopo desta entrega

Estabelecimento da conexão cliente-servidor via socket TCP e execução do handshake inicial, com negociação de três parâmetros: modo de operação, tamanho máximo do texto e tamanho da janela. A fragmentação do texto e a troca de dados são escopo do Checkpoint 2.

Implementação em Python 3, sem bibliotecas externas. Dois arquivos: `servidor.py` e `cliente.py`.

---

## 2. Protocolo proposto

### 2.1 Formato do pacote

```
TIPO|SEQ|TAM|CRC|PAYLOAD
```

| Campo | Tamanho | Descrição |
|---|---|---|
| TIPO | 3 caracteres | `HSK` neste checkpoint. `DAT`, `ACK` e `NAK` entram no CP2. |
| SEQ | 2 dígitos | Número de sequência do pacote. Limita o texto a 400 caracteres (100 fragmentos de 4). |
| TAM | variável | Quantidade de caracteres do payload. |
| CRC | 4 caracteres | Soma de verificação. Reservado com `0000` no CP1. |
| PAYLOAD | variável | Conteúdo. Nos pacotes `DAT` será limitado a 4 caracteres. |

O limite de 4 caracteres imposto pela especificação aplica-se ao conteúdo da aplicação, transportado nos pacotes `DAT`. Os pacotes de controle (`HSK`, `ACK`, `NAK`) carregam parâmetros do protocolo, não conteúdo do usuário, e por isso não estão sujeitos a esse limite.

### 2.2 Requisições e respostas do handshake

**Requisição — cliente propõe:**

```
HSK|00|10|0000|SR;LOTE;45
                └── MODO;ENVIO;TAMANHO_MAXIMO
```

- `MODO`: `GBN` (Go-Back-N) ou `SR` (Repetição Seletiva)
- `ENVIO`: `IND` (individual) ou `LOTE`
- `TAMANHO_MAXIMO`: inteiro entre 30 e 400

**Resposta — servidor decide:**

```
HSK|00|15|0000|OK;SR;LOTE;45;5
                └── STATUS;MODO;ENVIO;TAMANHO_MAXIMO;JANELA
```

### 2.3 Regras de negociação

O cliente **propõe** e o servidor **decide**. A janela é atribuição exclusiva do servidor: ela representa a capacidade de recepção, e apenas o receptor conhece o próprio limite. O protocolo reserva para ela a faixa de 1 a 5. Neste checkpoint o servidor anuncia sempre o valor máximo, 5: não há troca de dados, e portanto nenhuma condição de recepção que justifique reduzi-lo. O ajuste dentro da faixa passa a fazer sentido no CP2, quando os pacotes `DAT` começam a circular e a janela efetivamente limita o envio.

O servidor valida os parâmetros recebidos. Modo ou tipo de envio desconhecidos são substituídos pelos padrões (`GBN` e `IND`); tamanho de texto fora da faixa é ajustado ao limite mais próximo, 30 ou 400.

O limite superior decorre do campo `SEQ`: com dois dígitos e fragmentos de 4 caracteres, o espaço de numeração comporta 400 caracteres de texto. Aceitar valores maiores geraria pacotes com número de sequência fora do formato declarado no cabeçalho.

A resposta sempre informa os valores efetivamente adotados. O cliente compara cada um com o que propôs e imprime uma linha de divergência para cada parâmetro alterado pelo servidor.

### 2.4 Tratamento de pacotes malformados

A leitura usa `split("|", 4)`, que corta apenas nos quatro primeiros separadores — um caractere `|` presente no payload não quebra a decodificação.

Após a decodificação, dois campos são conferidos antes de qualquer uso do pacote:

- **TIPO** deve ser `HSK`. Sem essa checagem, um pacote de dados ou de confirmação seria interpretado como handshake — irrelevante enquanto só existe um tipo, mas incorreto a partir do CP2.
- **TAM** deve corresponder ao comprimento real do payload. O campo é o mesmo que o CRC vai proteger no CP2, e um cabeçalho que não descreve o próprio conteúdo invalida a verificação de integridade.

Pacotes fora do formato (separador ausente, campo numérico inválido, TIPO inesperado ou TAM incoerente) geram `ValueError`, tratado com descarte da conexão e retorno ao estado de espera, sem interromper o servidor. A mensagem de erro identifica a causa. As duas checagens ocorrem depois da impressão dos metadados, de modo que um pacote rejeitado ainda é exibido — o que a especificação exige e que também facilita a depuração.

As mesmas validações são aplicadas pelo cliente à resposta do servidor.

### 2.5 Decisões de projeto

**Representação textual em vez de binária.** O pacote trafega como texto legível delimitado por `|`. A alternativa (`struct.pack`, campos binários de posição fixa) é mais compacta e mais próxima de protocolos reais, mas dificulta a inspeção durante os testes e a demonstração. Como a especificação exige que os metadados sejam impressos nos dois lados, a forma legível foi considerada mais adequada.

**Campo CRC reservado desde o início.** O cálculo da soma de verificação é escopo do CP2, mas o campo já ocupa sua posição no cabeçalho. Assim o formato do pacote não muda entre os checkpoints, e o código de montagem e leitura permanece estável.

**Leitura por linha via `makefile`.** O TCP entrega um fluxo contínuo de bytes, sem preservar fronteiras entre mensagens: duas chamadas de envio podem chegar em uma única leitura. O socket é convertido em objeto de arquivo e cada pacote é terminado por `\n`, o que delimita as mensagens de forma explícita.

---

## 3. Manual de utilização

**Requisitos:** Python 3. Nenhuma dependência externa.

Abrir dois terminais na pasta dos arquivos.

```
Terminal 1:  python3 servidor.py
Terminal 2:  python3 cliente.py
```

O cliente faz três perguntas; Enter aceita o padrão.

| Pergunta | Opções | Padrão |
|---|---|---|
| Modo de confirmação | GBN / SR | GBN |
| Modo de envio | IND / LOTE | IND |
| Tamanho máximo do texto | número de 30 a 400 | 30 |

Respostas inválidas exibem uma mensagem de erro e repetem a pergunta, sem encerrar o programa. Se o servidor não estiver ativo, ou se a entrada for interrompida com Ctrl+D, o cliente encerra com mensagem própria.

**Execução em máquinas distintas:** alterar a constante `HOST` nos dois arquivos para o IP do servidor. Porta padrão: 5000.

---

## 4. Processo de construção e uso de IA

### 4.1 Estratégia de aprendizado

A IA (Claude) foi utilizada em todas as etapas deste checkpoint, conforme autorizado pela especificação: explicação dos conceitos de transporte confiável, discussão das alternativas de projeto, geração do código e revisão do texto deste relatório.

O uso partiu de um nível baixo de familiaridade com o tema. A sequência adotada foi: primeiro obter um panorama do que a especificação exigia, depois entender os conceitos envolvidos (cliente/servidor, socket, fragmentação, os seis mecanismos da tabela 3.1), em seguida decidir o formato do pacote e só então gerar o código.

A IA foi empregada para levantar alternativas e explicar suas implicações, mas a definição do protocolo é do grupo. Todas as escolhas estruturais registradas abaixo foram decididas pelos integrantes, com base nos critérios do próprio grupo — em particular, a prioridade de manter o código curto o bastante para ser lido e explicado integralmente, ainda que ao custo de recursos adicionais que a IA havia proposto:

| Decisão | Alternativas | Escolha e motivo |
|---|---|---|
| Linguagem | Python, Java, C | Python — biblioteca de sockets nativa e menos código acessório. |
| Formato do pacote | Texto delimitado vs. binário | Texto — inspeção direta durante testes e apresentação. |
| Organização | Dois arquivos vs. módulos separados | Dois arquivos — menor superfície de código para dominar. |
| Extensão do código | Versão comentada vs. enxuta | Enxuta — priorizar a leitura integral do código pelo grupo. |
| Robustez | Manter ou remover validações | Manter — requisito definido pelo grupo. |
| Janela no CP1 | Valor fixo vs. variação simulada | Fixo em 5 — variar sem fluxo de dados seria arbitrário. |

Todo o código entregue foi revisado, testado e compreendido pelo grupo antes da submissão, conforme o compromisso de validação crítica previsto na especificação.

### 4.2 Análise crítica e correções

**Primeira versão excessivamente extensa.** A entrega inicial da IA tinha aproximadamente 150 linhas, com comentários e camadas de validação que não eram exigidas pela especificação. O grupo avaliou que o volume comprometia o objetivo de compreender integralmente o código e solicitou uma redução ao essencial, preservando apenas o tratamento de entrada inválida. A versão enxuta ficou em 111 linhas; a revisão descrita a seguir a levou a 134.

**Inconsistência entre código e documentação.** Ao enxugar o código, foi removido o pacote de tipo `ERR`, enviado quando o primeiro pacote recebido não era um handshake. O manual de utilização, escrito antes dessa redução, continuou descrevendo esse comportamento — documentando uma funcionalidade que não existia mais. A divergência foi identificada na conferência final e o manual foi corrigido para descrever o comportamento real: descarte da conexão e retorno ao estado de espera.

Esse caso ilustra um risco específico do desenvolvimento assistido por IA: alterações pontuais no código não propagam automaticamente para os artefatos já produzidos. A verificação cruzada entre código e documentação passou a ser feita a cada modificação.

**Revisão final da entrega.** Uma última conferência linha a linha, feita com a IA a partir do repositório já montado, encontrou cinco defeitos que os testes manuais do grupo não haviam alcançado, porque todos exigiam pacotes que o próprio cliente nunca produz:

| Defeito | Consequência | Correção |
|---|---|---|
| `TIPO` não era verificado | Um pacote `DAT` era aceito como handshake | Checagem explícita de `HSK` |
| `TAM` não era conferido | Cabeçalho podia declarar tamanho falso | Comparação com o comprimento do payload |
| Ausência de limite superior no tamanho | `SEQ` estouraria os 2 dígitos no CP2 | Faixa fechada de 30 a 400 |
| Divergência não era comparada no cliente | Comportamento descrito na seção 2.3 não existia no código | Comparação campo a campo |
| `EOFError` não tratado | Ctrl+D encerrava com rastreamento de pilha | Saída com mensagem |

Os três primeiros só se manifestam contra um par malformado, situação que passa a existir no CP2, quando `DAT`, `ACK` e `NAK` entram em circulação. Foram corrigidos agora porque o custo cresce a cada checkpoint. O quarto é outra ocorrência do descompasso entre código e documentação descrito acima, desta vez na direção inversa: o relatório prometia um comportamento que o código não tinha.

A verificação foi conduzida enviando pacotes malformados diretamente ao servidor por socket, fora do cliente — treze casos, entre separador ausente, campos numéricos inválidos, TIPO inesperado, TAM incoerente e valores fora de faixa. O servidor descartou todos e permaneceu disponível para a conexão seguinte.

### 4.3 Log de prompts

Principais temas tratados com a IA nesta etapa:

| Tema | Objetivo do prompt |
|---|---|
| Interpretação da especificação | Mapear requisitos, checkpoints e critérios de avaliação |
| Escolha da linguagem | Comparar Python, Java e C para implementação de sockets |
| Formato do pacote | Entender a diferença entre representação textual e binária |
| Conceitos de transporte confiável | Compreender os mecanismos da tabela 3.1 e os modos GBN e SR |
| Implementação do handshake | Gerar e revisar `servidor.py` e `cliente.py` |
| Redução do código | Identificar o que era essencial e o que era acessório |
| Auditoria do repositório | Revisar o código publicado e testar pacotes malformados |

A tabela acima constitui o anexo com os principais prompts utilizados na arquitetura, implementação e testes, conforme previsto na especificação.

---

## 5. Próximos checkpoints

**CP2 (21/10):** implementação do CRC-16 sem bibliotecas externas, fragmentação do texto em payloads de 4 caracteres, números de sequência, ACK/NAK, temporizador e controle de janela — no caminho sem erros e sem perdas.

**CP3 (23/11):** simulador determinístico de erros e perdas no cliente, retransmissão em Go-Back-N e Repetição Seletiva, e criptografia simétrica implementada manualmente. A ordem de operações definida é cifrar o payload antes de calcular o CRC, de modo que a verificação de integridade ocorra sobre o pacote efetivamente transmitido.
