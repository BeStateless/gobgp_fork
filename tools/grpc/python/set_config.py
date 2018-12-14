import gobgp_pb2_grpc
import gobgp_pb2
import sys

import grpc
from grpc.framework.interfaces.face.face import ExpirationError

_TIMEOUT_SECONDS = 1


def run():
    channel1 = grpc.insecure_channel('192.168.100.2:50051')
    stub1 = gobgp_pb2_grpc.GobgpApiStub(channel1)
    channel2 = grpc.insecure_channel('192.168.100.3:50051')
    stub2 = gobgp_pb2_grpc.GobgpApiStub(channel2)
    try:
        reply = stub1.GetNeighbor(gobgp_pb2.GetNeighborRequest())
        print("GoBGP1 has %d neighbors" % (len(reply.peers)))
        reply = stub2.GetNeighbor(gobgp_pb2.GetNeighborRequest())
        print("GoBGP2 has %d neighbors" % (len(reply.peers)))

        # Set config 1
        config1 = '[global.config]\nas = 2222\nrouter-id = "192.168.100.2"\n[[neighbors]]\n[neighbors.config]\npeer-as = 3333\nneighbor-address = "192.168.100.3"'
        try:
            reply = stub1.SetConfig(gobgp_pb2.SetConfigRequest(config=config1,config_format=gobgp_pb2.SetConfigRequest.TOML))
        except grpc.RpcError as e:
            print e.details()
            status_code = e.code()
            print status_code.name
            print status_code.value

        # Set config 2
        config2 = '[global.config]\nas = 3333\nrouter-id = "192.168.100.3"\n[[neighbors]]\n[neighbors.config]\npeer-as = 2222\nneighbor-address = "192.168.100.2"'
        try:
            reply = stub2.SetConfig(gobgp_pb2.SetConfigRequest(config=config2, config_format=gobgp_pb2.SetConfigRequest.TOML))
        except grpc.RpcError as e:
            print e.details()
            status_code = e.code()
            print status_code.name
            print status_code.value

        # Set a bogus config
        config3 = 'this config is bogus.exe'
        try:
            reply = stub2.SetConfig(gobgp_pb2.SetConfigRequest(config=config3, config_format=gobgp_pb2.SetConfigRequest.TOML))
        except grpc.RpcError as e:
            print e.details()
            status_code = e.code()
            print status_code.name
            print status_code.value

        reply = stub1.GetNeighbor(gobgp_pb2.GetNeighborRequest())
        print("GoBGP1 has %d neighbors" % (len(reply.peers)))
        reply = stub2.GetNeighbor(gobgp_pb2.GetNeighborRequest())
        print("GoBGP2 has %d neighbors" % (len(reply.peers)))
    
    except ExpirationError, e:
        print str(e)
        sys.exit(-1)

if __name__ == '__main__':
    run()
