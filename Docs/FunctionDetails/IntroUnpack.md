# IntroUnpack

Операционные факты ниже получены из исходных инструкций.
Список непосредственных чтений и записей не включает косвенные обращения
через HL, DE, BC, IX/IY и эффекты вызываемых подпрограмм.

## UnpackScreen

[IntroUnpack.UnpackScreen](../../Source/IntroUnpack/UnpackScreen.asm)

[Алгоритм, контракт и проверка](../IntroScreen.md).

Распаковка экранного потока после переноса из #8931 в #6E31.

Вход `#6E31`, запись 3, смещения `#2631..#26CA`.

- Прямые вызовы: `#1FC6`.
- Непосредственные чтения: нет непосредственных обращений.
- Непосредственные записи: нет непосредственных обращений.
- Ввод и вывод: нет.
- Косвенное завершение: нет в этом фрагменте.

## SetAttributeScanDest

[IntroUnpack.SetAttributeScanDest](../../Source/IntroUnpack/SetAttributeScanDest.asm)

Выбор #FF01 и последовательный вход в условный обход атрибутов.

[Договоры и границы проверки](../IntroAttributeCountTail.md).

## ScanAttributeCountTail

[IntroUnpack.ScanAttributeCountTail](../../Source/IntroUnpack/ScanAttributeCountTail.asm)

Чтение PAPER, изменение первого счётчика и вывод смещения максимума в ULA.

[Договоры и границы проверки](../IntroAttributeCountTail.md).

## WaitNonzeroKeyByte

[IntroUnpack.WaitNonzeroKeyByte](../../Source/IntroUnpack/WaitNonzeroKeyByte.asm)

Очистка и ожидание ненулевого байта по 5C08.

[Договоры и границы проверки](../IntroDetachedTail.md).

## CopyScreenToBankWindow

[IntroUnpack.CopyScreenToBankWindow](../../Source/IntroUnpack/CopyScreenToBankWindow.asm)

Копирование экрана из 4000 в выбранное окно C000.

[Договоры и границы проверки](../IntroDetachedTail.md).

## CopyScreenFromBankWindow

[IntroUnpack.CopyScreenFromBankWindow](../../Source/IntroUnpack/CopyScreenFromBankWindow.asm)

Копирование экрана из выбранного окна C000 в 4000.

[Договоры и границы проверки](../IntroDetachedTail.md).

## UnpackTailGate

[IntroUnpack.UnpackTailGate](../../Source/IntroUnpack/UnpackTailGate.asm)

Внутренний вызов распаковщика и проверка двух байтов после его возврата.

[Договоры и границы проверки](../IntroDetachedUnpackGate.md).
