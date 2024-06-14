"""Postman but on the commandline."""

import argparse
import asyncio
import logging

import websockets

parser = argparse.ArgumentParser(description="Communicate with websocket connection.")
parser.add_argument(
    "--uri", "-t", default="", type=str, help="Target URI with wss:// or ws://."
)


args = parser.parse_args()


logging.basicConfig(level=logging.INFO, format="%(message)s")


async def connect_and_receive(uri: str):
    try:
        async with websockets.connect(uri) as connection:

            logging.info("Connection success to %s", uri)

            async def receive() -> None:
                while True:
                    incoming = await connection.recv()
                    logging.info("[FROM %s] %s", uri, incoming)

            async def send() -> None:
                while True:
                    message: str = input("[TO %s] ", uri)

                    if message == "exit":
                        await connection.close()
                        logging.info("Bye-bye!")
                        break

                    response = await connection.send(message)
                    logging.info("Message confirmation: %s", response)

            await asyncio.gather(receive(), send())

    except websockets.ConnectionClosedError as cce:
        logging.error("Websocket closed badly: %s", cce)


if __name__ == "__main__":
    uri: str = args.uri
    if uri == "":
        uri = input("Enter websocket URI starting with `ws://` or `wss://`: ")
        logging.info("Using URI: %s", uri)

    asyncio.get_event_loop().run_until_complete(connect_and_receive(uri))
