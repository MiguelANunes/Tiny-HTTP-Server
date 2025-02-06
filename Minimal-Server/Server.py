import socket                                # Operações sobre sockets
import logging                               # Biblioteca de criação de logs
from typing import Optional                  # Anotações de tipo
from ResponseHandler import Response         # Componentes do servidor
from RequestHandler import Request           # Componentes do servidor
from Exceptions import HTTPException         # Componentes do servidor
from Configuration import ServerConfig # Configurações do Servidor

"""
    TODO: Descrever esse arquivo aqui
    TODO: Fazer validações do input
    TODO: Capturar KeyBoardInterrupt no processo do servidor
"""

log = logging.getLogger("Main.Server")

def has_body(HTTPLine:str) -> bool:
    """
    Função que determina se a requisição HTTP recebida tem ou não um corpo de mensagem
    Isso é inferido a partir do método presente na requisição
    Caso a requisição seja um POST, PUT ou PATCH, então ela terá um corpo, caso contrário não terá
    O método DELETE também aceita um corpo na requisição, porém sua semântica não é definida, então esse caso
        não será considerado e o corpo de qualquer requisição DELETE será descartado 
        (informação retirada da documentação da Mozilla sobre HTTP)
    
    Recebe:
        HTTPLine: A primeira linha da requisição HTTP, contendo o método da requisição
        
    Retorna:
        Booleano indicando se a requisição tem ou não um corpo
    """
    
    return "POST" in HTTPLine or "PUT" in HTTPLine or "PATCH" in HTTPLine

def handle_request(clientSocket: socket.socket, serverConfigValues:ServerConfig) -> bool:
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
        
            if aux > 0 and blanks == 0 and (line != "\r\n" or line != "\n"):
                # Cabeçalhos acabam após uma linha vazia
                HTTPHeaders += line
                
            if aux > 0 and blanks == 1 and (line != "\r\n" or line != "\n"):
                # Corpo da mensagem começa após uma linha vazia, mas não pode ele mesmo conter uma linha vazia
                HTTPBody += line
                
            if line == "\r\n" or line == "\n":
                blanks += 1
            
            if blanks == max_blanks:
                # Quando ler todas as linhas da requisição enviada, começo a processar a requisição
                
                try:
                    clientRequest = Request(HTTPStartLine.rstrip(), HTTPHeaders, HTTPBody, serverConfigValues)
                    
                    log.info(f"Requisição recebida e processada:")
                    log.info(f"{10*'-'}")
                    log.info(f"\t{str(clientRequest)}")
                    log.info(f"{10*'-'}")
                    
                    responseToClient = Response(clientRequest, serverConfigValues) # Gero o objeto de resposta a partir da conexção
                    responseToClient.prepareResponse(serverConfigValues) # Preparando a resposta para ser eviada
                    
                    log.info(f"Resposta preparada e pronta para ser enviada:")
                    log.info(f"{10*'-'}")
                    log.info(f"\t{str(responseToClient)}")
                    log.info(f"{10*'-'}")
                    
                    formattedResponse = responseToClient.formatResponse()
                    
                    clientSocket.sendall(bytes(formattedResponse, "utf-8"))
                    
                    log.info("Resposta enviada")
                    
                    return True
                    
                except HTTPException as exception:
                    # Caso alguma exceção HTTP tenha sido levantada, processo ela com uma resposta de erro correspondente a exceção
                    log.warning("Excessão HTTP")
                    log.warning(exception)
                    return False
                except Exception:
                    # Caso qualquer outra exceção tenha sido levantada,
                    #   registro isso no log, respondo ao cliente com erro 418 e mato a conexão
                    log.warning("Outra excessão")
                    return False

            aux += 1
    
    return False

def server(serverConfigValues:ServerConfig, port:Optional[int]=None) -> None:
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
    if port is None:
        port = serverConfigValues.port  # type: ignore
    
    # Inicializando o servidor em uma porta TCP que recebe endereços IPv4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        
        # Pegando o host da configuração e a abrindo a conexão
        host = serverConfigValues.host
        serverSocket.bind((host, port))
        serverSocket.listen(5) # Servidor vai aceitar no máximo 5 conexões simultâneas
        
        print(f"Servidor funcinando em localhost:{port}")
        
        # Loop principal do servidor
        while True:
            # Recebendo conexões de um cliente
            # Quando um cliente conecta, ele é associado a uma nova porta e seu endereço é capturado
            clientSocket, address = serverSocket.accept()
            
            print(f"Conexão vinda de {address}")
            
            success = handle_request(clientSocket, serverConfigValues)
            
            if success:
                print("Requisição respondida com sucesso!")
            else:
                print("Erro na requisição!")
        
    return
    

