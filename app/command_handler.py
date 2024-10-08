from typing import Tuple, Any
from app.resp import deserialize, serialize, SIMPLE_STRING, BULK_STRING, ERROR, INTEGER, ARRAY
from app.store import Store

def command_dispatcher(data: bytes, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int, bool]:
    """
    function that takes in a request as input, deserializes it, and then dispatches it to the appropriate handler
    """
    COMMAND_HANDLER_MAP = {
        "PING": handle_ping,
        "ECHO": handle_echo,
        "SET": handle_set,
        "GET": handle_get,
        "INFO": handle_info,
        "REPLCONF": handle_repl_conf,
        "PSYNC": handle_psync
    }
    # Deserialize the request
    deserialized_data = deserialize(data)
    command = deserialized_data[0]

    return COMMAND_HANDLER_MAP[command](deserialized_data, store, server_details)

def handle_ping(data: list, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int]:
    return serialize("PONG"), store, 0, False

def handle_echo(data: list, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int]:
    message = data[1]
    return serialize(message), store, 0, False

def handle_set(data: list, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int]:
    # get key and value from data
    _, key, value = data[0], data[1], data[2]
    px = None
    if len(data) > 3 and data[3].lower() == 'px':
        px = int(data[4])
    new_store = store.set(key, value, px)
    return serialize("OK"), new_store, 0, True

def handle_get(data: list, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int]:
    _, key = data    
    value = store.get(key)
    return serialize(value if value is not None else None), store, 0, False

def handle_info(data: list, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int]:
    command, _ = data
    if command.lower() == 'info':
        # determine if master or replica
        role = "master" if not server_details.get("REPLICAOF") else "slave"
        master_replid = server_details.get("master_replid")
        master_repl_offset = server_details.get("master_repl_offset")
        return serialize(f"role:{role}\nmaster_replid:{master_replid}\nmaster_repl_offset:{master_repl_offset}"), store, 1, False
    return None, store, 0, False

def handle_repl_conf(data: list, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int]:
    command = data[0]
    listening_port = data[2]
    if command == "REPLCONF":
        return serialize("OK"), store, 0, False
    return None, store, 0, False

def handle_psync(data: list, store: Store, server_details: dict[str, Any]) -> Tuple[bytes, Store, int]:
    command = data[0]
    if command == "PSYNC":
        master_replid = server_details.get("master_replid")
        response = f"FULLRESYNC {master_replid} 0"
        return serialize(response), store, 1, False
    return None, store, 1, False

