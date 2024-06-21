import pygame
from twisted.internet import protocol, reactor

ROBOT_DONE = pygame.USEREVENT + 1


class PygameClient(protocol.Protocol):
    def connectionMade(self):
        print("Connected to server")
        self.factory.client = self

    def dataReceived(self, data):
        print("Data received from server:", data.decode())
        event = pygame.event.Event(ROBOT_DONE, message=data.decode())
        pygame.event.post(event)

    def sendMessage(self, message):
        self.transport.write(message.encode())


class PygameClientFactory(protocol.ClientFactory):
    protocol = PygameClient

    def __init__(self):
        self.client = None

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed:", reason)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost:", reason)
        reactor.stop()


def twisted_thread(factory):
    reactor.connectTCP("127.0.0.1", 8000, factory)
    reactor.run(installSignalHandlers=0)