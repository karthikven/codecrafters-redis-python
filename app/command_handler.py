from typing import Tuple
from app.resp import deserialize, serialize, SIMPLE_STRING, BULK_STRING, ERROR, INTEGER, ARRAY
from app.store import Store
import time

def command_dispatcher(data: bytes, store: Store, replicaof: str) -> Tuple[bytes, Store]:
    """
    function that takes in a request as input, deserializes it, and then dispatches it to the appropriate handler
    """
    COMMAND_HANDLER_MAP = {
        "PING": handle_ping,
        "ECHO": handle_echo,
        "SET": handle_set,
        "GET": handle_get,
        "INFO": handle_info
    }

    # determine if master or replica
    role = "master"
    if replicaof:
        role = "slave"
    # Deserialize the request
    deserialized_data = deserialize(data)
    command = deserialized_data[0]

    return COMMAND_HANDLER_MAP[command](deserialized_data, store, role)

def handle_ping(data: list, store: Store, role: str) -> Tuple[bytes, Store]:
    return serialize("PONG"), store

def handle_echo(data: list, store: Store, role: str) -> Tuple[bytes, Store]:
    message = data[1]
    return serialize(message), store

def handle_set(data: list, store: Store, role: str) -> Tuple[bytes, Store]:
    # get key and value from data
    _, key, value = data[0], data[1], data[2]
    px = None
    if len(data) > 3 and data[3].lower() == 'px':
        px = int(data[4])
    new_store = store.set(key, value, px)
    return serialize("OK"), new_store

def handle_get(data: list, store: Store, role: str) -> Tuple[bytes, Store]:
    _, key = data    
    value = store.get(key)
    return serialize(value if value is not None else None), store 

def handle_info(data: list, store: Store, role: str) -> Tuple[bytes, Store]:
    command, _ = data
    if command.lower() == 'info':
        return serialize(f"role:{role}"), store
    return None, store