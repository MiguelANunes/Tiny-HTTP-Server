import logging              # Biblioteca de criação de logs
import Exceptions
import ContentHandler
import json
from email.utils import formatdate
from RequestHandler import Request
from Configuration import ServerConfig # Configurações do Servidor
from typing import Any, Union

"""
ResponseHandler.py
Nesse módulo são definidas e processadas as requisições que são respondidas para o cliente 
O construtor da classe Response recebe uma requisição enviada pelo cliente e cónstroi uma resposta adequada para ela
Como as principais validações são feitas no módulo RequestHandler, não tenho tantas validações para fazer aqui
As validações que são feitas são referentes ao recurso que o cliente quer acessar, isto é, se o recurso existe, se o cliente pode acessar esse recurso, etc.

TODO: Ver https://stackoverflow.com/questions/5938007/what-is-the-difference-between-content-type-charset-x-and-content-encoding-x
"""

log = logging.getLogger("Main.Server.Response")

class Response:
    """
    Classe que representa respostas HTTP
    No seu construtor recebe a requisição para qual tem que responder e extrai os dados relevantes
    A resposta que é gerada depende do tipo de método na requisição
    Tendo gerado uma resposta, o método prepareResponse irá preparar preparar todos os dados que serão enviada ao cliente como a resposta
        Esse método depende de outros três: respondGet, respondHead e respondOptions
        Cada um desses prepara os headers e o corpo da mensagem dependo da requisição feita pelo cliente
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
        self.headers = dict()
        self.headers["Server"]         = serverConfig.configValue["serverName"]
        self.headers["Date"]           = formatdate(timeval=None, localtime=False, usegmt=True)
        self.headers["Connection"]     = "close" # Não é usual fechar a conexão depois de toda msg, mas o protocolo permite
        self.headers["Content-Type"]   = "text/html; charset=utf-8" # Valor padrão, muda dependendo do que está sendo retornado
        self.headers["Content-Lenght"] = 0 # Valor padrão, será calculado quando o conteúdo da resposta for determinado
        
        # Inicializando o corpo da resposta
        self.body: Union[str, bytes]
        # Parâmetro que indica se o corpo da mensagem é binário ou texto
        self.contentIsBinary = False
        
        # Carregando alguns metadados
        self.HTTPResponseCodes = responseCodes
        self.MIMEContentTypes  = contentTypes
    
        # Identificando a resposta
        self.id = id
    
    def respondOptions(self, serverConfig) -> None:
        """
        Método que prepara a resposta para uma requisição OPTIONS
        Essa é a requisição mais simples, pois apenas quer saber quais são os métodos que este servidor aceita
        Nesse caso, apenas GET, HEAD e OPTIONS
        
        Recebe e Retona:
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
    
    def respondHead(self, serverConfig:ServerConfig) -> None:
        """
        Método que prepara a resposta para uma requisição HEAD
        Essa requisição retorna o que uma requisição GET retornaria, porém omitindo o corpo da mensagem, contendo apenas os headers
        Logo, para gerar essa resposta, gero a resposta de um GET e removo o corpo da mensagem
        
        Recebe e Retona:
            Nada
        """
        
        self.respondGet(serverConfig)
        if self.contentIsBinary:
            self.body = bytes()
        else:
            self.body = ""
    
    def respondGet(self, serverConfig:ServerConfig) -> None:
        """
        Método que prepara a resposta para uma requisição GET
        Uma requisição GET retorna um recurso presente no servidor, usando alguma codificação pré-definida
        Nesse caso, estarei retornando apenas arquivos HTML/CSS codificado como UTF-8
        
        Recebe e Retona:
            Nada
        """
        
        # Para determinar o arquivo que será retornado, preciso verificar o caminho que foi passado na requisição
        # Caso seja apenas "/", respondo com Contents/index.html
        # Caso seja algo mais elaborado, abro essa pasta e respondo com o arquivo .html dentro dela
        # Caso algum erro ocorra, lanço erro 404
        
        # Todo o conteúdo possível de ser requisitado está na pasta Content
        # Mais ainda, (eu acho que) todo path possível de ser requisitado começa com "/"
        # Logo, basta concatenar o path requisitado ao final do nome da pasta para abrir aquele path
        
        # TODO: Validar se arquivos podem ser acessados aqui
        
        try:
            # TODO: Lidar com os caminhos aceitos aqui
            
            # Caso esteja procurando pela raiz do site, concateno index.html no final do caminho
            # para procurar o arquivo html raiz do site
            if self.resource == "../Content/":
                path = self.resource + "index.html"
            else:
                path = self.resource
            
            fileContents = ContentHandler.get_resource(path, serverConfig)
        except FileNotFoundError:
            log.error(f"Arquivo não encontrado {self.resource}")
            raise Exceptions.NotFound("Arquivo não encontrado.", self.resource)
        except OSError:
            log.error(f"Erro ao recuperar recurso {self.resource}")
            raise Exceptions.InternalError(f"Erro ao recuperar recurso {self.resource}.")
        except Exception as e:
            # Caso qualquer outro problema tenho acontecido, levanto um 418 e mando o cliente tomar no cu
            log.critical(f"Exceção {type(e)} não capturada.")
            raise Exceptions.ImTeapot("Exceção Não Capturada.")
        
        # Tendo recuperado o conteúdo do arquivo, defino ele como o corpo da minha resposta
        self.body = fileContents
        self.contentIsBinary = type(self.body) == bytes
        
        # E arrumo os headers
        if self.contentIsBinary:
            self.headers["Content-Lenght"] = len(self.body)
        else:
            self.headers["Content-Lenght"] = len(self.body.encode("utf-8")) #type: ignore
            # Linter estava reclamando do .encode pois não consegue inferir que o tipo de self.body sempre será str nessa branch
        
        # Para arrumar o Content-Type, tenho que descobrir o tipo de arquivo que foi requisitado
        # Para isso, preciso pegar a extensão do recurso requisitado
        requestedFile = path.split("/")[-1] # Retorna uma string
        # Dada a única string da lista (requestedFile[0]), separo ela no ponto (.split(".")) e pego o que está depois do ponto ([1]), incluindo o próprio ponto ("."+...)
        fileExt       = requestedFile.split(".")[1]
        # Dada a única extensão, recupero qual o Content-Type associado a ela
        contentType   = self.MIMEContentTypes[fileExt] + "; charset=utf-8"
        
        self.headers["Content-Type"] = contentType
        
        # Por fim, defino o código e msg de retorno
        self.responseCode = 200
        self.responseMsg  = self.HTTPResponseCodes[str(self.responseCode)]["message"]
    
    def respondError(self) -> None:
        pass
    
    def prepareResponse(self, serverConfig:ServerConfig) -> None:
        """
        Método que prepara a resposta a ser enviada ao cliente
        Dependendo do método utilizado pelo cliente, o conteúdo da resposta varia
        Esse método não gera a mensagem em formato texto que será enviada ao cliente, mas processa todos os dados necessários para gerar ela
        
        Recebe e Retorna:
            Nada
        """
        
        # Verificando qual o método utilizado pelo cliente
        if self.method == "GET":
            self.respondGet(serverConfig)
        elif self.method == "HEAD":
            self.respondHead(serverConfig)
        else:
            self.respondOptions(serverConfig)
        
        # Saindo dessas funções tenho tudo que preciso para enviar a resposta ao cliente
        # Porém, deixo para fazer isso em outra função para garantir organização e pegar qualquer possível exceção que apareça
    
    def prepareErrorResponse(self, error:Exception) -> None:
        """
        Método que prepara uma resposta de erro para ser enviada ao cliente
        Dependendo do erro que ocorreu, o conteúdo e código de resposta variam
        Recebe como argumento a exceção que ocorreu para determinar o código de erro a ser enviado
        """
        # TODO: Implementar você
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