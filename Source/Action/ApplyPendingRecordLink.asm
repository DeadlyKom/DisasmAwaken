                module Action
                module ApplyPendingRecordLink
                ; Документация [алгоритм и проверка](../../Docs/ActionRecordLinkEvent.md)
                ; -----------------------------------------
                ; Установка бита 0 LinkFlags, замена LinkedIndex на 1A и условная поправка по ClassCode записи
                ; исходная запись 17, перенесённое ядро ACTION банка 5, адреса 635B..637F, далее возможен общий хвост 6380, смещения #0598..#05BC
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, DE сохраняется
                ;   PendingRecord в операнде LD HL,nn задаёт ноль либо базу доступной FActionRecord с исходным выравниванием на 64
                ;   действует договор ApplyIndexedDelta, доступен поток RecordRow00 банка 0 и его CursorA, банк 0 выбран
                ;   на CPU-стеке внешний возврат, IRQ не вмешиваются, CaptureProjectedRecord пишет HL' в PendingRecord, допустимость указателя должен обеспечить окружающий обход
                ; Out:
                ;   при PendingRecord=0 HL=0000, DE и BC сохраняются, AF=0044, записей памяти нет
                ;   при ненулевом указателе бит 0 LinkFlags устанавливается, LinkedIndex получает 1A, остальные биты и поля сохраняются
                ;   после обработки PendingRecord=0000, CursorA=EF3B, эти изменения происходят до проверки старого LinkedIndex
                ;   если старый LinkedIndex равен 1A, HL=EF3B, DE сохраняется, B=ClassCode, C=1A, AF=1A42, State не меняется
                ;   иначе исполнение продолжается в ApplyIndexedDelta с B=ClassCode и C=старый LinkedIndex, результат определяется его договором
                ;   для класса не меньше 16 HL=EF3B, DE сохраняется, BC сохраняет ClassCode и старый LinkedIndex, A=ClassCode, F соответствует CP 16
                ;   для класса меньше 16 HL адрес поправки, DE сохраняется, B старый State, C и A новый State, F соответствует CP старого State с 32
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2, дополнительных стековых записей и OUT нет
                ; Corrupt:
                ;   HL, BC и AF по пути, R, LinkFlags и LinkedIndex выбранной записи, PendingRecord, CursorA, State при допустимом классе и старом LinkedIndex не равном 1A
                ; Note:
                ;   проверка старого LinkedIndex=1A запрещает только повторную поправку, запись полей, сброс указателя и назначение звука всё равно выполняются
                ;   разность ClassCode и LinkedIndex равна 7, исходная адресация изменяет только L, выравнивание записи не допускает переноса в H
                ;   сам вызов не выводит AY-регистры, это сделает UpdateAyEffects позднее
                ;   бит 0 LinkFlags имеет доказанного писателя, но его игровой смысл и смысл кода 1A ещё не установлены
                ;   CONTINUE после условного RET требует соседнего include ApplyIndexedDelta в жёстком порядке, новая команда JP не добавляется
                ;   проверка композиционная, реальный дочерний хвост исполнялся без подмен, игровой источник события и нативное поведение не доказаны
                ; -----------------------------------------
                ; Проверка изменяемого PendingRecord, ноль означает отсутствие записи для этой обработки.
Entry:          LD HL, #0000
                LD A, L
                OR H
                RET Z                                                           ; выход, если PendingRecord равен нулю, поля и звук не изменять

                ; -----------------------------------------
                ; Преобразование двух полей записи
                ; Расчёт адреса LinkFlags по базе физической FActionRecord.
                LD BC, FActionRecord.LinkFlags
                ADD HL, BC
                ; Обновление бита 0 LinkFlags с сохранением остальных семи разрядов, игровой смысл бита ещё не установлен.
                SET @ActionLinkFlagsConst.BackLinkBit, (HL)
                ; Сохранение старого LinkedIndex в C и замена поля исходным кодом 1A.
                DEC HL
                LD C, (HL)
                LD (HL), #1A
                ; Расчёт адреса ClassCode через младший байт, выровненная база записи исключает перенос.
                LD A, L
                ADD A, FActionRecord.ClassCode - FActionRecord.LinkedIndex
                LD L, A
                LD B, (HL)
                ; -----------------------------------------
                ; Сброс указателя и подготовка звука
                ; Обнуление PendingRecord до проверки прежнего LinkedIndex.
                LD HL, #0000
                LD (@ActionRecordLinkEventState.PendingRecord), HL
                ; Назначение потока RecordRow00 для AY-канала A, фактического вывода здесь нет.
                LD HL, @ActionAyStreams.RecordRow00
                LD (@ActionAyEffectState.CursorA), HL
                ; Проверка прежнего LinkedIndex после уже выполненного преобразования полей.
                LD A, C
                CP #1A
                RET Z                                                           ; выход, если прежний LinkedIndex равен 1A, дополнительную поправку State не выполнять

                ; JP @Action.ApplyIndexedDelta.Entry, продолжение в ApplyIndexedDelta.asm

                ; -----------------------------------------
                endmodule
                endmodule
