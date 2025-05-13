# proto

This directory contains gRPC and protobuf service definitions and generated code for peer synchronization and plugin propagation in Aria-node.

### Files

- **sync.proto**
  - Defines the AriaPeer gRPC service.
  - Messages include:
    - `MemoryEntry`
    - `PluginPush`
    - `SyncMemoryRequest`
    - `SyncMemoryResponse`
    - `HandshakeRequest`
    - `HandshakeResponse`

- **sync_pb2.py / sync_pb2_grpc.py**
  - Auto-generated Python files using `protoc`.
  - `sync_pb2.py` defines message structures.
  - `sync_pb2_grpc.py` provides gRPC client/server stubs.

These files facilitate encrypted peer sync, memory transmission, and plugin injection.
