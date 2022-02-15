# **UFCoin**

Trabalho da disciplina de Projeto Integrador IV.


## **Executar**
---

Instalar dependências:

```
$ python -m pip install -r requiriments.txt
```

Executar:

```
$ python . [http-port] [ws-port]
```

- `http-port`: Argumento opcional. Representa a porta a ser usada pelo servidor
http. Valor padrão: 5000.
- `ws-port`: Argumento opcional. Representa a porta a ser usada pelo servidor
p2p. Valor padrão: 6000.

Exemplo:

```
$ python . 5000 6000
```


## **Instruções de uso**
---

### **Mineração**
---

Para iniciar a mineração, clique em `minerar` no menu lateral e em seguida
clique no ícone no centro da tela.

Para parar a mineração, clique novamente no ícone no centro da tela.

Ao minerar um novo bloco, o usuário recebe 5 unidades da criptomoeda.

Para verificar os blocos minerados, clique em `chain` no menu lateral.


### **Adicionar novos peers**
---

A descoberta de novos peers na rede não ocorre de forma automática. Todos os
peers devem ser adicionados manualmente.

Para adicionar um novo peer, clique em `peers` no menu lateral. No campo
"Endereço P2P", adicione o endereço do servidor P2P do peer e clique em
adicionar.

O endereço P2P de cada peer pode ser visualizado na tela inicial.


### **Transações**
---

Para realizar uma transação, clique em `transações` no menu lateral. No
formulário, adicione o endereço de transações do outro peer, a quantidade de
moedas a serem enviadas e clique em "concluir transação".

O endereço de transações de cada peer pode ser visualizado na
[carteira](#carteira).

A transação será validada e caso seja válida, será adicionada à blockchain. Caso
seja invalida, será descartada.

Se a transação for válida, a  quantidade enviada será adicionada ao saldo do
destinatário e subtraida do saldo do rementente.

Para verificar se a transação ocorreu com sucesso, clique em `listar transações`
no menu lateral e verifique se a transação aparece na lista (novas transações
são adicionadas ao final da lista). Também pode verificar se o saldo nas
carteiras do remetente e destinatário foi atualizado.

É necessário ter saldo maior ou igual à quantidade enviada. Caso contrário, a
transação não será realizada.

É necessário que o destinatário esteja incluso na rede para que a transação seja
realizada com sucesso. Para adicionar novos peers, veja
[adicionar novos peers](#adicionar-novos-peers).

Transações só podem ser realizadas a cada 10 minutos por um mesmo usuário.


### **Carteira**
---

A carteira exibe o saldo do usuário e o endereço de transações.

O endereço de transações é derivado a partir de um hash do nome de usuário e
senha que o usuário utilizou para se identificar na tela de login.
