import grpc
from concurrent import futures
import wallet_pb2
import wallet_pb2_grpc
import threading
import sys

class WalletService(wallet_pb2_grpc.WalletServiceServicer):
    def __init__(self, server, stop_event):
        self.wallets = {}
        self.orders = {}
        self.next_order_id = 1
        self.server = server
        self._stop_event = stop_event  

    def load_wallets(self):
        for line in sys.stdin:
            wallet_id, balance = line.strip().split()
            self.wallets[wallet_id] = int(balance)

    def GetBalance(self, request, context):
        wallet_id = request.wallet_id
        balance = self.wallets.get(wallet_id, -1)
        return wallet_pb2.BalanceResponse(balance=balance)

    def CreatePaymentOrder(self, request, context):
        wallet_id = request.wallet_id
        amount = request.amount

        if wallet_id not in self.wallets:
            return wallet_pb2.PaymentOrderResponse(order_id=-1)

        if self.wallets[wallet_id] < amount:
            return wallet_pb2.PaymentOrderResponse(order_id=-2)

        order_id = self.next_order_id
        self.next_order_id += 1
        self.wallets[wallet_id] -= amount
        self.orders[order_id] = amount

        return wallet_pb2.PaymentOrderResponse(order_id=order_id)

    def Transfer(self, request, context):
        order_id = request.order_id
        amount = request.amount
        wallet_id = request.wallet_id

        if order_id not in self.orders:
            return wallet_pb2.TransferResponse(status=-1)

        if self.orders[order_id] != amount:
            return wallet_pb2.TransferResponse(status=-2)

        if wallet_id not in self.wallets:
            return wallet_pb2.TransferResponse(status=-3)

        self.wallets[wallet_id] += amount
        del self.orders[order_id]

        return wallet_pb2.TransferResponse(status=0)

    def Shutdown(self, request, context):
        pending_orders = len(self.orders)
        wallet_statuses = [wallet_pb2.Wallet(wallet_id=k, balance=v) for k, v in self.wallets.items()]

        
        keys = self.wallets.keys()
        for key in keys:
            print(f'{key} {self.wallets[key]}')
        
        self._stop_event.set()
        return wallet_pb2.ShutdownResponse(pending_orders=pending_orders, wallet_statuses=wallet_statuses)

def serve():
    port = int(sys.argv[1])
    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    wallet_service = WalletService(server, stop_event)
    wallet_service.load_wallets()
    wallet_pb2_grpc.add_WalletServiceServicer_to_server(wallet_service, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    stop_event.wait()
    server.stop(grace=1)   

if __name__ == '__main__':
    serve()
