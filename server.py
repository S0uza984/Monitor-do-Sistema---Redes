import socket
from datetime import datetime
import threading
import psutil
import sys

# gerenciamento de clientes
connected_clients = []
client_limit = 5
client_lock = threading.Lock()

def send_message(client,msg):
    try:
        client.send(msg.encode("utf-8"))
    except:
        pass
    
def monitor_cpu(client,periodo,stop_cpu):
    while not stop_cpu.is_set():
        if stop_cpu.wait(periodo):
            break
        try:
            uso_cpu = psutil.cpu_percent(interval=0.1)
            client.send(f"Uso de CPU: {uso_cpu}%.".encode("utf-8"))
        except Exception:
            break
        
        
        
def monitor_memoria(client,periodo, stop_memoria):
    while not stop_memoria.is_set():
        if stop_memoria.wait(periodo):
            break
        try:
            uso_memoria = psutil.virtual_memory().percent
            client.send(f"Uso de memória em: {uso_memoria}%".encode("utf-8"))
        except Exception:
            break
    
    
        
def handle_client(client,addr,menu):
    global connected_clients
    
    # adiciona cliente
    with client_lock:
        connected_clients.append((client, addr))
        print(f"Monitor {str(addr)} conectado. Total de monitores: {len(connected_clients)}")
    
    stop_cpu = threading.Event()
    stop_mem = threading.Event()
    
    monitor_da_cpu = None
    monitor_da_memoria = None
    
    while True:
        try:
            msg_monitoramento = client.recv(1024).decode("utf-8").strip()
            
            if not msg_monitoramento:
                print(f"Monitor no ip: {str(addr)}, desconectado")
                break
            
            msg_lower = msg_monitoramento.lower()
            
            if msg_lower == "exit":
                send_message(client,"Desconectando seu monitor do servidor")
                stop_cpu.set()
                stop_mem.set()
                break 
            
            if msg_lower == "quit":
                if monitor_da_cpu and monitor_da_cpu.is_alive() or monitor_da_memoria and monitor_da_memoria.is_alive():
                    stop_cpu.set()
                    stop_mem.set()
                    
                    stop_cpu = threading.Event()
                    stop_mem = threading.Event()
                    send_message(client,"Todos os monitoramentos foram parados")
                else:
                    send_message(client,"Não há monitoramentos a serem parados")
                continue
                
            if msg_lower == "help":
                send_message(client,menu)
                continue
            
            try:
                partes = msg_lower.split("-",1)
                comando = partes[0].strip()
                comando2 = partes[1].strip()
            except Exception as e:
                send_message(client,"Comando inválido. Use CPU-<segundos>, MEM-<segundos>, QUIT-<mem/memoria ou CPU> ou EXIT")
                continue
            
            try:
                if comando == "quit":
                    if comando2 in ("mem", "memória"):
                        if monitor_da_memoria and monitor_da_memoria.is_alive():
                            stop_mem.set()
                            stop_mem = threading.Event()
                            send_message(client, "Monitoriamento da memoria parado")
                        else:
                            send_message(client, "Não há monitoramento de memoria a ser parado")
                    elif comando2 == "cpu":
                        
                        if monitor_da_cpu and monitor_da_cpu.is_alive():
                            stop_cpu.set()
                            stop_cpu = threading.Event()
                            send_message(client, "Monitoriamento da cpu parado")                   
                        else:
                            send_message(client, "Não há monitoramento de cpu a ser parado")
                    else:
                        send_message(client, "Comando inválido. Use CPU-<segundos>, MEM-<segundos>, QUIT-<mem/memoria ou CPU> ou EXIT")
                elif comando == "cpu":
                    comando2 = int(comando2)
                    
                    if monitor_da_cpu and monitor_da_cpu.is_alive():
                        stop_cpu.set()
                        
                    stop_cpu = threading.Event()
                    client.send(f"Iniciando monitoriamento da CPU a cada {comando2}s".encode("utf-8"))
                    
                    monitor_da_cpu = threading.Thread(target=monitor_cpu, args=(client, comando2, stop_cpu), daemon=True)
                    monitor_da_cpu.start()
                elif comando in ("mem", "memória"):
                    comando2 = int(comando2)
                    
                    if monitor_da_memoria and monitor_da_memoria.is_alive():
                        stop_mem.set()
                        
                    stop_mem = threading.Event()
                    
                    client.send(f"Iniciando monitoriamento da MEMÓRIA a cada {comando2}s".encode("utf-8"))
                    
                    monitor_da_memoria = threading.Thread(target=monitor_memoria, args=(client, comando2, stop_mem), daemon=True)
                    monitor_da_memoria.start()
                else:
                    send_message(client, "Comando inválido. Use CPU-<segundos>, MEM-<segundos>, QUIT-<mem/memoria ou CPU> ou EXIT")
            except ValueError:
                send_message(client, "Período inválido. Use um número inteiro positivo para os segundos.")
        except Exception as e:
            print(f"Ocorreu um erro: a conexão com o monitor {str(addr)} foi perdida repentinamente")
            client.close()
            break
    
    # remove cliente
    with client_lock:
        connected_clients = [(c, a) for c, a in connected_clients if c != client]
        print(f"Monitor {str(addr)} desconectado. Total de clientes: {len(connected_clients)}")
    
    client.close()
    
        
            
            
def receive(server):
    global connected_clients, client_limit
    
    while True:
        try:
            client, addr = server.accept()
            
            # verifica limite
            with client_lock:
                if len(connected_clients) >= client_limit:
                    horario = datetime.now().strftime("<%H:%M:%S>")
                    client.send(f"{horario}: LIMITE DE CLIENTES ATINGIDO. Máximo permitido: {client_limit}".encode("utf-8"))
                    client.close()
                    print(f"Monitor {str(addr)} rejeitado - limite atingido ({len(connected_clients)}/{client_limit})")
                    continue
            
            # aceita cliente
            horario = datetime.now().strftime("<%H:%M:%S>")
            client.send(f"{horario}: CONECTADO!!".encode("utf-8"))
            menu = f"""
                Funções Disponíveis:
                - Help                      : Reenvia as informações de cada comando
                - CPU-<segundos>            : Monitora o uso da CPU a cada <segundos>
                - MEMORIA-<segundos>        : Monitora o uso da memória a cada <segundos>
                - QUIT                      : Para todos os monitoramentos
                - QUIT-<mem/memoria ou cpu> : Para um monitoramento específico 
                - EXIT                      : Encerra a conexão
                Exemplo de uso: CPU-5
                """
            client.send(menu.encode("utf-8"))
            
            # cria thread
            conexao_client_thread = threading.Thread(target=handle_client, args=(client,addr,menu), daemon=True)
            conexao_client_thread.start()
            
        except Exception as e:
            print("Ocorreu um erro no servidor:",e)
            server.close()
            break
        
    server.close()
    

def Main():
    global client_limit
    
    # verifica argumentos
    if len(sys.argv) > 1:
        try:
            client_limit = int(sys.argv[1])
            if client_limit <= 0:
                print("Erro: O limite de monitores deve ser um número positivo.")
                return
        except ValueError:
            print("Erro: O limite de monitores deve ser um número inteiro.")
            print("Uso: python server.py [limite_clientes]")
            return
    else:
        print(f"Usando limite padrão de {client_limit} monitores.")
        print("Para definir um limite personalizado, use: python server.py [limite_clientes]")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('0.0.0.0', 9999))
        server.listen(5)
    except Exception:
        print("\nErro ao iniciar o servidor: não foi possível vincular o socket.\n")
        return
        
    
    print(f"Servidor iniciado com sucesso!")
    print(f"Limite de monitores: {client_limit}")
    print("Aguardando conexões...")

    receive(server)
    
if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        print("\nServidor encerrado manualmente.")
    
