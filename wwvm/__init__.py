import argparse
import atexit
import json
import os
import subprocess
import time
import uuid

import urllib3

WWVM_USER = "tunnel"
WWVM_HOST = "wwvm.net"
WWVM_URL = "https://{}".format(WWVM_HOST)


def set_up_tunnel(user, host, socket_path, private_key_path, local_port, remote_port):
    subprocess.check_call([
        "ssh",
        "-q",
        "-f",
        "-N",
        "-M",
        "-S", socket_path,
        "-R", "{}:localhost:{}".format(remote_port, local_port),
        "{}@{}".format(user, host),
        "-i", private_key_path,
    ])


def tear_down_tunnel(user, host, socket_path):
    subprocess.check_call([
        "ssh",
        "-q",
        "-S", socket_path,
        "-O", "exit",
        "{}@{}".format(user, host)
    ])


def cleanup(user, host, socket_path, private_key_path):
    tear_down_tunnel(user, host, socket_path)
    os.unlink(private_key_path)


def generate_socket_path():
    return "/tmp/wwvm-{}".format(
        str(uuid.uuid4()).split("-")[0]
    )


def main():
    parser = argparse.ArgumentParser(prog="wwvm")
    parser.add_argument("port", help="The local port wwvm should use to construct the tunnel")
    args = parser.parse_args()

    local_port = args.port
    socket_path = generate_socket_path()

    response = urllib3.PoolManager().request("POST", WWVM_URL)
    result = json.loads(response.data)

    private_key = result["private_key"].replace("\\n", "\n")
    subdomain = result["subdomain"]
    remote_port = result["port"]

    private_key_path = "/tmp/wwvm-{}".format(subdomain)

    with open(private_key_path, "w") as f:
        f.write(private_key)

    os.chmod(private_key_path, 0o600)
    set_up_tunnel(WWVM_USER, WWVM_HOST, socket_path,
                  private_key_path, local_port, remote_port)
    atexit.register(cleanup, WWVM_USER, WWVM_HOST,
                    socket_path, private_key_path)

    print("Tunnels: ")
    print("")
    print("\thttp://localhost:5000 -> http://{}.{}".format(subdomain, WWVM_HOST))
    print("\thttp://localhost:5000 -> https://{}.{}".format(subdomain, WWVM_HOST))

    while True:
        time.sleep(5)
        pass


if __name__ == "__main__":
    main()
