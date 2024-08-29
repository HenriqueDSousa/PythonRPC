PROTO_FILES = wallet.proto store.proto

GEN_FILES = wallet_pb2.py wallet_pb2_grpc.py store_pb2.py store_pb2_grpc.py

stubs:
	@python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. $(PROTO_FILES)

clean:
	@rm -f $(GEN_FILES)

run_serv_banco: stubs
	@python3 svc_banco.py $(arg1)

run_cli_banco: stubs
	@python3 cln_banco.py $(arg1) $(arg2)

run_serv_loja: stubs
	@python3 svc_loja.py $(arg1) $(arg2) $(arg3) $(arg4)

run_cli_loja: stubs
	@python3 cln_loja.py $(arg1) $(arg2) $(arg3)

all: clean stubs
