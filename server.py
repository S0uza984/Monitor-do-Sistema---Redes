import socket
from datetime import datetime

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(5)

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
    print(client.recv(1024).decode())
    client.send(menu.encode())