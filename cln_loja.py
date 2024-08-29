import grpc
import store_pb2
import store_pb2_grpc
import wallet_pb2
import wallet_pb2_grpc
import sys

def run():
    wallet_id = sys.argv[1]
    wallet_server = sys.argv[2]
    store_server = sys.argv[3]
    wallet_channel = grpc.insecure_channel(f'{wallet_server}')
    store_channel = grpc.insecure_channel(f'{store_server}')
    wallet_stub = wallet_pb2_grpc.WalletServiceStub(wallet_channel)
    store_stub = store_pb2_grpc.StoreServiceStub(store_channel)

    def get_price():
        response = store_stub.GetPrice(store_pb2.PriceRequest())
        print(response.price)

    def buy_product():
        # Get price
        price_response = store_stub.GetPrice(store_pb2.PriceRequest())
        price = price_response.price

        # Create payment order
        order_response = wallet_stub.CreatePaymentOrder(wallet_pb2.PaymentOrderRequest(wallet_id=wallet_id, amount=price))
        order_id = order_response.order_id
        if order_id > 0:
            # Perform the sale
            sell_response = store_stub.Sell(store_pb2.SellRequest(order_id=order_id))
            print(order_response.order_id)
            print(sell_response.status)
        else:
            print(order_response.order_id)

    def shutdown_store():
        shutdown_response = store_stub.Shutdown(store_pb2.ShutdownRequest())
        print(shutdown_response.seller_balance, shutdown_response.pending_orders)

    # Get price of the product
    get_price()

    for line in sys.stdin:
        line = line.strip()
        if line.startswith("C"):
            buy_product()
        elif line.startswith("T"):
            shutdown_store()
            break

if __name__ == '__main__':
    run()
