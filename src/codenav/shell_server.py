# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 23:39:06 2023

@author: jkris
"""

from os import path
from sys import platform, argv
from socket import gethostname
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from multiprocessing.managers import BaseManager
from multiprocessing import Queue, Process
from time import sleep
import psutil

PORT_D = 8000
KEY_D = b"key"
SHELL = True
if "win" in platform.lower():
    ACTIVATE = "C:\\ProgramData\\Anaconda3\\Scripts\\activate.bat && conda activate py39 && python"
else:
    # conda_path = "/appl/anaconda/anaconda3-2021.05/"
    CONDA_PATH = "/home/jkrist2696/anaconda3"
    CONDA_INIT = path.join(CONDA_PATH, "etc/profile.d/conda.sh")
    ACTIVATE = f'. "{CONDA_INIT}" && conda activate py39 && python3'


class QueueManager(BaseManager):
    """
    QueueManager
    """


def run_queue_server(queuename: str, port: int, hostname: str = None, key: str = KEY_D):
    """
    run_queue_server
    """
    if not hostname:
        hostname = gethostname()
    manager = QueueManager(address=(hostname, port), authkey=key)
    queue = Queue()
    QueueManager.register(queuename, callable=lambda: queue)
    queue_done = Queue()
    QueueManager.register(queuename + "_done", callable=lambda: queue_done)
    queue_server = manager.get_server()
    print(f"Server Started (Host, Queue, Port) = ({hostname}, {queuename}, {port})")
    queue_server.serve_forever()


def connect_to_queue(
    queuename: str, hostname: str = None, port: int = PORT_D, key: str = KEY_D
):
    """
    connect_to_queue
    """
    if not hostname:
        hostname = gethostname()
    QueueManager.register(queuename)
    manager = QueueManager(address=(hostname, port), authkey=key)
    manager.connect()
    queue_function = getattr(manager, queuename)
    queue = queue_function()
    return queue


def test_connect(
    queuename: str, port: int = PORT_D, key: str = KEY_D, tries: int = 10
) -> bool:
    """test_connect"""
    error_str = "None"
    for i in range(tries):
        try:
            connect_to_queue(queuename, port=port, key=key)
            connect_to_queue(queuename + "_done", port=port, key=key)
            print(f"    Connected in {i+1} tries.")
            return True
        except ConnectionRefusedError as err:
            error_str = err
            sleep(0.1 * i)
    print(f"    Could not connect in {i+1} attempt(s).\n        error: {error_str}")
    return False


def kill_id(pid: int, reason: str = ""):
    """
    kill_id
    """
    if psutil.pid_exists(pid):
        if len(reason) > 0:
            print(f"    Killing process due to {reason}: {pid}")
        process = psutil.Process(pid)
        for childproc in process.children(recursive=True):
            childproc.kill()
        process.kill()


def get_from_queue(
    server_id: int,
    queuename: str,
    hostname: str = None,
    port: int = PORT_D,
    key: str = KEY_D,
    stop: str = None,
):
    """
    get_from_queue
    """
    if not psutil.pid_exists(server_id):
        # [f"Process {server_id} Does Not Exist: {err}\n"]
        return False, False
    if not hostname:
        hostname = gethostname()
    if stop is not None:
        kill_id(server_id, reason=stop)
        return [f"    Killed Process: {server_id}\n"], False
    try:
        queue = connect_to_queue(queuename, hostname=hostname, port=port, key=key)
        queue_done = connect_to_queue(
            queuename + "_done", hostname=hostname, port=port, key=key
        )
    except ConnectionRefusedError as err:  # ,OSError,ConnectionResetError
        outstring = f"!!!! No Connection with (Host,Queue,Port) = ({hostname},{queuename},{port})"
        return [
            f"{outstring}\n    Process {server_id} has no active connection: {err}\n"
        ], False
    queueitems = []
    if (not queue_done.empty()) and queue.empty():
        _done = queue_done.get()
        return [" "], False  # f"\n\ndone message: {_done}"
    while (not queue.empty()) and (len(queueitems) < 100):
        queueitem = queue.get()
        queueitems.append(queueitem)
    return queueitems, True


def sub_stdout_stream(command: str, queuename: str, port: int):
    """
    sub_stdout_stream
    """
    queue = connect_to_queue(queuename, port=port)
    queue_done = connect_to_queue(queuename + "_done", port=port)
    # print(f"\nsub_stdout_stream Command:    {command}")
    # test below in linux while shell=False
    process = Popen(
        command,
        stdout=PIPE,
        stderr=STDOUT,
        shell=SHELL,
        errors="ignore",
        encoding="utf-8",
        text=True,
    )
    for line in iter(process.stdout.readline, ""):
        if len(line) > 0:
            queue.put(line)
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        queue_done.put("error")
        return CalledProcessError(return_code, command)
    queue_done.put("success")
    return


def stream_queue(queuename: str, command: str, port: int = PORT_D):
    """
    stream_queue
    """
    server_proc = Process(target=run_queue_server, args=(queuename, port))
    server_proc.start()
    print(f"\nServer Process ID = {server_proc.pid}")
    test_connect(queuename, port=port, key=KEY_D)
    sub_stdout_stream(command, queuename, port)
    server_proc.join()
    return server_proc


def shell_server_test(__file__):
    """
    shell_server_test
    """

    queuename = "test_server"
    scriptdir = path.dirname(__file__)
    testpath = path.join(scriptdir, "queue_test.py")
    serverpath = path.join(scriptdir, "shell_server.py")
    runpycmd = f'{ACTIVATE} ""{testpath}""'
    server_args = f'"{serverpath}" "{queuename}" "{runpycmd}"'
    runserver = f"{ACTIVATE} {server_args}"
    print(f"\nServer Command:\n{runserver}")
    parent_proc = Popen(runserver, shell=SHELL)
    # parent_proc = Popen("/bin/bash", shell=SHELL, stdin=PIPE, encoding="utf-8")
    test_connect(queuename)
    print("\nParent Process Started")
    pid = parent_proc.pid
    i = 0
    increment = 0.25
    status = True
    while status:  # psutil.pid_exists(pid) and
        lines, status = get_from_queue(pid, queuename, port=PORT_D)
        print(
            f"\n    time={i} : proc[{pid}]={psutil.pid_exists(pid)} : Status={status}"
        )
        if lines:
            print("".join(lines))
        else:
            print("    lines = False")
        i += increment
        sleep(increment)
    print("\nLoop Finished")
    lines, status = get_from_queue(pid, queuename, port=PORT_D, stop="loop finished")
    print(f"\n    time={i} : proc[{pid}]={psutil.pid_exists(pid)} : Status={status}")
    if lines:
        print("".join(lines))
    else:
        print("    lines = False")
    print("\nFinal Check")
    lines, status = get_from_queue(pid, queuename, port=PORT_D, stop="final check")
    print(f"\n    time={i} : proc[{pid}]={psutil.pid_exists(pid)} : Status={status}")
    if lines:
        print("".join(lines))
    else:
        print("    lines = False")


if __name__ == "__main__":
    if len(argv) == 1:
        shell_server_test(__file__)
    else:
        PORT = PORT_D
        if len(argv) > 3:
            PORT = int(argv[3])
        stream_queue(argv[1], argv[2], PORT)
