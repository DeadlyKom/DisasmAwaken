"""Чтение остановленных изолированных запусков Xpeccy+, без подмены RAM и регистров."""

from pathlib import Path
import hashlib
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from RuntimeSmoke import request, WORK, EMULATOR
from ExportScreens import bitmap


def main():
    runs = json.loads((WORK/"Runs.json").read_text(encoding="utf-8-sig"))
    results = []
    target = ROOT/"Tools/Disasm/Reports/Runtime"
    target.mkdir(parents=True,exist_ok=True)
    for run in runs["runs"]:
        evidence = request(run["port"], ["pause","getreg PC","getreg SP","dump 4000 432","dump 5c00 32"])
        (target/(run["name"]+".json")).write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        def get(command):
            return next(x["response"] for x in evidence if x["command"]==command)
        screen = bytearray()
        for line in get("dump 4000 432").splitlines():
            match = re.match(r"[0-9A-Fa-f]+\s*:\s*((?:[0-9A-Fa-f]{2}\s+){16})",line)
            if match:
                screen.extend(bytes.fromhex(match[1]))
        if len(screen) != 6912:
            raise ValueError("Получен неполный экран из TCP-интерфейса")
        (target/(run["name"]+".scr")).write_bytes(screen)
        bitmap(screen).resize((512,384)).save(target/(run["name"]+".png"))
        result = dict(name=run["name"],pc=get("getreg PC").split()[0],sp=get("getreg SP").split()[0],
                      image_sha256=hashlib.sha256((ROOT/run["image"]).read_bytes()).hexdigest(),
                      screen_sha256=hashlib.sha256(screen).hexdigest(), screen=f"Tools/Disasm/Reports/Runtime/{run['name']}.png")
        results.append(result)
        print(run["name"],"PC",result["pc"],"SP",result["sp"])
    report = dict(method="full_xpeccy_execution_with_isolated_config",memory_or_registers_injected=False,
                  emulator_sha256=hashlib.sha256((ROOT/runs["executable"]).read_bytes()).hexdigest(),
                  original_config_unchanged=hashlib.sha256((EMULATOR/"config/config.conf").read_bytes()).hexdigest()==runs["original_config_sha256"],
                  results=results,visual_scope_requires_review=True,all_gameplay_verified=False)
    (ROOT/"Tools/Disasm/Reports/RuntimeVerification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
