import socket                                       # Operações sobre sockets
import logging                                      # Biblioteca de criação de logs
import json                                         # Abertura de arquivos .json
import selectors                                    # Multiplexação de input
import sys                                          # Funções do sistema
from typing import Optional, Any                    # Anotações de tipo
from ResponseHandler import Response, ErrorResponse # Módulo de Respostas HTTP
from RequestHandler import Request                  # Módulo de Requisições HTTP
from Exceptions import HTTPException, ImTeapot      # Módulo de Exceções específicas do Servidor
from Configuration import ServerConfig              # Configurações do Servidor

"""
Server.py
Módulo principal do meu servidor HTTP
Nesse módulo é inicializada a execução do servidor, as requisições são lidas vindas de uma socket e são respondidas para a mesma socket
Mensagens HTTP são inicialmente processadas aqui, antes de seu processamento ser passado para as classes específicas
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
        
        # Talvez tenha um jeito melhor de fazer isso
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
                # TODO: Talvez esse if não será necessário e todo processamento da mensagem deva ocorrer fora do with, testar mais
                # Quando ler todas as linhas da requisição enviada, começo a processar a requisição
                # Ver: https://stackoverflow.com/a/69859356
                
                try:
                    global id
                    
                    clientRequest = Request(HTTPStartLine.rstrip(), HTTPHeaders, HTTPBody, serverConfig, id)
                    
                    print(f"\tRequisição: {HTTPStartLine.rstrip()} ID: {id}")
                    
                    log.info(f"Requisição recebida e processada:")
                    log.info(f"\n\n{str(clientRequest)}")
                    
                    # Gero o objeto de resposta a partir da requisição
                    responseToClient = Response.createResponse(clientRequest, serverConfig, responses, types, id)
                    responseToClient.prepareResponse(serverConfig) # Preparando a resposta para ser eviada
                    
                    log.info(f"Resposta preparada e pronta para ser enviada:")
                    log.info(f"\n\n{responseToClient.printHead()}")
                    
                    # Método formatResponse() retorna a resposta gerada em binário, essa que é transmitida na socket sem conversão
                    responseInBinary = responseToClient.formatResponse()
                    ret = clientSocket.sendall(responseInBinary)
                    
                    if ret is not None:
                        log.warning("Erro ao enviar resposta!")
                        print("Erro ao enviar resposta!")
                    else:                    
                        log.info("Resposta enviada")
                    
                    id += 1
                    
                    return True
                    
                except HTTPException as exception:
                    # Caso alguma exceção HTTP tenha sido levantada, processo ela com uma resposta de erro correspondente a exceção
                    log.warning("Excessão HTTP")
                    log.warning(repr(exception))
                    
                    # Preparando a msg de erro a ser enviada ao cliente
                    errorResponse = ErrorResponse(exception, serverConfig, responses, types, id)
                    errorResponse.prepareResponse(serverConfig)
                    
                    log.info(f"Mensagem de erro preparada e pronta para ser enviada:")
                    log.info(f"\n\n{errorResponse.printHead()}")
                    
                    errorInBinary = errorResponse.formatResponse()
                    
                    ret = clientSocket.sendall(errorInBinary)
                    
                    if ret is not None:
                        log.warning("Erro ao enviar resposta!")
                        print("Erro ao enviar resposta!")
                    else:                    
                        log.info("Resposta enviada")
                    
                    id += 1
                    
                    return False
                except Exception as exception:
                    # Caso qualquer outra exceção tenha sido levantada,
                    #   registro isso no log, respondo ao cliente com erro 418 e mato a conexão
                    
                    log.warning("Outra excessão")
                    log.warning(repr(exception))
                    
                    # Preparando a msg de erro a ser enviada ao cliente
                    errorResponse = ErrorResponse(ImTeapot("Outra excessão"), serverConfig, responses, types, id)
                    errorResponse.prepareResponse(serverConfig)
                    
                    errorInBinary = errorResponse.formatResponse()
                    
                    ret = clientSocket.sendall(errorInBinary)
                    
                    if ret is not None:
                        log.warning("Erro ao enviar resposta!")
                        print("Erro ao enviar resposta!")
                    else:                    
                        log.info("Resposta enviada")
                    
                    id += 1
                    
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
    
    try:
        with open("json/response.json") as f:
            responseDict = json.load(f)
    except (OSError, FileNotFoundError) as err:
        log.critical("Arquivo de códigos de respostas HTTP não encontrado ou impossível de abrir! Encerrando execução")
        sys.exit()

    try:
        with open("json/mime.json") as f:
            contentDict = json.load(f)
    except (OSError, FileNotFoundError) as err:
        log.critical("Arquivo de códigos MIME associados a tipos de arquivos não encontrado ou impossível de abrir! Encerrando execução")
        sys.exit()
        
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
        serverSocket.listen(10) # Servidor vai aceitar no máximo 10 conexões simultâneas
        
        # Carregando a socket do servidor no seletor para lidar com múltiplas conexões simultâneas
        serverSocket.setblocking(False) # socket não pode estar em modo bloqueante para isso funcionar
        seletor = selectors.DefaultSelector()
        # Registrando a socket no seletor de modo que quando ela estiver disponível para ser lida poderei acessar ela
        seletor.register(serverSocket, selectors.EVENT_READ)
        
        log.info(f"Servidor funcinando em localhost:{port}")
        print(f"Servidor funcinando em localhost:{port}")
        
        resp, typ = load_json_data()
        
        # Preciso usar seletores pois navegadores enviam múltiplas requisições de uma vez
        # Parece ser algo parecido com pipelining (https://developer.mozilla.org/en-US/docs/Web/HTTP/Connection_management_in_HTTP_1.x#http_pipelining)
        # Mas não necessáriamente é isso
        # De qualquer forma, essa implementação consegue lidar com o problema
        
        incomingConnections = []
        
        try:
            # Loop principal do servidor
            while True:
                # Recebendo conexões 
                incomingConnections = seletor.select()
                
                for readySocket, _ in incomingConnections:
                    
                    # sanity
                    assert isinstance(readySocket.fileobj, socket.socket)
                    
                    if readySocket.fileobj is serverSocket:
                        # Quando a socket pronta para ser lida é a socket do servidor, aceito a conexão que está chegando e 
                        # registro essa conexão na fila de conexões para ser processada
                        
                        clientSocket, address = readySocket.fileobj.accept()
                        clientSocket.setblocking(False)
                        seletor.register(clientSocket, selectors.EVENT_READ)
                        
                        print(f"Conexão vinda de {address}")
                    
                    else:
                        # Caso não seja a socket do servidor, processo a conexão que chegou
                        success = handle_request(readySocket.fileobj, serverConfig, resp, typ)
                        # TODO: Caso queira respeitar o Connection: keep-alive do cliente, não deveria remover a socket daqui
                        seletor.unregister(readySocket.fileobj)
                        readySocket.fileobj.shutdown(socket.SHUT_RDWR)
                        readySocket.fileobj.close()
                                
                        if success:
                            print("Requisição respondida com sucesso!\n")
                        else:
                            print("Erro na requisição!\n")
        except (KeyboardInterrupt, Exception) as err: 
            # Caso ocorra qualquer excessão que não foi lidada anteriormente, fecho todas as conexões
            # Apenas "except Exception" não captura exceções de KeyboardInterrupt, pois elas herdam da classe Exception
            if type(err) is KeyboardInterrupt:
                log.warning("Execução do servidor encerrada pelo teclado! Fechando todas as conexões abertas.")
                print("\nExecução do servidor encerrada pelo teclado! Fechando todas as conexões abertas.")
            else:
                log.critical("Exceção inesperada! Fechando todas as conexões abertas.")
                log.critical(repr(err))
                print("\nExceção inesperada! Fechando todas as conexões abertas.")
            
            for readySocket, _ in incomingConnections:
                # sanity
                assert isinstance(readySocket.fileobj, socket.socket)
                
                try:                
                    readySocket.fileobj.shutdown(socket.SHUT_RDWR)
                    readySocket.fileobj.close()
                except OSError:
                    # As vezes acontece de tentar fechar uma socket já fechada, nesse caso só ignoro a socket e vida que segue
                    pass
        
    return
    

