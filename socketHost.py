from twisted.internet import protocol, reactor

class SimpleServerProtocol(protocol.Protocol):
    def connectionMade(self):
        print(len(self.factory.clients))
        self.factory.clients.append(self)
        print("Client connected:", self.transport.getPeer())
        self.transport.write("Welcome to the server!\n".encode())

    def dataReceived(self, data):
        message = data.decode()
        print("Data received from client:", message)
        # Broadcast the message to all connected clients

        self.factory.broadcastMessage(data)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        print("Client disconnected:", self.transport.getPeer())

    def sendMessage(self, message):
        self.transport.write(message)

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
            print(client)
            client.sendMessage(message + b'\n')

# Setup and start the server
host = '127.0.0.1'
port = 8000

def startServer(host, port):
    factory = SimpleServerFactory()
    reactor.listenTCP(port, factory, interface=host)
    print(f"Server listening on {host}:{port}")
    reactor.run()

startServer(host, port)
