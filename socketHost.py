from twisted.internet import protocol, reactor

class SimpleServerProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.clients.append(self)
        print("Client connected:", self.transport.getPeer())
        self.transport.write("Welcome to the server!".encode())

    def dataReceived(self, data):
        print("Data received from client:", data.decode())
        response = f"Server received: {data.decode()}"
        self.transport.write(response.encode())

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        print("Client disconnected:", self.transport.getPeer())

    def sendMessage(self, message):
        self.transport.write(message.encode())

class SimpleServerFactory(protocol.Factory):
    protocol = SimpleServerProtocol

    def __init__(self):
        self.clients = []

    def startFactory(self):
        print("Server started")

    def stopFactory(self):
        print("Server stopped")

    def broadcastMessage(self, message):
        for client in self.clients:
            client.sendMessage(message)

# Setup and start the server
host = '192.168.56.1'
port = 8000

def startServer(host, port):
    factory = SimpleServerFactory()
    reactor.listenTCP(port, factory, interface=host)
    print(f"Server listening on {host}:{port}")
    reactor.run()

startServer(host, port)
