import zmq
import time
import sys
import struct

def bind(port = "5557"):
  context = zmq.Context()
  socket = context.socket(zmq.REP)
  socket.bind("tcp://*:%s" % port)
  print "Binding to tcp://*:{}".format(port)
  return socket

def recv(socket):
  try:
    data = socket.recv(flags=zmq.NOBLOCK)
    return data
  except zmq.Again as e:
    return None

def recv_wait(socket):
  while True:
    try:
      data = socket.recv(flags=zmq.NOBLOCK)
      return data
    except zmq.Again as e:
      pass

def send(socket, message):
  return socket.send(message)

def close(socket):
  socket.close()

if __name__ == "__main__":
  socket = bind()
  message = recv_wait(socket)
  print message
  print len(message)
  send(socket, bytearray(struct.pack("d", 5.1)) )
  close(socket)

