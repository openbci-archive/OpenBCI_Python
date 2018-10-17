from socketIO_client import SocketIO


def on_sample(*args):
    print(args)


socketIO = SocketIO('10.0.1.194', 8880)
socketIO.on('openbci', on_sample)
socketIO.wait(seconds=10)
