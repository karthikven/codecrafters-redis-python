import asyncio


async def handle_client(reader, writer):
    while True:
        data = await reader.read(100)
        if not data:
            break
        writer.write(b"+PONG\r\n")
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
