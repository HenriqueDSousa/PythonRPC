# Nome dos arquivos .proto
PROTO_FILES = wallet.proto store.proto

# Nome dos arquivos gerados pelo gRPC
GEN_FILES = wallet_pb2.py wallet_pb2_grpc.py store_pb2.py store_pb2_grpc.py

# Comando para gerar os stubs
stubs:
	@if [ ! -f wallet_pb2.py ] || [ ! -f wallet_pb2_grpc.py ] || [ ! -f store_pb2.py ] || [ ! -f store_pb2_grpc.py ]; then \
		python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. $(PROTO_FILES); \
		echo "Stubs generated."; \
	fi

# Comando para limpar os arquivos gerados
clean:
	@files_removed=0; \
	for file in $(GEN_FILES); do \
		if [ -f $$file ]; then \
			rm -f $$file; \
			files_removed=1; \
		fi; \
	done; \
	if [ $$files_removed -eq 1 ]; then \
		echo "Generated files removed."; \
	else \
		echo "No files to clean."; \
	fi
# Regras para rodar os servidores e clientes
run_serv_banco: stubs
	python3 svc_banco.py $(arg1)

run_cli_banco: stubs
	python3 cln_banco.py $(arg1) $(arg2)

run_serv_loja: stubs
	python3 svc_loja.py $(arg1) $(arg2) $(arg3) $(arg4)

run_cli_loja: stubs
	python3 cln_loja.py $(arg1) $(arg2) $(arg3)

# Comando padrão (gera os stubs)
all: stubs
