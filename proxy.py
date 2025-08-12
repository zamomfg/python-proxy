import argparse
import asyncio
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options
from mitmproxy import http
from mitmproxy.addonmanager import Loader
from mitmproxy import ctx
from mitmproxy.addons import clientplayback
from time import sleep

SLEEP_TIME = 3

class RequestReplayAddon:
    max_retries = 0
    def __init__(self, retries: int):
        self.max_retries = retries

    def load(self, loader: Loader):
        loader.add_option(
            name="max_retries", typespec=int, default=self.max_retries,
            help="Max retries for 404 responses"
        )

    def request(self, flow: http.HTTPFlow):
        if flow.is_replay == "request":
            flow.metadata["retries"] = flow.metadata["retries"] + 1
        else:
            flow.metadata["retries"] = 0

    def response(self, flow: http.HTTPFlow):
        max_retires = ctx.options.max_retries

        if flow.response.status_code == 404: # or flow.response.status_code == 400: # code 400 happends when a linked resource do not exist (yet)
            if flow.is_replay == None:
                print(flow.request.url, flow.response.status_code)

            if flow.metadata["retries"] < max_retires:
                print(f"Request failed (attempt {flow.metadata["retries"] + 1}), retrying the previous request...")
                copy = flow.copy() 
                flow.kill()
                sleep(SLEEP_TIME)
                playback = ctx.master.addons.get('clientplayback')
                playback.start_replay([copy])
            else:
                print("Maximum retires reached!")


async def start_proxy(listen_host: str, listen_port: int, retries: int):
    options = Options(listen_host=listen_host, listen_port=listen_port)
    m = DumpMaster(options, with_termlog=False, with_dumper=False)

    addon = RequestReplayAddon(retries)
    m.addons.add(addon)

    try:
        print(f"Starting proxy on {listen_host}:{listen_port}...")
        await m.run()
    except KeyboardInterrupt:
        print("Shutting down proxy...")
        await m.shutdown()

def main():
    parser = argparse.ArgumentParser(description="Start a mitmproxy-based proxy server with retry logic.")
    parser.add_argument(
        "-p", "--port", type=int, default=8080,
        help="Port to listen on (default: 8080)"
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--retries", type=int, default=3,
        help="The number of retries of 404 erros before failing"
    )

    args = parser.parse_args()
    LISTENING_PORT = args.port
    asyncio.run(start_proxy(args.host, LISTENING_PORT, args.retries))

if __name__ == "__main__":
    main()