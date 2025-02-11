import socket                                # Operações sobre sockets
import logging                               # Biblioteca de criação de logs
import json
from typing import Optional, Any             # Anotações de tipo
from ResponseHandler import Response         # Componentes do servidor
from RequestHandler import Request           # Componentes do servidor
from Exceptions import HTTPException         # Componentes do servidor
from Configuration import ServerConfig # Configurações do Servidor

"""
    TODO: Descrever esse arquivo aqui
    TODO: Fazer validações do input
    TODO: Talvez precise processar requisições de outra forma, ver: https://stackoverflow.com/questions/29023885/python-socket-readline-without-socket-makefile
"""

log = logging.getLogger("Main.Server")
id = 0 # Um id numérico e sequencial usado para identificar pares de requisição/resposta

def handle_request(clientSocket: socket.socket, serverConfig:ServerConfig, responses:dict[Any, Any], types:dict[Any, Any]) -> bool:
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
    
    # Função anônima para verificar se uma requisição tem um corpo que deve se rprocessado
    has_body = lambda l: "POST" in l or "PUT" in l or "PATCH" in l
    
    # Ouvindo a mensagem que o cliente está mandando para o servidor
    with clientSocket.makefile() as incomingMessage:
        
        # deve ter um jeito melhor de fazer isso, mas isso fica para depois
        # TODO: Fazer de jeito melhor
        linesRead = 0
        blanksRead = 0
        maxBlanks = 2
        
        # Processando a requisição que está chegando
        for line in incomingMessage:
        
            if linesRead == 0:
                HTTPStartLine = line
                # Caso o método não tenha um corpo, não preciso contar duas linhas vazias
                maxBlanks = maxBlanks - 1 if not has_body(HTTPStartLine) else maxBlanks
        
            if linesRead > 0 and blanksRead == 0 and (line != "\r\n" or line != "\n"):
                # Cabeçalhos acabam após uma linha vazia
                HTTPHeaders += line
                
            if linesRead > 0 and blanksRead == 1 and (line != "\r\n" or line != "\n"):
                # Corpo da mensagem começa após uma linha vazia, mas não pode ele mesmo conter uma linha vazia
                HTTPBody += line
                
            if line == "\r\n" or line == "\n":
                blanksRead += 1
            
            if blanksRead == maxBlanks:
                # Quando ler todas as linhas da requisição enviada, começo a processar a requisição
                
                try:
                    global id
                    
                    clientRequest = Request(HTTPStartLine.rstrip(), HTTPHeaders, HTTPBody, serverConfig, id)
                    
                    print(f"\tRequisição: {HTTPStartLine.rstrip()} ID: {id}")
                    
                    log.info(f"Requisição recebida e processada:")
                    log.info(f"\n\n{str(clientRequest)}")
                    
                    # Gero o objeto de resposta a partir da requisição
                    responseToClient = Response(clientRequest, serverConfig, responses, types, id)
                    responseToClient.prepareResponse(serverConfig) # Preparando a resposta para ser eviada
                    
                    log.info(f"Resposta preparada e pronta para ser enviada:")
                    log.info(f"\n\n{responseToClient.printHead()}")
                    
                    # Método formatResponse() retorna a resposta gerada em binário, essa que é transmitida na socket sem conversão
                    responseInBinary = responseToClient.formatResponse()
                    ret = clientSocket.sendall(responseInBinary)
                    
                    log.info("Resposta enviada")
                    
                    if ret is not None:
                        log.warning("Erro ao enviar resposta!")
                        print("Erro ao enviar resposta!")
                    
                    id += 1
                    
                    return True
                    
                except HTTPException as exception:
                    # Caso alguma exceção HTTP tenha sido levantada, processo ela com uma resposta de erro correspondente a exceção
                    log.warning("Excessão HTTP")
                    log.warning(repr(exception))
                    return False
                except Exception as exception:
                    # Caso qualquer outra exceção tenha sido levantada,
                    #   registro isso no log, respondo ao cliente com erro 418 e mato a conexão
                    log.warning("Outra excessão")
                    log.warning(repr(exception))
                    return False

            linesRead += 1
    
    return False

def load_json_data() -> "tuple[dict[Any, Any], dict[Any, Any]]":
    """
    Função que carrega em memória os código de retorno HTTP e códigos MIME de diversos tipos de arquivo
        em dois dicts
    Esses dados são lidos de arquivos .JSON que estão dentro da pasta /json/
    
    Recebe:
        Nada
        
    Retona:
        Uma tupla contendo os dicionários de códigos de retorno e tipos MIME
    """
    
    # TODO: Deveria ter um bloco try-except aqui
    
    with open("json/response.json") as f:
        responseDict = json.load(f)

    with open("json/mime.json") as f:
        contentDict = json.load(f)
        
    return (responseDict, contentDict)

def server(serverConfig:ServerConfig, port:Optional[int]=None) -> None:
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
        port = serverConfig.configValue["port"]
    
    # Inicializando o servidor em uma porta TCP que recebe endereços IPv4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        
        # Pegando o host da configuração e a abrindo a conexão
        host = serverConfig.configValue["host"]
        serverSocket.bind((host, port))
        serverSocket.listen(100) # Servidor vai aceitar no máximo 5 conexões simultâneas
        
        log.info(f"Servidor funcinando em localhost:{port}")
        print(f"Servidor funcinando em localhost:{port}")
        
        resp, typ = load_json_data()
        
        # Loop principal do servidor
        while True:
            # Recebendo conexões de um cliente
            # Quando um cliente conecta, ele é associado a uma nova porta e seu endereço é capturado
            clientSocket, address = serverSocket.accept()
            
            print(f"Conexão vinda de {address}")
            
            success = handle_request(clientSocket, serverConfig, resp, typ)
            
            if success:
                print("Requisição respondida com sucesso!\n")
            else:
                print("Erro na requisição!\n")
        
    return
    

