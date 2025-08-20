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
    while True:
        msg_monitoramento = client.recv(1024).decode("utf-8")
        if(msg_monitoramento.lower() == "exit"):
                client.send("Saindo da conexão".encode("utf-8")) #termina a conexão e as threads
                client.close()
                break
        else:
                partes = msg_monitoramento.split("-")
                comando = partes[0]
                periodo = int(partes[1])
                if(comando.lower() == "mem"):
                    monitor_thread = threading.Thread(target=monitor_memoria, args=(client, periodo))
                    monitor_thread.start()
                elif(comando.lower() == "cpu"):
                    monitor_thread = threading.Thread(target=monitor_cpu, args=(client, periodo))
                    monitor_thread.start()

def monitor_memoria(client,periodo):
    while True:
        uso_memoria = psutil.virtual_memory().percent
        client.send(f"Uso de Memória: {uso_memoria}%".encode("utf-8"))
        threading.Event().wait(periodo)
def monitor_cpu(client,periodo):
    while True:
        uso_cpu = psutil.cpu_percent(interval=periodo)
        print({uso_cpu})
        client.send(f"Uso de CPU: {uso_cpu}%".encode("utf-8"))

receive()