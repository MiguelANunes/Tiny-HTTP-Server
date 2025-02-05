from typing import Optional # Anotações de tipo
import os

"""
Arquivo que vai lidar com todas as operações sobre arquivos presentes na pasta Content/

TODO: Esse arquivo só está pegando arquivos .html!!!! 
"""

def get_file_contents(filePath:str) -> str:
    """
    Função que vai receber um caminho para um arquivo dentro da pasta Content/ e vai retornar o 
        conteúdo do arquivo desse arquivo em uma string
    
    Recebe:
        [str] filePath: Caminho para um arquivo na pasta Content/
    
    Retorna:
        String contendo o conteúdo do arquivo em filePath
    """
    
    print(f"Procurando o arquivo {filePath}")
    
    # Começo verificando se o caminho passado termina com .html
    if filePath.endswith(".html"):
        # Se sim, leio esse arquivo e já retorno ele
        with open(filePath) as f:
            fileContents = f.read()
        return fileContents
    
    # Se não, procuro por arquivos .html na pasta atual
    dirContents = os.listdir(filePath)
    files       = []
    for item in dirContents:
        if item.endswith(".html"):
            files.append(item)
    
    if len(files) == 1:
        # Caso tenha apenas um arquivo recupero o conteúdo dele em uma string e retorno essa string
        with open(filePath+files[0]) as f:
            fileContents = f.read()
        return fileContents
    
    # Caso não tenha, testo se tem um index.html
    if "index.html" in files:
        # Se sim, abro ele
        with open(filePath+files[files.index("index.html")]) as f:
            fileContents = f.read()
        return fileContents
    
    # Caso não tenha um index.html, retorna o primeiro .html da lista
    with open(filePath+files[0]) as f:
        fileContents = f.read()
    return fileContents