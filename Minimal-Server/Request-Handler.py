from typing import Optional # Anotações de tipo
import Exceptions

"""
Arquivo onde é definida a classe de requisições HTTP
"""

class Request:
    
    # Uma requisição HTTP tem três componentes
    # A primeira linha, contendo o método, o caminho e a versão do protocolo
    # Uma lista de cabeçalhos
    # Um corpo (opcional)
    def __init__(self, firstLine:str, headers:str, body:Optional[str]) -> None:
        self.firstLine = firstLine # Assumo que a primeira linha já teve o whitespace final removido
        self.body      = body      # Não lidarei com requisições que tem corpo aqui, então só copio para o objeto e é isso
        
        # Recuperando as informações da primeira linha
        # A primeira linha da requisição sempre terá 3 componentes, separados por espaços
        # Portanto é seguro fazer essa operação
        # De qualquer forma, irei fazer uma validação no input
        try:
            self.method, self.path, self.version = self.firstLine.split()
        except ValueError:
            raise Exceptions.BadRequest("Requisição Mal Formada!", Exceptions.ProblemComponent.METHOD ,self.firstLine)

        # Verificando se o método utilizado é suportado
        supportedMethods = [str(x.value) for x in Exceptions.ImplementedMethods]
        if self.method not in supportedMethods:
            raise Exceptions.MethodNotImplemented("Método Não Implementado!", self.method)

        # Verificando se o caminho requisitado é válido
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
        for header in headers:
            try:
                k, v = header.split(":", 1) # Separando a string em cada ":" e apenas uma vez, para evitar que argumentos que tenha ":" sejam separados tbm
            except ValueError:
                raise Exceptions.BadRequest("Requisição Mal Formatada!", Exceptions.ProblemComponent.HEADER, header)
            
            self.headers[k] = v