                module Controls
                module PrepareCircleLeftClip
                ; Документация [алгоритм и проверка](../../Docs/ControlsCircleSetup.md)
                ; -----------------------------------------
                ; Подготовка фиксированного левого столбца 1 и правого криволинейного края
                ; исходная запись 22, банк 1, смещения #14E4..#1500
                ; In:
                ;   HL, DE, BC и AF входных аргументов не задают
                ;   банк 1 выбран, WorkX, WorkY, CenterY, Radius, Flags и Mode доступны для чтения, SavedB доступен для записи
                ;   на CPU-стеке внешний возврат, ещё четыре байта нужны для CALL и сохранённого AF, IRQ не вмешиваются
                ; Out:
                ;   для X=(128+Radius-WorkX) AND FF и P=8000+32*CenterY+(X DIV 8)
                ;   HL=P, D=Radius, E=((LOW P) AND E0) OR 1, B=0, C=FF >> (X AND 7)
                ;   A=E, F соответствует AND Mode, Z установлен ровно при Mode=0, возвращаемый A всегда ненулевой
                ;   HL' сохраняется, D' сохраняется, E'=0, B' сохраняется, C'=(-Radius) AND FF
                ;   AF', IX, IY, I, IM и IFF сохраняются
                ;   SavedB=WorkX, I, IM и IFF сохраняются, SP=входной SP+2, R получает 93-4*(X AND 7) M1
                ; Corrupt:
                ;   HL, DE, BC, AF, E', C', SavedB, четыре байта CPU-стека, R
                ; Note:
                ;   фиксированный левый край расположен в столбце 1 и имеет маску B=0, правая маска включает X
                ;   помощник BuildRightSpanMask сохраняет на стеке вычисленный X и F от SUB WorkX
                ;   пиксели не записываются, байтовый перенос при расчёте X сохраняется как в оригинале
                ; -----------------------------------------
                ; подготовка радиуса и альтернативного состояния без рисования
Entry:          CALL @Controls.LoadCircleMidpoint.Entry
                ; выбор центральной строки для правого криволинейного края
                LD A, (@ControlsCircleSetupState.CenterY)
                LD C, A
                ; вычисление X правого края как 128+Radius-WorkX по модулю байта
                LD A, #80
                ADD A, D
                SUB B
                ; построение адреса и включающей маски правого края, SavedB получает WorkX
                CALL @Controls.BuildRightSpanMask.Entry
                ; вычисление младшего адреса фиксированного левого столбца 1
                LD A, L
                AND #E0
                OR #01
                LD E, A
                ; сохранение адреса в B перед чтением Mode, LD не меняют флаги
                LD B, A
                ; проверка нулевого Mode для выходного Z, возвращаемый A ниже заменяется адресом
                LD A, (@ControlsInteriorRowsState.Mode)
                AND A
                ; возврат адреса в A и нулевой маски B с сохранением F от проверки Mode
                LD A, B
                LD B, #00
                RET

                endmodule
                endmodule
