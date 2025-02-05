import socket # Operações sobre sockets
from typing import Optional # Anotações de tipo

"""
    TODO: Descrever esse arquivo aqui
    TODO: Fazer validações do input
"""

def has_body(HTTPLine:str) -> bool:
    """
    Função que determina se a requisição HTTP recebida tem ou não um corpo de mensagem
    Isso é inferido a partir do método presente na requisição
    Caso a requisição seja um POST, PUT ou PATCH, então ela terá um corpo, caso contrário não terá
    O método DELETE também aceita um corpo na requisição, porém sua semântica não é definida, então esse caso
        não será considerado e o corpo de qualquer requisição DELETE será descartado
    
    Recebe:
        HTTPLine: A primeira linha da requisição HTTP, contendo o método da requisição
        
    Retorna:
        Booleano indicando se a requisição tem ou não um corpo
    """
    
    return "POST" in HTTPLine or "PUT" in HTTPLine or "PATCH" in HTTPLine

def handle_request(clientSocket: socket.socket) -> bool:
    """
    Função que lida com uma requisição HTTP
    Quando o servidor receber uma requisição, essa função irá processar a mensagem HTTP recebida
    Após processar a mensagem, irá chamar a função que processa a reposta para essa requisição
    Retorna booleano indicando se a requisição foi aceita ou não
    
    Recebe:
        clienteSocket: A porta na qual um cliente se conectou e está mandando uma requisição HTTP
        
    Retorna:
        True caso a requisição tenha sido aceita (retorno 1xx, 2xx ou 3xx)
        False caso a requisição tenha sido recusada (retorno 4xx ou 5xx)
    """
    
    HTTPStartLine = "" # Primeira linha da requisição (onde tem o método)
    HTTPHeaders   = "" # Cabeçalhos da requisição
    HTTPBody      = "" # Corpo da requisição
    
    # Ouvindo a mensagem que o cliente está mandando para o servidor
    with clientSocket.makefile() as incomingMessage:
        
        # deve ter um jeito melhor de fazer isso, mas isso fica para depois
        aux = 0
        blanks = 0
        max_blanks = 2
        
        # Processando a requisição que está chegando
        for line in incomingMessage:
        
            if aux == 0:
                HTTPStartLine = line
                # Caso o método não tenha um corpo, não preciso contar duas linhas vazias
                max_blanks = max_blanks - 1 if not has_body(HTTPStartLine) else max_blanks
        
            if aux > 0 and blanks == 0:
                # Cabeçalhos acabam após uma linha vazia
                HTTPHeaders += line
                
            if aux > 0 and blanks == 1 and (line != "\r\n" or line != "\n"):
                # Corpo da mensagem começa após uma linha vazia, mas não pode ele mesmo conter uma linha vazia
                HTTPBody += line
                
            if line == "\r\n" or line == "\n":
                blanks += 1
            
            if blanks == max_blanks:
                # Aqui eu começo a processar a resposta
                print(f"Primeira linha: {HTTPStartLine.rstrip()}")
                
                print(f"Cabeçalhos:")
                for header in HTTPHeaders.splitlines():
                    print(f"\t{header.rstrip()}")
                    
                print(f"Corpo:")
                for body in HTTPBody:
                    print(f"\t{body.rstrip()}")

            aux += 1
    
    return True

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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        # Associando a porta com o localhost
        
        serverSocket.bind(("localhost", port))
        
        serverSocket.listen(5) # Servidor vai aceitar no máximo 5 conexões simultâneas
        
        print(f"\nServidor funcinando em localhost:{port}")
        
        # Loop principal do servidor
        while True:
            # Recebendo conexões de um cliente
            # Quando um cliente conecta, ele é associado a uma nova porta e seu endereço é capturado
            clientSocket, address = serverSocket.accept()
            
            print(f"Conexão vinda de {address}")
            
            request = handle_request(clientSocket)
        
    return
    

