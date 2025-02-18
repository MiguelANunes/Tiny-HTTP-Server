# migs' Tiny HTTP Server

Uma implementação quase [minimal](https://pt.wikipedia.org/wiki/Elemento_minimal) de um servidor HTTP em Python.

Aceita apenas requisições GET, HEAD e OPTIONS, lidando apenas com poucas conexões de cada vez e retorna uma versão (ainda mais) estática do  [meu blog](https://miguelanunes.github.io).

Erros são respondidos com as mensagens de erro apropriadas e, em alguns casos, uma página HTML correspondente a mensagem de erro é enviada ao cliente.

Meu objetivo com esse servidor é apenas me divertir e estudar, então terão bugs, coisas incompletas e TODOs, mas espero com o tempo chegar em um estado estável com ele.
