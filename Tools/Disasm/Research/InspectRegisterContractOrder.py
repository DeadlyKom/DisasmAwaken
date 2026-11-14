"""Кандидаты нарушения порядка явно перечисленных регистров в заголовках Source.

Условные абзацы и полнота договоров этой проверкой не доказываются.
"""
from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
ORDER = ('HL', 'DE', 'BC', 'AF', "HL'", "DE'", "BC'", "AF'", 'IX', 'IY')
TOKEN = r"(?:(?:HL|DE|BC|AF|H|L|D|E|B|C|A|F)'?|IXH|IXL|IYH|IYL|IX|IY)"
REGISTER = re.compile(TOKEN + r'(?=[\s,=—-]|$)')
SEPARATOR = re.compile(r'\s*(?:,|\bи\b)\s*')
DECLARATION = re.compile(r'(?:^|,\s*)(' + TOKEN + r')(?=\s*(?:=|[-—]))')
SECTIONS = ('In', 'Out', 'Corrupt')


def canonical(register):
    alternate = register.endswith("'")
    base = register.rstrip("'")
    if base.startswith(('IX', 'IY')):
        return base[:2]
    base = {'H': 'HL', 'L': 'HL', 'D': 'DE', 'E': 'DE',
            'B': 'BC', 'C': 'BC', 'A': 'AF', 'F': 'AF'}.get(base, base)
    return base + ("'" if alternate else '')


def declarations(text):
    # Условные абзацы не смешиваются с прямым перечислением регистров.
    first = REGISTER.match(text)
    if first is None:
        return []
    found = {first.start(): first.group()}
    end = first.end()
    while (separator := SEPARATOR.match(text, end)) is not None:
        token = REGISTER.match(text, separator.end())
        if token is None:
            break
        found[token.start()] = token.group()
        end = token.end()
    # Учитываются также отдельные объявления после запятой, например HL - 0, BC - 0.
    for match in DECLARATION.finditer(text):
        found[match.start(1)] = match.group(1)
    return [canonical(found[position]) for position in sorted(found)]


def main():
    source_map_path = ROOT / 'Tools/Disasm/Reports/SourceMap.json'
    source_map = json.loads(source_map_path.read_bytes())
    paths = sorted({row['path'] for row in source_map if row['kind'] == 'code'})
    fingerprint = sha256()
    candidates = []
    checked_sections = 0
    for path in paths:
        raw = (ROOT / path).read_bytes()
        fingerprint.update(path.encode('utf-8') + b'\0' + raw + b'\0')
        section = None
        seen = []
        evidence = []

        def finish():
            if section is None:
                return
            ranks = [ORDER.index(register) for register in seen]
            if ranks != sorted(ranks):
                candidates.append(dict(path=path, section=section, observed=seen[:],
                                       expected=sorted(seen, key=ORDER.index), evidence=evidence[:]))

        for number, line in enumerate(raw.decode('utf-8').splitlines(), 1):
            stripped = line.strip()
            if not stripped:
                continue
            if not stripped.startswith(';'):
                finish()
                section, seen, evidence = None, [], []
                continue
            text = stripped[1:].strip()
            if text in tuple(name + ':' for name in (*SECTIONS, 'Note')):
                finish()
                section = text[:-1] if text[:-1] in SECTIONS else None
                seen, evidence = [], []
                checked_sections += int(section is not None)
                continue
            if section is None:
                continue
            # Первое появление логического регистра отделяется от повторных пояснений его частей.
            for register in declarations(text):
                if register not in seen:
                    seen.append(register)
                    evidence.append(dict(line=number, register=register, text=text))
        finish()
    report = dict(method='explicit_unconditional_register_declarations_first_appearance_review_candidates',
                  source_map_sha256=sha256(source_map_path.read_bytes()).hexdigest(),
                  source_code_files_sha256=fingerprint.hexdigest(),
                  checked_files=len(paths), checked_sections=checked_sections,
                  candidate_count=len(candidates), candidates=candidates,
                  conditional_paragraphs_not_validated=True, register_aliases_normalized=True,
                  completeness_of_contracts_proved=False, candidates_are_not_confirmed_errors=True,
                  source_files_modified=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/RegisterContractOrderInspection.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'candidates'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
