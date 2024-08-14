import grpc
from concurrent import futures
import wallet_pb2
import wallet_pb2_grpc
import store_pb2
import store_pb2_grpc
import threading
import sys

class StoreService(store_pb2_grpc.StoreServiceServicer):
    def __init__(self, wallet_channel, wallet_id, server, stop_event):
        self.price = int(sys.argv[1])
        self.port = int(sys.argv[2])
        self.wallet_id = wallet_id
        self.wallet_channel = wallet_channel
        self.wallet_stub = wallet_pb2_grpc.WalletServiceStub(wallet_channel)
        self.seller_balance = self.get_seller_balance()
        self.server = server
        self._stop_event = stop_event

    def get_seller_balance(self):
        response = self.wallet_stub.GetBalance(wallet_pb2.BalanceRequest(wallet_id=self.wallet_id))
        return response.balance

    def GetPrice(self, request, context):
        return store_pb2.PriceResponse(price=self.price)

    def Sell(self, request, context):
        order_id = request.order_id
        try:
            response = self.wallet_stub.Transfer(wallet_pb2.TransferRequest(
                order_id=order_id,
                amount=self.price,
                wallet_id=self.wallet_id
            ))
            response = store_pb2.SellResponse(status=response.status)
            
            if(response.status == 0):
                self.seller_balance += self.price

            return response

        except grpc.RpcError as e:
            return store_pb2.SellResponse(status=-9)

    def Shutdown(self, request, context):
        # Send shutdown request to wallet server
        try:
            response = self.wallet_stub.Shutdown(wallet_pb2.ShutdownRequest())
            pending_orders = response.pending_orders
            # Report final balance
            final_balance = self.seller_balance
            
            self._stop_event.set()

            return store_pb2.ShutdownResponse(
                seller_balance=final_balance,
                pending_orders=pending_orders
            )
           
        except grpc.RpcError as e:
            return store_pb2.ShutdownResponse(
                seller_balance=self.seller_balance,
                pending_orders=-9
            )

def serve():
    port = int(sys.argv[2])
    wallet_server = sys.argv[4]
    wallet_channel = grpc.insecure_channel(f'{wallet_server}')
    wallet_id = sys.argv[3]

    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_service = StoreService(wallet_channel, wallet_id, server, stop_event)
    store_pb2_grpc.add_StoreServiceServicer_to_server(store_service, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Store server running on port {port}")
    stop_event.wait()
    server.stop(grace=1)

if __name__ == '__main__':
    serve()
