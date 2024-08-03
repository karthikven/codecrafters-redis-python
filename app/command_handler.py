from typing import Tuple
from app.resp import deserialize, serialize, SIMPLE_STRING, BULK_STRING, ERROR, INTEGER, ARRAY
from app.store import Store

def command_dispatcher(data: bytes, store: Store) -> Tuple[bytes, Store]:
    """
    function that takes in a request as input, deserializes it, and then dispatches it to the appropriate handler
    """
    COMMAND_HANDLER_MAP = {
        "PING": handle_ping,
        "ECHO": handle_echo,
        "SET": handle_set,
        "GET": handle_get
    }

    # Deserialize the request
    deserialized_data = deserialize(data)
    command = deserialized_data[0]

    return COMMAND_HANDLER_MAP[command](deserialized_data, store)

def handle_ping(data: list, store) -> Tuple[bytes, Store]:
    return serialize("PONG"), store

def handle_echo(data: list, store: Store) -> Tuple[bytes, Store]:
    message = data[1]
    return serialize(message), store

def handle_set(data: list, store: Store) -> Tuple[bytes, Store]:
    # get key and value from data
    _, key, value = data
    new_store = store.set(key, value)
    return serialize("OK"), new_store

def handle_get(data: list, store: Store) -> Tuple[bytes, Store]:
    _, key = data
    value = store.get(key)
    return serialize(value if value is not None else None), store 

