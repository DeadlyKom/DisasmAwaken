"""Подготовка изолированного Xpeccy+ и чтение его локального TCP-интерфейса."""

from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import socket


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT/"Tools/Disasm/Research/Runtime"
EMULATOR = WORK/"Emulator"


def configure(text, port):
    replacements = {"port":str(port),"savepaths":"no","pause.inactive":"no", "addboot":"no",
                    "autorun":"yes","lastdir":".","recent":"","enabled":"no", "mute":"yes"}
    for key, value in replacements.items():
        text = re.sub(r"(?m)^"+re.escape(key)+r"\s*=.*$", key+" = "+value, text)
    return text


def prepare():
    inputs = {"Original":ROOT/"Tools/Disasm/Disk/original.trd", "Rebuilt":ROOT/"Awakenv02.trd"}
    entries = []
    for index,(name,path) in enumerate(inputs.items()):
        directory = WORK/name
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copytree(EMULATOR/"config", directory/"config", dirs_exist_ok=True)
        config = directory/"config/config.conf"
        original = (EMULATOR/"config/config.conf").read_bytes()
        port = 30131 + index
        config.write_text(configure(original.decode("utf-8",errors="replace"),port),encoding="utf-8")
        shutil.copy2(path, directory/"Awakenv02.trd")
        entries.append(dict(name=name,port=port,config=(directory/"config").relative_to(ROOT).as_posix(),
                            image=(directory/"Awakenv02.trd").relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    report = dict(executable=(EMULATOR/"xpeccy-plus.exe").relative_to(ROOT).as_posix(),runs=entries,
                  original_config_sha256=hashlib.sha256((EMULATOR/"config/config.conf").read_bytes()).hexdigest())
    (WORK/"Runs.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Prepared",len(entries),"isolated configurations")


def request(port, commands):
    result = []
    with socket.create_connection(("127.0.0.1",port),timeout=3) as stream:
        stream.settimeout(3)
        def read():
            data = b""
            while not data.endswith(b"> "):
                part = stream.recv(65536)
                if not part:
                    break
                data += part
            return data.decode("utf-8",errors="replace")
        result.append(dict(command=None,response=read()))
        for command in commands:
            stream.sendall((command+"\n").encode("ascii"))
            result.append(dict(command=command,response=read()))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare","request"))
    parser.add_argument("--port",type=int)
    parser.add_argument("--command",action="append",default=[])
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    else:
        print(json.dumps(request(args.port,args.command),ensure_ascii=False,indent=2))
