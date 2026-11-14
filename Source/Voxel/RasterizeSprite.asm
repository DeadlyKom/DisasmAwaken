                module Voxel
                module RasterizeSprite
                ; Документация [развёрнутый проход](../../Docs/VoxelSpriteClipBounds.md)
                ; -----------------------------------------
                ; Развёрнутый проход по парам кодов спрайта с маскированием прозрачных половин и шагом по строкам
                ; In:
                ;   контекст формируется ClipSprite, в SP временно находится шаг ресурса по X
                ;   IXH хранит число видимых строк, IXL младший байт целого шага по Y, IYL младший адрес назначения
                ;   доступны таблицы преобразования #C0..#C3 банка 3, поток ресурса и буфер #8000..#8BFF
                ;   изменяемые операнды должны быть установлены для текущего спрайта, IRQ не вмешиваются
                ;   VoxelSpriteState.SavedSP содержит исходный CPU-стек с внешним возвратом, текущий SP не является адресом возврата
                ; Out:
                ;   для каждой непустой пары записаны четыре байта буфера, прозрачные пары не пишутся
                ;   по завершении всех строк маска первого столбца возвращена к #F0, SP восстановлен до RET
                ;   после RET SP равен слову VoxelSpriteState.SavedSP плюс два, входной дробный шаг X этим не сохраняется
                ;   I, IM и IFF сохраняются, R меняется согласно числу M1 с сохранением бита 7
                ;   значения регистров после вызова ClipSprite приведены в документации
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, изменяемая маска и буфер
                ; Note:
                ;   каждая группа занимает 84 байта, у последней отдельная проверка маски правого края
                ;   при нечётной левой границе вход смещается на 3, а непосредственная маска временно обнуляется
                ;   2600 моделей сверяют M1 пар и строк, R после каждой инструкции, весь буфер и единственную запись восстановления маски вне буфера
                ;   стоимость включает продолжения ClipSprite.NextRow между строками, подготовка ресурса перед первым входом считается отдельно
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 00, считывание двух кодов и выбор способа записи четырёх подстрок.
Entry:          LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly00                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly00                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance00

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair00:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance00

                ; Подготовка маски при прозрачной правой половине.
LeftOnly00:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair00

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly00:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair00                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair00:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance00:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 01, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair01:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly01                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly01                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance01

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair01:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance01

                ; Подготовка маски при прозрачной правой половине.
LeftOnly01:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair01

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly01:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair01                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair01:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance01:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 02, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair02:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly02                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly02                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance02

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair02:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance02

                ; Подготовка маски при прозрачной правой половине.
LeftOnly02:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair02

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly02:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair02                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair02:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance02:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 03, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair03:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly03                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly03                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance03

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair03:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance03

                ; Подготовка маски при прозрачной правой половине.
LeftOnly03:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair03

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly03:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair03                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair03:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance03:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 04, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair04:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly04                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly04                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance04

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair04:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance04

                ; Подготовка маски при прозрачной правой половине.
LeftOnly04:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair04

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly04:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair04                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair04:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance04:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 05, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair05:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly05                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly05                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance05

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair05:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance05

                ; Подготовка маски при прозрачной правой половине.
LeftOnly05:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair05

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly05:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair05                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair05:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance05:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 06, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair06:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly06                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly06                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance06

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair06:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance06

                ; Подготовка маски при прозрачной правой половине.
LeftOnly06:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair06

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly06:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair06                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair06:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance06:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 07, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair07:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly07                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly07                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance07

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair07:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance07

                ; Подготовка маски при прозрачной правой половине.
LeftOnly07:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair07

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly07:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair07                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair07:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance07:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 08, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair08:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly08                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly08                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance08

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair08:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance08

                ; Подготовка маски при прозрачной правой половине.
LeftOnly08:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair08

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly08:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair08                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair08:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance08:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 09, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair09:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly09                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly09                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance09

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair09:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance09

                ; Подготовка маски при прозрачной правой половине.
LeftOnly09:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair09

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly09:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair09                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair09:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance09:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 10, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair10:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly10                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly10                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance10

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair10:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance10

                ; Подготовка маски при прозрачной правой половине.
LeftOnly10:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair10

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly10:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair10                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair10:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance10:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 11, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair11:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly11                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly11                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance11

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair11:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance11

                ; Подготовка маски при прозрачной правой половине.
LeftOnly11:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair11

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly11:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair11                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair11:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance11:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 12, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair12:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly12                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly12                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance12

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair12:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance12

                ; Подготовка маски при прозрачной правой половине.
LeftOnly12:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair12

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly12:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair12                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair12:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance12:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 13, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair13:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly13                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly13                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance13

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair13:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance13

                ; Подготовка маски при прозрачной правой половине.
LeftOnly13:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair13

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly13:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair13                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair13:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance13:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 14, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair14:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly14                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly14                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance14

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair14:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance14

                ; Подготовка маски при прозрачной правой половине.
LeftOnly14:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair14

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly14:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair14                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair14:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance14:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 15, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair15:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly15                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly15                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance15

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair15:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance15

                ; Подготовка маски при прозрачной правой половине.
LeftOnly15:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair15

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly15:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair15                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair15:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance15:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 16, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair16:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly16                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly16                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance16

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair16:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance16

                ; Подготовка маски при прозрачной правой половине.
LeftOnly16:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair16

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly16:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair16                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair16:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance16:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 17, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair17:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly17                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly17                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance17

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair17:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance17

                ; Подготовка маски при прозрачной правой половине.
LeftOnly17:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair17

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly17:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair17                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair17:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance17:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 18, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair18:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly18                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly18                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance18

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair18:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance18

                ; Подготовка маски при прозрачной правой половине.
LeftOnly18:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair18

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly18:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair18                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair18:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance18:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 19, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair19:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly19                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly19                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance19

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair19:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance19

                ; Подготовка маски при прозрачной правой половине.
LeftOnly19:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair19

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly19:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair19                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair19:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance19:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 20, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair20:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly20                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly20                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance20

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair20:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance20

                ; Подготовка маски при прозрачной правой половине.
LeftOnly20:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair20

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly20:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair20                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair20:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance20:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 21, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair21:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly21                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly21                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance21

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair21:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance21

                ; Подготовка маски при прозрачной правой половине.
LeftOnly21:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair21

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly21:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair21                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair21:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance21:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 22, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair22:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly22                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly22                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance22

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair22:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance22

                ; Подготовка маски при прозрачной правой половине.
LeftOnly22:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair22

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly22:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair22                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair22:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance22:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 23, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair23:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly23                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly23                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance23

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair23:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance23

                ; Подготовка маски при прозрачной правой половине.
LeftOnly23:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair23

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly23:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair23                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair23:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance23:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 24, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair24:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly24                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly24                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance24

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair24:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance24

                ; Подготовка маски при прозрачной правой половине.
LeftOnly24:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair24

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly24:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair24                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair24:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance24:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 25, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair25:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly25                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly25                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance25

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair25:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance25

                ; Подготовка маски при прозрачной правой половине.
LeftOnly25:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair25

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly25:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair25                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair25:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance25:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 26, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair26:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly26                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly26                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance26

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair26:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance26

                ; Подготовка маски при прозрачной правой половине.
LeftOnly26:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair26

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly26:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair26                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair26:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance26:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 27, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair27:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly27                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly27                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance27

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair27:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance27

                ; Подготовка маски при прозрачной правой половине.
LeftOnly27:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair27

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly27:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair27                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair27:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance27:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 28, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair28:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly28                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly28                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance28

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair28:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance28

                ; Подготовка маски при прозрачной правой половине.
LeftOnly28:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair28

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly28:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair28                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair28:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance28:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 29, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair29:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly29                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly29                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance29

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair29:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.Advance29

                ; Подготовка маски при прозрачной правой половине.
LeftOnly29:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair29

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly29:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair29                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair29:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance29:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 30, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair30:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly30                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND D
                JR Z, @Voxel.RasterizeSprite.LeftOnly30                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.Advance30

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair30:     RES 5, C
                INC H
                INC H
                INC H
                JP @Voxel.RasterizeSprite.Advance30

                ; Подготовка маски при прозрачной правой половине.
LeftOnly30:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair30

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly30:    AND D
                JR Z, @Voxel.RasterizeSprite.SkipPair30                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair30:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                INC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
Advance30:      INC C
                EXX
                ; -----------------------------------------
                ; -----------------------------------------
                ; Пара 31, считывание двух кодов и выбор способа записи четырёх подстрок.
Pair31:         LD E, H
                ADD HL, SP
                LD A, (DE)
                AND #F0
                EXX
                LD L, A
                EXX
                LD E, H
                ADD HL, SP
                LD A, (DE)
                EXX
                JR Z, @Voxel.RasterizeSprite.RightOnly31                        ; переход, если старший код прозрачен, проверить младший отдельно

                AND #0F
                JR Z, @Voxel.RasterizeSprite.LeftOnly31                         ; переход, если младший код прозрачен, сохранить младшую половину назначения

                OR L
                LD L, A
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (HL)
                LD (BC), A
                JP @Voxel.RasterizeSprite.NextRow

                ; Обе половины прозрачны, обновить только позицию внутри строки.
SkipPair31:     SET 5, C
                DEC H
                DEC H
                DEC H
                JP @Voxel.RasterizeSprite.NextRow

                ; Подготовка маски при прозрачной правой половине.
LeftOnly31:     LD E, D
                JP @Voxel.RasterizeSprite.MergePair31

                ; Подготовка правого кода при прозрачной левой половине.
RightOnly31:    AND #0F
                JR Z, @Voxel.RasterizeSprite.SkipPair31                         ; переход, если оба кода прозрачны, пропустить запись

                LD E, #F0
                LD L, A
                ; Сохранение прозрачной половины назначения по маске E.
MergePair31:    LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                SET 5, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                DEC H
                RES 6, C
                LD A, (BC)
                AND E
                OR (HL)
                LD (BC), A
                ; -----------------------------------------
                ; Продвижение адреса назначения и источника после конца строки.
NextRow:        LD A, IYL
                ADD A, #80
                LD C, A
                LD IYL, A
                JR NC, @Voxel.RasterizeSprite.SetRowHalf                        ; переход, если шаг назначения #80 не вызвал перенос в старший байт

                INC B
SetRowHalf:     SET 5, C
                LD H, #00
                EXX
                EX AF, AF'
                ADD A, C
                LD L, A
                LD A, B
                JR NC, @Voxel.RasterizeSprite.StepSource                        ; переход, если дробный шаг Y не дал перенос в целую часть

                ADD A, #00
                JR C, @Voxel.RasterizeSprite.CarrySource                        ; переход, если добавление шага строки ресурса перенеслось в старший байт

StepSource:     ADD A, IXL
                LD B, A
                LD A, D
                ADC A, #00
                LD D, A
                LD A, L
                DEC IXH
                JP NZ, @Voxel.ClipSprite.NextRow                                ; переход, если остались видимые строки спрайта

                ; Восстановление маски первого столбца и настоящего CPU-стека.
                LD HL, #0000
                INC HL
                INC HL
                INC HL
                INC HL
                LD (HL), #F0
                LD SP, #0000
                RET

CarrySource:    INC D
                JP @Voxel.RasterizeSprite.StepSource

                endmodule
                endmodule
