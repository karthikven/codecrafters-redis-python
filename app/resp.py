from typing import Union, List
RESPType = Union[str, int, bytes, List['RESPType'], None]

# constants
SIMPLE_STRING = b'+'
ERROR = b'-'
INTEGER = b':'
BULK_STRING = b'$'
ARRAY = b'*'
CRLF = b'\r\n'

# serialization functions to convert data -> byte strings respecting resp rules
def serialize(data: RESPType) -> bytes:
    """
    serializes data into a byte string following the RESP protocol.
    works by checking the type of data and then sending it to the appropriate serialization function.
    args:
        data (RESPType): The data to be serialized.

    returns:
        bytes: The serialized byte string.
    """
    if isinstance(data, str):
        if data.lower().startswith('err'):
            return serialize_error(data)
        if data.lower() == 'ok' or data.lower() == 'ping':
            return serialize_simple_string(data)
        return serialize_bulk_str(data)
    elif isinstance(data, int):
        return serialize_integer(data)
    elif isinstance(data, list):
        return serialize_array(data)
    elif isinstance(data, bytes):
        return serialize_bulk_str(data.decode('utf-8', errors='replace'))
    elif data == None:
        return serialize_bulk_str(None)
    else:
        raise ValueError(f"Unsupported type for RESP serialization: {type(data)}")
    
def serialize_simple_string(data: str) -> bytes:
    if data not in ["PING", "OK", "PONG"]:
        raise ValueError(f"Unsupported simple string for RESP serialization: {data}")
    encoded_data = data.encode('utf-8')
    return SIMPLE_STRING + encoded_data + CRLF

def serialize_error(data: str) -> bytes:
    encoded_data = data.encode('utf-8')
    return ERROR + encoded_data + CRLF

def serialize_integer(data: int) -> bytes:
    encoded_data = str(data).encode('utf-8')
    return INTEGER + encoded_data + CRLF

def serialize_bulk_str(data: str) -> bytes:
    if data is None:
        return BULK_STRING + b'-1' + CRLF
    encoded_data_len = str(len(data)).encode('utf-8')
    encoded_data = data.encode('utf-8')
    return BULK_STRING + encoded_data_len + CRLF + encoded_data + CRLF

def serialize_array(data: list) -> bytes:
    if not data:
        return ARRAY + b'-1' + CRLF
    encoded_data = ARRAY + str(len(data)).encode('utf-8') + CRLF
    for item in data:
        encoded_data += serialize(item)
    return encoded_data

# helper functions
def read_until_crlf(data: bytes, start: int = 0) -> tuple[bytes, int]:
    index = start + 1
    while index < len(data) - 1:
        if data[index: index+2] == CRLF:
            return [data[start: index+2], index+2]
        index += 1
    return (b'', len(data))

def parse_bulk_string_data_wrapper(data: bytes) -> tuple[bytes, int]:
    start = 0
    # perform two consecutive read_until_crlf calls to get the bulk string
    _, first_crlf_index = read_until_crlf(data, start)
    _, second_crlf_index = read_until_crlf(data, first_crlf_index)
    return (data[start: second_crlf_index], second_crlf_index)


# functions to parse resp byte strings into RESPType datatype
def deserialize(data: bytes) -> RESPType:
    """
    deserializes a byte string into a RESPType datatype, by checking the first byte and then calling the appropriate parsing function.
    args:
        data (bytes): The byte string to be deserialized.
    returns:
        RESPType: The deserialized data.
    """
    if not data:
        raise ValueError('Empty Input Data')

    RESP_PARSER = {
        ord(SIMPLE_STRING): parse_simple_string,
        ord(ERROR): parse_error,
        ord(INTEGER): parse_integer,
        ord(BULK_STRING): parse_bulk_string,
        ord(ARRAY): parse_array
    }

    parser = RESP_PARSER.get(data[0])

    if not parser:
        raise ValueError(f'Unknown RESPType Indicator: {data[0]}')

    data_to_parse = data
    if data[0] == ord(BULK_STRING):
        data_to_parse, _ = parse_bulk_string_data_wrapper(data)
    return parser(data_to_parse)


def parse_simple_string(data: bytes) -> str:
    data_decode = data.decode('utf-8')
    data_split = data_decode[1:].split("\r\n")
    return data_split[0]

def parse_integer(data: bytes) -> int:
    data_decode = data.decode('utf-8')
    data_split = data_decode[1:].split("\r\n")
    return int(data_split[0])

def parse_error(data: bytes) -> str:
    data_decode = data.decode('utf-8')
    data_split = data_decode[1:].split("\r\n")
    return data_split[0]

def parse_bulk_string(data: bytes) -> str:
    data_decode = data.decode('utf-8')
    data_split_up = data_decode.split("\r\n")
    if data_split_up[0] == '-1':
        return None
    return data_split_up[1]

def parse_array(data: bytes) -> list:
    if data[0] != ord(ARRAY):
        raise ValueError('Input cannot be parsed as an array')
    
    # find the end of the length specification
    length_end = data.index(CRLF)
    length = int(data[1:length_end])

    if length == -1:
        return []
    arr = []
    start_index = length_end + 2

    for _ in range(length):
        element_type = data[start_index]
        if element_type == ord(BULK_STRING):
            to_parse, new_index = parse_bulk_string_data_wrapper(data[start_index:])
            arr.append(deserialize(to_parse))
            start_index += new_index 
        else:
            to_parse, new_index = read_until_crlf(data, start_index)
            arr.append(deserialize(to_parse))
            start_index = new_index
        if start_index >= len(data):
            break
    return arr


def main():
    # write tests for each case
    # test for simple string
    assert deserialize(serialize("PING")) == "PING"
    # test for error
    assert deserialize(serialize("ERR something went wrong")) == "ERR something went wrong"
    # test for integer
    assert deserialize(serialize(123)) == 123
    # # test for bulk string
    assert deserialize(serialize("PING PONG PONG PONG")) == "PING PONG PONG PONG"
    # # test for array
    assert deserialize(serialize(["PING PONG PONG PONG", 23, "OK", "PING", "PONG", "PONG", "PONG"])) == ["PING PONG PONG PONG", 23, "OK", "PING", "PONG", "PONG", "PONG"]
    # serialized_arr = serialize(["OKOK", 1223, "PING", "PING PONG >>>", 66529])
    # print(deserialize(serialized_arr))
if __name__ == '__main__':
    main()