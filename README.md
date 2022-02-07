# **UFCoin**

Trabalho da disciplina de Projeto Integrador IV.


## **Executar**
---

Instalar dependências:

```
$ python3 -m pip install -r requiriments.txt
```

Executar:

```
$ python3 . [http-port] [ws-port]
```

- `http-port`: Argumento opcional. Representa a porta a ser usada pelo servidor
http. Valor padrão: 5000.
- `ws-port`: Argumento opcional. Representa a porta a ser usada pelo servidor
p2p. Valor padrão: 6000.

Exemplo:

```
$ python3 . 5000 6000
```


## **Instruções de uso**
---

### **Mineração**
---

Para iniciar a mineração, clique em `minerar` no menu lateral.

Para parar a mineração, clique no ícone no centro da tela.

Para iniciar a mineração novamente, clique novamente no ícone no centro da tela.


### **Adicionar novos peers**
---

A descoberta de novos peers na rede não ocorre de forma automática. Todos os
peers devem ser adicionados manualmente.

Para adicionar um novo peer, clique em `peers` no menu lateral. No campo
"Endereço P2P", adicione o endereço do servidor P2P do peer e clique em
adicionar.


### **Transações**
---

Para realizar uma transação, cliquem em `transações` no menu lateral. No
formulário, adicione o endereço de transações do outro peer, a quantidade de
moedas a serem enviadas e clique em "concluir transação".

A quantidade enviada será adicionada ao saldo do destinatário quando o próximo
bloco for minerado.

É necessário ter saldo maior ou igual à quantidade enviada. Caso contrário, a
transação não será realizada.
