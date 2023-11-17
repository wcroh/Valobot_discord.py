import socket
import os
import time


class HealthCheckServer(object):
    """ Simple TCP server to allow for TCP health checks.
    """

    def __init__(self, ip='0.0.0.0', port=8000, handle_method=None,
                 log=False, retry_count=5):

        super(HealthCheckServer, self).__init__()

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.log = log
        self.retry_count = retry_count
        self.current_try_count = 0

        if handle_method is None:
            self.handle_method = self.default_handle_method
        else:
            self.handle_method = handle_method

    def default_handle_method(self):
        """ Simple handle method that accepts the connection then closes.
        """
        while True:
            if self.log:
                print("Waiting for a connection")

            connection, client_address = self.sock.accept()
            try:
                if self.log:
                    print("Client connected: {0}".format(client_address))
            finally:
                connection.close()

    def start(self):
        server_address = (self.ip, self.port)

        if self.log:
            print("Starting health server on {0} port {1}"
                  .format(server_address[0], server_address[1]))

        if self.current_try_count > self.retry_count:
            if self.log:
                print("Unable to start health server on {0} port {1}"
                      .format(server_address[0], server_address[1]))
            return

        try:
            self.current_try_count = self.current_try_count + 1
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(server_address)
            self.sock.listen(1)
            self.default_handle_method()
        except socket.error:
            if self.log:
                print("Unable to start health server...retrying in 5s.")
            time.sleep(5)
            self.start()
        except Exception as e:
            print("Unable to start health server due to unknown exception {0}"
                  .format(e))


if __name__ == '__main__':
    """ For now, if executed as main, simply run default server with just logging enabled
    """

    server = HealthCheckServer(log=True)
    server.start()