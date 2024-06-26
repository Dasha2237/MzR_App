from twisted.internet import protocol, reactor


class SimpleServerProtocol(protocol.Protocol):
    def connectionMade(self):
        print("Client connected:", self.transport.getPeer())
        self.transport.write("Welcome to the server!".encode())

    def dataReceived(self, data):
        print("Data received from client:", data.decode())
        response = f"Server received: {data.decode()}"
        self.transport.write(response.encode())

    def connectionLost(self, reason):
        print("Client disconnected:", self.transport.getPeer())

    def sendMessage(self, message):
        self.transport.write(message.encode())


class SimpleServerFactory(protocol.Factory):
    protocol = SimpleServerProtocol

    def startFactory(self):
        print("Server started")

    def stopFactory(self):
        print("Server stopped")


# Настройка и запуск сервера
host = '10.55.30.190'
port = 8000
def startServer(host, port):
    factory = SimpleServerFactory()
    reactor.listenTCP(port, factory, interface=host)
    print(f"Server listening on {host}:{port}")
    reactor.run()

startServer(host, port)