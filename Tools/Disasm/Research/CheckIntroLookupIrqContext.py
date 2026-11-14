"""Фактический IY первого атрибутного вывода табличного эффекта.

Документация: ../../../Docs/IntroGeneratedEffects.md#irq-первого-табличного-вывода
"""
import json

from CheckIntroColumnIrqContext import check_initializer, ROOT


def main():
    report = check_initializer(entry=0x6C9C, end=0x6D6A, texture_bytes=0x1300)
    report['initializer_entry'] = 0x6C9C
    (ROOT / 'Tools/Disasm/Reports/IntroLookupIrqContextVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены восемь IRQ первого табличного вывода с IY=5C0F и переносом в 5C4F.')


if __name__ == '__main__':
    main()
