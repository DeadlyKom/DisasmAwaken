"""Фактический IY первого вывода прокручиваемого эффекта.

Документация: ../../../Docs/IntroScrolledFrame.md#iy-инициализатора-и-перенос-frames
"""
import json

from CheckIntroColumnIrqContext import check_initializer, ROOT


def main():
    report = check_initializer(entry=0x66FB, end=0x6722, texture_bytes=0x1000)
    report['initializer_entry'] = 0x66FB
    (ROOT / 'Tools/Disasm/Reports/IntroScrolledIrqContextVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены восемь IRQ первого прокручиваемого вывода с IY=5C0F и переносом в 5C4F.')


if __name__ == '__main__':
    main()
