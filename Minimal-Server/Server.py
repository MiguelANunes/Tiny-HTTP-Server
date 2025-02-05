import socket # Operações sobre sockets
from typing import Optional # Anotações de tipo

def server(port:Optional[int]=None) -> None:
    """
    Função principal do servidor HTTP
    Fica em um loop constante ouvindo por requisições HTTP válidas no localhost numa porta fornecida por argumento
        Caso não tenha recebido uma porta, ouve na porta 9999
    Responde as requisições HTTP com respostas HTTP válidas
    
    Recebe:
        port (opcional): um int que indica a porta que o servidor deve estar escutando, caso não seja fornecido, usa a porta 9999
        
    Retorna:
        Nada
    """
    
    # Validando a porta
    if port == None:
        port = 9999
    
    # Inicializando o servidor em uma porta TCP que recebe endereços IPv4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Associando a porta com o localhost
        server_socket.bind("localhost", port) # type: ignore # Linter estava reclamando do port aqui
        
        server_socket.listen(5) # Servidor vai aceitar no máximo 5 conexões simultâneas
        
        # Loop principal do servidor
        while True:
            # Recebendo conexões
            client_socket, address = server_socket.accept()
            
            
            pass
        
    return
    

