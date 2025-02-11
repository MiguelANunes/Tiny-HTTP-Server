import selectors
import socket

"""
Exemplo da documentação do Python
https://docs.python.org/3/library/selectors.html#module-selectors
Outros recursos
https://mathspp.com/blog/til/022
https://pymotw.com/3/selectors/index.html
https://www.reddit.com/r/learnpython/comments/j82di8/cant_understand_select_and_selector_modules/
Outro
https://stackoverflow.com/questions/11591054/python-how-select-select-works
"""

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()

sock = socket.socket()
sock.bind(('localhost', 1234))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

i = 0

while True:
    events = sel.select()
    
    print(f"events: {events}", end="\n\n")
    for key, mask in events:
        
        print(f"key: {key}", end="\n\n")
        print(f"key.fileobj: {key.fileobj}", end="\n\n")
        
        callback = key.data
        callback(key.fileobj, mask)