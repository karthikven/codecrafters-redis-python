import asyncio


def serialize_string_in_resp(inp: str):
    len_of_str = len(inp)
    output = f"${len_of_str}\r\n{inp}\r\n"
    byte_output = output.encode('utf-8')
    return byte_output

def parse_request(req):
    # convert byte string to regular string
    string_data = req.decode('utf-8')
    array_data = string_data.split("\r\n")
    if len(array_data) > 3 and array_data[2].lower() == "echo":
        return serialize_string_in_resp(array_data[4])
    return serialize_string_in_resp("PONG")    

async def handle_client(reader, writer):
    while True:
        data = await reader.read(100)
        if not data:
            break
        to_send = parse_request(data)
        writer.write(to_send)
        await writer.drain()
    writer.close()

async def main():
    HOST = "localhost"
    PORT = 6379
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()
        
if __name__ == "__main__":
    asyncio.run(main())
