import logging              # Biblioteca de criação de logs
import ContentHandler
from email.utils import formatdate
from RequestHandler import Request
from Configuration import ServerConfig # Configurações do Servidor
from typing import Any

"""
Arquivo onde é definida a classe de respostas HTTP

TODO: Melhorar essa descrição
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
    def __init__(self, clientRequest:Request, serverConfig:ServerConfig, responseCodes:dict[Any,Any], contentTypes: dict[Any,Any]) -> None:
        # Recuperando dados da requisição
        self.method  = clientRequest.method
        self.path    = "../Content" + clientRequest.path  # TODO: melhorar aqui com caminhos aceitos
        self.version = clientRequest.version
        
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
        self.body: str
        
        # Carregando alguns metadados
        self.HTTPResponseCodes = responseCodes
        self.MIMEContentTypes  = contentTypes
    
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
        self.body = f"{{'accepted_methods': {methods}}}"
        
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
        try:
            # TODO: Lidar com os caminhos aceitos aqui
            
            # Caso esteja procurando pela raiz do site, concateno index.html no final do caminho
            # para procurar o arquivo html raiz do site
            if self.path == "../Content/":
                path = self.path + "index.html"
            else:
                path = self.path
            
            fileContents = ContentHandler.get_file_contents(path, serverConfig)
        except Exception as e:
            # TODO: Lidar com possíveis erros aqui
            return
        
        # Tendo recuperado o conteúdo do arquivo, defino ele como o corpo da minha resposta
        self.body = fileContents
        
        # E arrumo os headers
        self.headers["Content-Lenght"] = len(self.body.encode("utf-8"))
        
        # Para arrumar o Content-Type, tenho que descobrir o tipo de arquivo que foi requisitado
        # Para isso, preciso pegar a extensão do recurso requisitado
        requestedFile = path.split("/")[-1] # Retorna uma string
        # Dada a única string da lista (requestedFile[0]), separo ela no ponto (.split(".")) e pego o que está depois do ponto ([1]), incluindo o próprio ponto ("."+...)
        fileExt       = "."+requestedFile.split(".")[1]
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
        
        pass
    
    def formatResponse(self) -> str:
        """
        Método que vai formatar os dados a serem retornados no formato adequado para uma resposta HTTP
        Todos os dados necessários para a resposta já estão dentro do objeto, logo basta recuperar eles e formatá-los
        
        Recebe:
            Nada
            
        Retorna:
            A string de resposta formatada
        """
        
        resposeFirstLine = f"{self.version} {self.responseCode} {self.responseMsg}\r\n"
        
        responseHeaders  = ""
        for header, value in self.headers.items():
            responseHeaders += f"{header}: {value}\r\n"
        
        crlf = "\r\n"
        responseBody = self.body + "\r\n"

        response = resposeFirstLine + responseHeaders + crlf + responseBody
        
        return response
    
    def __str__(self) -> str:
        return self.formatResponse().replace("\r", "")