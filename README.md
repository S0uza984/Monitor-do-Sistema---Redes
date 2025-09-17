# monitor do sistema - redes

repositorio destinado ao desenvolvimento do projeto de redes, onde sera desenvolvido um sistema de monitoramento do sistema aplicando a biblioteca sockets em python.

## fase 2: implementacao multi-cliente

### funcionalidades implementadas

#### servidor (`server.py`)
- multi-cliente simultaneo: suporta multiplos clientes conectados ao mesmo tempo
- limite de clientes: configuravel via linha de comando
- threads independentes: cada cliente e tratado em uma thread separada
- gerenciamento de conexoes: controle automatico de clientes conectados/desconectados
- rejeicao por limite: clientes sao rejeitados quando o limite e atingido
- liberacao de recursos: recursos sao liberados automaticamente quando cliente desconecta

#### cliente (`client.py`)
- comando de desconexao: comando `exit` para desconectar graciosamente
- tratamento de rejeicao: detecta quando servidor rejeita conexao por limite
- interface melhorada: mensagens mais claras para o usuario

### como usar

#### executar o servidor
```bash
# com limite padrao (5 clientes)
python server.py

# com limite personalizado (ex: 3 clientes)
python server.py 3
```

#### executar o cliente
```bash
python client.py
```

#### comandos disponiveis
- `help` - mostra o menu de comandos
- `cpu-<segundos>` - monitora cpu a cada x segundos
- `memoria-<segundos>` - monitora memoria a cada x segundos
- `quit` - para todos os monitoramentos
- `quit-<cpu/memoria>` - para monitoramento especifico
- `exit` - desconecta do servidor


### arquitetura

- thread principal: aguarda novas conexoes via `accept()`
- threads de trabalho: uma para cada cliente conectado
- memoria compartilhada: lista de clientes conectados com lock para thread-safety
- gerenciamento de recursos: limpeza automatica quando cliente desconecta

### requisitos
- python 3.6+
- psutil (para monitoramento do sistema)
