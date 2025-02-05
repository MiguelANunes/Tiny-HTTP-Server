from typing import Optional # Anotações de tipo
import Exceptions

"""
Arquivo onde é definida a classe de requisições HTTP
TODO: Melhorar essa descrição
"""

class Request:
    
    """
    Classe que representa uma requisição HTTP
    No seu construtor recebe os componentes da requisição -- primeira linha, cabeçalhos e corpo -- como strings
    No caso do cabeçalho, uma string que pode conter várias substrings, cada uma delimitada por "\r\n" ou "\n"
    
    O construtor dessa classe processa essas strings para obter as informações necessárias para responder a requisição,
        levantando exceções quando necessário
        
    Atributos da Classe:
        [str]            method:  O método HTTP na requisição
        [str]            path:    Caminho do recurso requisitado
        [str]            version: A versão do protocolo HTTP da requisição
        [dict(str, str)] headers: Os cabeçalhos presentes na requisição
        [str]            body:    O corpo da requisição
        
    Métodos da Classe:
        __init__: Construtor da classe
        TODO: Métodos para processar os cabeçalhos e métodos para processar o corpo
    """
    
    # Uma requisição HTTP tem três componentes
        # A primeira linha, cujo formato é
            # <METODO> <CAMINHO-RECURSO> <VERSÃO-PROTOCOLO>
        # Uma lista de cabeçalhos
        # Um corpo (opcional)
    def __init__(self, firstLine:str, headers:str, body:Optional[str]) -> None:
        # Não lidarei com requisições que tem corpo aqui, então só copio para o objeto e é isso
        self.body = body
        
        # Recuperando as informações da primeira linha
        # A primeira linha da requisição sempre terá 3 componentes, separados por espaços
        # Portanto é seguro fazer essa operação
        # De qualquer forma, irei fazer uma validação no input
        try:
            self.method, self.path, self.version = firstLine.split() # Aqui estou assumindo que o whitespace no final da primeira linha já foi removido
        except ValueError:
            raise Exceptions.BadRequest("Requisição Mal Formada!", Exceptions.ProblemComponent.METHOD ,firstLine)

        # Verificando se o método utilizado é suportado
        supportedMethods = [str(x.value) for x in Exceptions.ImplementedMethods]
        if self.method not in supportedMethods:
            raise Exceptions.MethodNotImplemented("Método Não Implementado!", self.method)

        # Verificando se o caminho requisitado é válido
        # TODO: Fazer nova validação aqui para garantir que está requisitando um caminho que existe
        forbiddenPaths = [str(x.value) for x in Exceptions.ForbiddenPaths]
        for path in forbiddenPaths:
            if path in self.path:
                raise Exceptions.Forbidden("Recurso Proibido de ser Acessado!", self.path)

        # Verificando se a versão do HTTP passada na requisição é válida
        supportedVersions = [str(x.value) for x in Exceptions.HTTPVersion]
        if self.version not in supportedVersions:
            raise Exceptions.VersionNotSupported("Versão do Protocolo HTTP Não Suportada", self.version)

        # Recuperando os headers da requisição
        # Os headers tem formato "header: value"
        # Cada header está em uma única linha
        # Portanto, basta iterar pelas linhas da string recebida no construtor e colocar cada par em um dict
        self.headers = dict()
        for header in headers.splitlines():
            if header == "": # Isso me deu muita dor de cabeça
                continue
            try:
                k, v = header.split(":", 1) # Separando a string em cada ":" e apenas uma vez, para evitar que argumentos que tenha ":" sejam separados tbm
            except ValueError:
                # sanity
                raise Exceptions.BadRequest("Requisição Mal Formatada!", Exceptions.ProblemComponent.HEADER, header)
            
            self.headers[k] = v