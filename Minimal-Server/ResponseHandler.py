import logging              # Biblioteca de criação de logs
import Exceptions
import ContentHandler
import json
from typing import Any, Union
from abc import ABC, abstractmethod # Implementação de métodos abstratos
from email.utils import formatdate
from RequestHandler import Request
from Configuration import ServerConfig # Configurações do Servidor
from Exceptions import HTTPException   # Módulo de Exceções específicas do Servidor

"""
ResponseHandler.py
Nesse módulo são definidas e processadas as requisições que são respondidas para o cliente 
O construtor da classe Response recebe uma requisição enviada pelo cliente e cónstroi uma resposta adequada para ela
Como as principais validações são feitas no módulo RequestHandler, não tenho tantas validações para fazer aqui
As validações que são feitas são referentes ao recurso que o cliente quer acessar, isto é, se o recurso existe, se o cliente pode acessar esse recurso, etc.
"""

log = logging.getLogger("Main.Server.Response")

class ErrorResponse():
    """
    Classe que representa respostas de erro HTTP
    Como eu não necessáriamente tenho uma requisição bem formatada para associar essa resposta, ela não herda da classe Response abaixo
    De qualquer forma, seus métodos tem mesmo nome para evitar confusão enquanto estou implementando
    Seu construtor recebe o erro que ocorreu durante processamento para poder determinar qual resposta enviar ao cliente
    """
    
    def __init__(self, error:HTTPException, serverConfig: ServerConfig, responseCodes: dict[Any, Any], contentTypes: dict[Any, Any], id: int) -> None:
        """
        Construtor da classe de respostas de erro
        Recebe o erro que ocorreu e apartir dele, obtém o código de resposta e os headers da mensagem a ser enviada
        """
        
        # Carregando alguns metadados
        self.HTTPResponseCodes = responseCodes
        self.MIMEContentTypes  = contentTypes
        
        # Inicializando código e mensagem de resposta a partir do erro ocorrido
        self.responseCode = error.code
        self.problem      = error.problem
        self.responseMsg  = self.HTTPResponseCodes[str(self.responseCode)]["message"]
        self.version      = serverConfig.configValue["httpVersion"]
        
        # Inicializando os headers da resposta
        self.headers                   = dict()
        self.headers["Server"]         = serverConfig.configValue["serverName"]
        self.headers["Date"]           = formatdate(timeval=None, localtime=False, usegmt=True)
        self.headers["Connection"]     = "close" # Não é usual fechar a conexão depois de toda msg, mas o protocolo permite
        self.headers["Content-Type"]   = "text/plain; charset=utf-8" # Valor padrão, muda dependendo do que está sendo retornado
        self.headers["Content-Lenght"] = 0 # Valor padrão, será calculado quando o conteúdo da resposta for determinado
        
        # Inicializando o corpo da resposta
        self.body: str
    
        # Identificando a resposta
        self.id = id
    
    def prepareResponse(self, serverConfig:ServerConfig) -> None:
        """
        Método que prepara a resposta de erro, dependendo do erro que ocorreu
        Caso o erro tenha uma página associada, recupera essa página e envia ela na resposta
        Caso não tenha, formata a resposta de erro em JSON e retorna isso no corpo da mensagem
        
        Recebe 
            [ServerConfig] serverConfig: Dados de configuração do servidor
        
        Retona:
            Nada
        """
        
        log.info(f"Processando resposta de erro {self.responseCode}")

        # Apenas três dos erros que posso retornar tem uma página associada, então verifico se o erro que estou processando é um destes
        # Se sim, recupero a página
        # Se não, carrego a msg de erro em JSON
        
        # sanity
        #   ||
        #   \/
        if int(self.responseCode) in [403, 404,418, 500]:
            
            log.info(f"Recuperando página de erro associada ao erro {self.responseCode}")
            
            # A página de erro é chamada de {código-erro}.html e se encontra dentro da pasta de erros, que por sua vez está dentro da pasta raiz de conteúdo
            errorPath = serverConfig.configValue["contentRoot"] + serverConfig.configValue["errorPath"] + str(self.responseCode) + ".html"
            self.body = ContentHandler.get_resource(errorPath, serverConfig) #type: ignore Linter estava reclamando dos tipos pois get_resource pode retornar bytes, isso nunca vai ocorrer nessa caso
            
            # Como eu sei que sempre vou retornar uma página HTML, posso definir rigidamente esses valores
            self.headers["Content-Lenght"] = len(self.body.encode("utf-8"))
            self.headers["Content-Type"]   = self.MIMEContentTypes["html"] + "; charset=utf-8"
            
            return 
        
        log.info(f"Processando mensagem JSON associada ao erro {self.responseCode}")
        
        self.body  = f"{{\"error\": {json.dumps(self.responseCode)}}}\n"
        self.body += f"{{\"message\": {json.dumps(self.problem, ensure_ascii=False)}}}"
        
        # Arrumando headers
        self.headers["Content-Type"]   = "application/json"
        self.headers["Content-Lenght"] = len(self.body.encode("utf-8"))

    def formatResponse(self) -> bytes:
        """
        Método que vai formatar os dados a serem retornados no formato adequado para uma resposta HTTP
        Todos os dados necessários para a resposta já estão dentro do objeto, logo basta recuperar eles e formatá-los
        
        Recebe:
            Nada
            
        Retorna:
            A resposta formatada codificada em bytes
        """
        resposeFirstLine = f"{self.version} {self.responseCode} {self.responseMsg}\r\n".encode("utf-8")
        
        responseHeaders  = bytearray()
        for header, value in self.headers.items():
            responseHeaders += f"{header}: {value}\r\n".encode("utf-8")
        
        crlf = "\r\n".encode("utf-8")
        responseBody = self.body.encode("utf-8") + "\r\n".encode("utf-8")

        response = resposeFirstLine + responseHeaders + crlf + responseBody
        
        return response
     
    def printHead(self) -> str:
        """
        Esse método serve como alternativa ao __str__ para casos onde o corpo da msg é binário que não foi codificado a partir da uma string
        Ou casos onde não quero ver o corpo da msg, apenas os cabeçalhos (por exemplo para imprimir no log)
        
        Recebe:
            Nada
        
        Retorna:
            String contendo a primeira linha e o cabeçalho da respostas
        """
        resposeFirstLine = f"{self.version} {self.responseCode} {self.responseMsg}\n"
        responseHeaders  = str()
        for header, value in self.headers.items():
            responseHeaders += f"{header}: {value}\n"
        
        return resposeFirstLine + responseHeaders + f"ID: {self.id}\n"

class Response(ABC):
    """
    Classe abstrata que representa respostas HTTP
    No seu construtor recebe a requisição para qual tem que responder e extrai os dados relevantes
    A resposta que é gerada depende do tipo de método na requisição
    Tendo gerado uma resposta, o método prepareResponse irá preparar preparar todos os dados que serão enviada ao cliente como a resposta
        Cada subclasse tem uma implementação específica desse método
        Cada implementação prepara os headers e o corpo da mensagem dependo da requisição feita pelo cliente
    Tendo preparado a resposta, o método formatResponse irá formatar os dados da resposta numa string que pode ser enviada para o cliente
    """
    
    # Uma resposta HTTP tem os mesmos três componentes que uma requisição
        # O corpo e o cabeçalho operam da mesma maneira
        # O formato da primeira linha é diferente:
            # <VERSÃO-PROTOCOLO> <CÓDIGO-RESPOSTA> <MENSAGEM-RESPOSTA>
        # Como esse servidor é muito simples, irei responder com a mesma versão que o cliente pediu
    def __init__(self, clientRequest:Request, serverConfig:ServerConfig, responseCodes:dict[Any,Any], contentTypes: dict[Any,Any], id: int) -> None:
        # Recuperando dados da requisição
        self.method   = clientRequest.method
        self.resource = clientRequest.resource
        self.version  = clientRequest.version
        
        # Inicializando código e mensagem de resposta
        self.responseCode = 100
        self.responseMsg: str
        
        # Inicializando os headers da resposta
        self.headers                   = dict()
        self.headers["Server"]         = serverConfig.configValue["serverName"]
        self.headers["Date"]           = formatdate(timeval=None, localtime=False, usegmt=True)
        self.headers["Connection"]     = "close" # Não é usual fechar a conexão depois de toda msg, mas o protocolo permite
        self.headers["Content-Type"]   = "text/plain; charset=utf-8" # Valor padrão, muda dependendo do que está sendo retornado
        self.headers["Content-Lenght"] = 0 # Valor padrão, será calculado quando o conteúdo da resposta for determinado
        
        # Inicializando o corpo da resposta
        self.body: Union[str, bytes, None] # Preciso do None dentro do Union no caso da resposta de HEAD
        # Parâmetro que indica se o corpo da mensagem é binário ou texto
        self.contentIsBinary = False
        
        # Carregando alguns metadados
        self.HTTPResponseCodes = responseCodes
        self.MIMEContentTypes  = contentTypes
    
        # Identificando a resposta
        self.id = id
    
    @staticmethod
    def createResponse(clientRequest:Request, serverConfig:ServerConfig, responseCodes:dict[Any,Any], contentTypes: dict[Any,Any], id: int):
        """
        Método fábrica que retorna as subclasses específicas para cada tipo de resposta que será enviada pelo servidor
        Esse método é estático, ou seja, pode ser chamado sem instanciar a classe, é carregado em tempo de compilação
        TODO: Terminar de documentar você
        TODO: Anotar tipo de retorno, ver https://stackoverflow.com/questions/46007544/python-3-type-hint-for-a-factory-method-on-a-base-class-returning-a-child-class
        """
        # Switch case do Python 
        match clientRequest.method:
            
            case "GET":
                return GetResponse(clientRequest, serverConfig, responseCodes, contentTypes, id)
            
            case "HEAD":
                return HeadResponse(clientRequest, serverConfig, responseCodes, contentTypes, id)
            
            case "OPTIONS":
                return OptionsResponse(clientRequest, serverConfig, responseCodes, contentTypes, id)
            
            case _ :
                log.error("Aconteceu algo de muito errado no método createResponse")
                raise Exceptions.InternalError("Erro ao determinar qual resposta ser criada!")
    
    @abstractmethod
    def prepareResponse(self, serverConfig:ServerConfig) -> None:
        """
        Método abstrato cuja implementação nas subclasses prepara a resposta a ser enviada ao cliente
        Dependendo do método utilizado pelo cliente, o conteúdo da resposta varia
        Esse método não gera a mensagem em formato texto que será enviada ao cliente, mas processa todos os dados necessários para gerar ela
        
        Recebe 
            [ServerConfig] serverConfig: Dados de configuração do servidor
            
        Retorna:
            Nada
        """
        pass
    
    def formatResponse(self) -> bytes:
        """
        Método que vai formatar os dados a serem retornados no formato adequado para uma resposta HTTP
        Todos os dados necessários para a resposta já estão dentro do objeto, logo basta recuperar eles e formatá-los
        
        Recebe:
            Nada
            
        Retorna:
            A resposta formatada codificada em bytes
        """
        resposeFirstLine = f"{self.version} {self.responseCode} {self.responseMsg}\r\n".encode("utf-8")
        
        responseHeaders  = bytearray()
        for header, value in self.headers.items():
            responseHeaders += f"{header}: {value}\r\n".encode("utf-8")
        
        crlf = "\r\n".encode("utf-8")
        if self.contentIsBinary:
            # Novamente linter reclamando que não consegue inferir tipos aqui
            responseBody = self.body + "\r\n".encode("utf-8") #type: ignore
        else:
            responseBody = self.body.encode("utf-8") + "\r\n".encode("utf-8") #type: ignore

        response = resposeFirstLine + responseHeaders + crlf + responseBody
        
        return response
    
    def printHead(self) -> str:
        """
        Esse método serve como alternativa ao __str__ para casos onde o corpo da msg é binário que não foi codificado a partir da uma string
        Ou casos onde não quero ver o corpo da msg, apenas os cabeçalhos (por exemplo para imprimir no log)
        
        Recebe:
            Nada
        
        Retorna:
            String contendo a primeira linha e o cabeçalho da respostas
        """
        resposeFirstLine = f"{self.version} {self.responseCode} {self.responseMsg}\n"
        responseHeaders  = str()
        for header, value in self.headers.items():
            responseHeaders += f"{header}: {value}\n"
        
        return resposeFirstLine + responseHeaders + f"ID: {self.id}\n"
    
    def __str__(self) -> str:
        if self.contentIsBinary:
            log.warning("Chamando __str__ de requisição onde o conteúdo retornado são dados binários!")
        return self.formatResponse().decode().replace("\r", "")

class GetResponse(Response):
    
    def __init__(self, clientRequest: Request, serverConfig: ServerConfig, responseCodes: dict[Any, Any], contentTypes: dict[Any, Any], id: int) -> None:
        super().__init__(clientRequest, serverConfig, responseCodes, contentTypes, id)

    def prepareResponse(self, serverConfig:ServerConfig) -> None:
        """
        Método que prepara a resposta para uma requisição GET
        Uma requisição GET retorna um recurso presente no servidor, usando alguma codificação pré-definida
        Nesse caso, estarei retornando apenas arquivos HTML/CSS codificado como UTF-8
        
        Recebe 
            [ServerConfig] serverConfig: Dados de configuração do servidor
        
        Retona:
            Nada
        """
        
        log.info("Processando requisição GET")
        
        # Calculando o caminho do recurso a ser acessado
        path = serverConfig.configValue["contentRoot"] + self.resource
        
        try:
            # Caso esteja procurando por uma pasta, concateno index.html no final do caminho
            # para procurar o arquivo html nessa pasta
            if path.endswith("/"):
                path += "index.html"
            
            fileContents = ContentHandler.get_resource(path, serverConfig)
        except FileNotFoundError:
            log.error(f"Arquivo não encontrado {self.resource}")
            raise Exceptions.NotFound("Arquivo não encontrado.", self.resource)
        except OSError:
            log.error(f"Erro ao recuperar recurso {self.resource}")
            raise Exceptions.InternalError(f"Erro ao recuperar recurso {self.resource}.")
        except Exception as e:
            # Caso qualquer outro problema tenho acontecido, levanto um 418
            # TODO: Pensar qual seria a melhor exceção para ser levantada aqui
            log.critical(f"Exceção {type(e)} não capturada.")
            raise Exceptions.ImTeapot("Exceção Não Capturada.")
        
        # Tendo recuperado o conteúdo do arquivo, defino ele como o corpo da minha resposta
        self.body = fileContents
        self.contentIsBinary = type(self.body) == bytes
        
        # E arrumo os headers
        if self.contentIsBinary:
            self.headers["Content-Lenght"]   = len(self.body)
            self.headers["Content-Encoding"] = "gzip"
        else:
            self.headers["Content-Lenght"] = len(self.body.encode("utf-8")) #type: ignore
            # Linter estava reclamando do .encode pois não consegue inferir que o tipo de self.body sempre será str nessa branch
        
        # Para arrumar o Content-Type, tenho que descobrir o tipo de arquivo que foi requisitado
        # Para isso, preciso pegar a extensão do recurso requisitado
        requestedFile = path.split("/")[-1] # Retorna uma string
        # Dada a string, separo ela no ponto (.split(".")) e pego o que está depois do ponto ([1])
        fileExt       = requestedFile.split(".")[1]
        # Dada a única extensão, recupero qual o Content-Type associado a ela
        contentType   = self.MIMEContentTypes[fileExt]
        # Caso esteja retornando um arquio texto, indico que ele é codificado com utf-8
        contentType   = contentType if self.contentIsBinary else contentType + "; charset=utf-8"
        
        self.headers["Content-Type"] = contentType
        
        # Por fim, defino o código e msg de retorno
        self.responseCode = 200
        self.responseMsg  = self.HTTPResponseCodes[str(self.responseCode)]["message"]

class HeadResponse(Response):
    
    def __init__(self, clientRequest: Request, serverConfig: ServerConfig, responseCodes: dict[Any, Any], contentTypes: dict[Any, Any], id: int) -> None:
        super().__init__(clientRequest, serverConfig, responseCodes, contentTypes, id)
        
        # Respostas do método HEAD não tem corpo, logo o atributo corpo delas é sempre None nessa subclasse
        self.body            = None
        self.contentIsBinary = False # Não tenho conteúdo então ele não é binário

    def prepareResponse(self, serverConfig:ServerConfig) -> None:
        """
        Método que prepara a resposta para uma requisição HEAD
        Essa requisição retorna o que uma requisição GET retornaria, porém omitindo o corpo da mensagem, contendo apenas os headers
        Logo, para gerar essa resposta, gero a resposta de um GET e removo o corpo da mensagem
        
        Recebe 
            [ServerConfig] serverConfig: Dados de configuração do servidor
            
        Retona:
            Nada
        """
        
        # TODO: Aqui eu só copiei praticamente todo o método de responder um GET, visto que um HEAD é um GET sem corpo de mensagem
        # Certamente tem uma maneira melhor de fazer isso, contudo eu não consigo pensar numa agora
        
        log.info("Processando requisição HEAD")
        
        # Calculando o caminho do recurso a ser acessado
        path = serverConfig.configValue["contentRoot"] + self.resource
        
        try:
            # Caso esteja procurando por uma pasta, concateno index.html no final do caminho
            # para procurar o arquivo html nessa pasta
            if path.endswith("/"):
                path += "index.html"
            
            contentSize = ContentHandler.get_sizeof_resource(path, serverConfig)
        except FileNotFoundError:
            log.error(f"Arquivo não encontrado {self.resource}")
            raise Exceptions.NotFound("Arquivo não encontrado.", self.resource)
        except OSError:
            log.error(f"Erro ao recuperar recurso {self.resource}")
            raise Exceptions.InternalError(f"Erro ao recuperar recurso {self.resource}.")
        except Exception as e:
            # Caso qualquer outro problema tenho acontecido, levanto um 418 e mando o cliente tomar no cu
            # TODO: Pensar qual seria a melhor exceção para ser levantada aqui
            log.critical(f"Exceção {type(e)} não capturada.")
            raise Exceptions.ImTeapot("Exceção Não Capturada.")
        
        # Definindo o tamanho do conteúdo
        self.headers["Content-Lenght"] = contentSize
        
        # Para arrumar o Content-Type, tenho que descobrir o tipo de arquivo que foi requisitado
        # Para isso, preciso pegar a extensão do recurso requisitado
        requestedFile = path.split("/")[-1] # Retorna uma string
        # Dada a string, separo ela no ponto (.split(".")) e pego o que está depois do ponto ([1])
        fileExt       = requestedFile.split(".")[1]
        # Dada a única extensão, recupero qual o Content-Type associado a ela
        contentType   = self.MIMEContentTypes[fileExt]
        # Caso esteja retornando um arquio texto, indico que ele é codificado com utf-8
        contentType   = contentType if self.contentIsBinary else contentType + "; charset=utf-8"
        
        self.headers["Content-Type"] = contentType
        
        # Por fim, defino o código e msg de retorno
        self.responseCode = 200
        self.responseMsg  = self.HTTPResponseCodes[str(self.responseCode)]["message"]
    
    def formatResponse(self) -> bytes:
        """
        Método que vai formatar os dados a serem retornados no formato adequado para uma resposta HTTP
        Todos os dados necessários para a resposta já estão dentro do objeto, logo basta recuperar eles e formatá-los
        
        Recebe:
            Nada
            
        Retorna:
            A resposta formatada codificada em bytes
        """
        resposeFirstLine = f"{self.version} {self.responseCode} {self.responseMsg}\r\n".encode("utf-8")
        
        responseHeaders  = bytearray()
        for header, value in self.headers.items():
            responseHeaders += f"{header}: {value}\r\n".encode("utf-8")
        
        crlf = "\r\n".encode("utf-8")

        response = resposeFirstLine + responseHeaders + crlf
        
        return response

class OptionsResponse(Response):
    
    def __init__(self, clientRequest: Request, serverConfig: ServerConfig, responseCodes: dict[Any, Any], contentTypes: dict[Any, Any], id: int) -> None:
        super().__init__(clientRequest, serverConfig, responseCodes, contentTypes, id)

    def prepareResponse(self, serverConfig:ServerConfig) -> None:
        """
        Método que prepara a resposta para uma requisição OPTIONS
        Essa é a requisição mais simples, pois apenas quer saber quais são os métodos que este servidor aceita
        Nesse caso, apenas GET, HEAD e OPTIONS
        
        Recebe:
            [ServerConfig] serverConfig: Dados de configuração do servidor 
        
        Retona:
            Nada
        """
        
        # Definindo o corpo como uma string de JSON indicando os métodos aceitos
        methods = serverConfig.configValue["implemmentedMethods"]
        self.body = f"{{\"accepted_methods\": {json.dumps(methods)}}}"
        
        # Arrumando headers
        self.headers["Content-Type"]   = "application/json"
        self.headers["Content-Lenght"] = len(self.body.encode("utf-8"))
        
        # Definindo código e mensagem de resposta
        self.responseCode = 200
        self.responseMsg = self.HTTPResponseCodes[str(self.responseCode)]["message"]