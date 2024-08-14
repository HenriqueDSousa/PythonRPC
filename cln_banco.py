import grpc
import wallet_pb2
import wallet_pb2_grpc
import sys

def run():
    wallet_id = sys.argv[1]
    server_address = sys.argv[2]

    channel = grpc.insecure_channel(server_address)
    stub = wallet_pb2_grpc.WalletServiceStub(channel)

    for line in sys.stdin:
        line = line.strip()
        if line.startswith('S'):
            response = stub.GetBalance(wallet_pb2.BalanceRequest(wallet_id=wallet_id))
            print(response.balance)
        elif line.startswith('O'):
            _, amount = line.split()
            response = stub.CreatePaymentOrder(wallet_pb2.PaymentOrderRequest(wallet_id=wallet_id, amount=int(amount)))
            print(response.order_id)
        elif line.startswith('X'):
            _, order_id, amount, dest_wallet = line.split()
            response = stub.Transfer(wallet_pb2.TransferRequest(order_id=int(order_id), amount=int(amount), wallet_id=dest_wallet))
            print(response.status)
        elif line.startswith('F'):
            response = stub.Shutdown(wallet_pb2.ShutdownRequest())
            
            for wallet in response.wallet_statuses:
                print(f'{wallet.wallet_id} {wallet.balance}')
            print(response.pending_orders)
            
            break

if __name__ == '__main__':
    run()