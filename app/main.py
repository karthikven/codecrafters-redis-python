import asyncio
from app.resp import deserialize, serialize
from app.command_handler import command_dispatcher
from app.store import Store

async def handle_client(reader, writer):
    store = Store()
    while True:
        data = await reader.read(100)
        if not data:
            break
        to_send, store = command_dispatcher(data, store)
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
