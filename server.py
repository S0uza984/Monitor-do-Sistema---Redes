import socket
from datetime import datetime
import threading
import psutil

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(5)

def receive():
    while True:
        client, addr = server.accept()
        horario = datetime.now().strftime("<%H:%M:%S>")
        menu = f"""{horario}: CONECTADO!!
            Menu de Monitores Disponíveis:
            - CPU-<segundos>      : Monitora o uso da CPU a cada <segundos>
            - MEMORIA-<segundos>  : Monitora o uso da memória a cada <segundos>
            - QUIT                : Para o monitoramento atual
            - EXIT                : Encerra a conexão
            Exemplo de uso: CPU-5
            """
        client.send(menu.encode())
        print(f"Conectado {str(addr)}")
        conexao_thread= threading.Thread(target=handle, args=(client,))
        conexao_thread.start()

def handle(client):
    # Controla o monitoramento atual deste cliente
    stop_event_atual = None
    while True:
        try:
            msg_monitoramento = client.recv(1024).decode("utf-8").strip()
        except Exception:
            # Erro de leitura/cliente desconectado
            try:
                client.close()
            except Exception:
                pass
            break

        if not msg_monitoramento:
            # Cliente enviou vazio ou desconectou
            try:
                client.close()
            except Exception:
                pass
            break

        msg_lower = msg_monitoramento.lower()

        if msg_lower == "exit":
            # Finaliza conexão e qualquer monitor ativo
            if stop_event_atual is not None:
                stop_event_atual.set()
                stop_event_atual = None
            try:
                client.send("Saindo da conexão".encode("utf-8"))
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass
            break

        if msg_lower == "quit":
            # Para o monitoramento atual, se houver
            if stop_event_atual is not None:
                stop_event_atual.set()
                stop_event_atual = None
                try:
                    client.send("Monitoramento parado".encode("utf-8"))
                except Exception:
                    pass
            else:
                try:
                    client.send("Nenhum monitoramento em execução".encode("utf-8"))
                except Exception:
                    pass
            continue

        # Tenta interpretar comandos do tipo <cpu|mem|memoria>-<segundos>
        try:
            partes = msg_monitoramento.split("-", 1)
            comando = partes[0].strip().lower()
            periodo = int(partes[1].strip())
            if periodo <= 0:
                raise ValueError()
        except Exception:
            try:
                client.send(
                    "Comando inválido. Use CPU-<segundos>, MEM-<segundos>, QUIT ou EXIT".encode("utf-8")
                )
            except Exception:
                pass
            continue

        # Se já há um monitor, para-o antes de iniciar outro
        if stop_event_atual is not None:
            stop_event_atual.set()
            stop_event_atual = None

        stop_event_atual = threading.Event()

        if comando in ("mem", "memoria"):
            monitor_thread = threading.Thread(
                target=monitor_memoria, args=(client, periodo, stop_event_atual), daemon=True
            )
            monitor_thread.start()
            try:
                client.send(f"Iniciando monitor de memória a cada {periodo}s".encode("utf-8"))
            except Exception:
                pass
        elif comando == "cpu":
            monitor_thread = threading.Thread(
                target=monitor_cpu, args=(client, periodo, stop_event_atual), daemon=True
            )
            monitor_thread.start()
            try:
                client.send(f"Iniciando monitor de CPU a cada {periodo}s".encode("utf-8"))
            except Exception:
                pass
        else:
            # Comando desconhecido
            if stop_event_atual is not None:
                stop_event_atual.set()
                stop_event_atual = None
            try:
                client.send("Comando desconhecido.".encode("utf-8"))
            except Exception:
                pass

def monitor_memoria(client, periodo, stop_event):
    while not stop_event.is_set():
        try:
            uso_memoria = psutil.virtual_memory().percent
            client.send(f"Uso de Memória: {uso_memoria}%".encode("utf-8"))
        except Exception:
            # Provável desconexão do cliente
            break
        # Aguarda período, mas permite interrupção rápida com QUIT
        if stop_event.wait(periodo):
            break

def monitor_cpu(client, periodo, stop_event):
    while not stop_event.is_set():
        try:
            # Bloqueia pelo período configurado enquanto mede a CPU
            uso_cpu = psutil.cpu_percent(interval=periodo)
            client.send(f"Uso de CPU: {uso_cpu}%".encode("utf-8"))
        except Exception:
            break

receive()