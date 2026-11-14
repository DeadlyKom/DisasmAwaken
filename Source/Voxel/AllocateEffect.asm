                module Voxel
                module AllocateEffect
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
                ; Полный договор создания [разбор](../../Docs/Effects.md#полные-договоры-создания-эффектов)
; Подробный разбор [Effects.md](../../Docs/Effects.md)
; -----------------------------------------
; Поиск свободной записи #12 байт по знаку и нулевому признаку в поле +7
; исходная запись 21, файловые смещения #0033..#007E
                ; In:
                ;   HL и DE ресурс и шаг кадра, HL', DE', BC' три слова записи, AF' - A полный State, IY запись перед поиском
                ;   операнды #EC5A, #EC6C, #EC79 и #EC7D содержат Mode, FrameReload, FrameWidth и FrameHeight
                ;   код VOXAL и его изменяемые операнды доступны в банке 3, IRQ/NMI не вмешиваются
                ;   первый проверяемый State находится по IY+18+7, поиск должен достигнуть нуля либо отрицательного байта
                ;   читаемые записи и выбранная свободная запись доступны, CPU-стек и код не пересекаются с записями и операндами
                ; Out:
                ;   HL и DE сохранены, BC - #0012, IY указывает выбранную запись либо отрицательный ограничитель
                ;   HL', DE', BC', IX, I, IM, IFF и paging сохраняются, SP равен входному SP+2, портовых операций нет
                ;   при успехе записаны все 18 байтов FVisualEffect, первые три слова равны входным альтернативным HL, DE и BC
                ;   при успехе A=FrameReload, F равен входному F', AF'=0054, State получает входной A' без проверки его знака или нуля
                ;   при отрицательном ограничителе записи не меняются, A равен прочитанному State, F от AND A, AF' сохранён
                ;   при n пропущенных занятых записях IY равен входному IY+18*(n+1) modulo 65536, Z не является общим признаком успеха
                ; Corrupt:
                ;   BC, AF, AF' на успешном пути, IY, R, выбранная запись при успехе, операнды настроечного префикса и SP снятием возврата
                ; Note:
                ;   сам вход не изменяет четыре настроенных операнда, затраты префикса равны нулю
                ;   State существующей записи 1..127 занят, 0 свободен, #80..#FF завершает поиск, исходная запись IY пропускается
                ;   успешный поиск записывает FramePointer и FirstFrame из HL, FrameStride из DE и FrameCount=1
                ;   новый State=0 либо отрицательный State допускается, указанный положительный либо отрицательный признак относится только к поиску старых записей
                ;   неудача не отменяет выполненную до поиска настройку операндов, временных записей CPU-стека внутри четырёх входов нет
                ;   AllocateEffect требует 49+7*n M1 при успехе либо 7+7*n при отрицательном ограничителе, префикс добавляется отдельно
                ;   R увеличивает младшие семь битов на число M1 modulo 128, старший сохраняется
                ;   6144 сценария проверяют четыре входа, 0, 1 и 7 занятых записей, все наблюдаемые Mode/State и оба исхода
                ;   проверены все регистры кроме времени, восемь банков RAM и кратности записей, полное совместное пространство и нативная игра не доказаны
; -----------------------------------------
                ; поиск свободной записи с шагом исходной структуры FVisualEffect
Entry:          LD BC, FVisualEffect
                ; переход к следующей записи до проверки её состояния, исходная запись пропускается
FindFree:       ADD IY, BC
                LD A, (IY + FVisualEffect.State)
                AND A
                RET M                                                           ; выход, если поле State отрицательно и достигнут ограничитель списка


                JR NZ, @Voxel.AllocateEffect.FindFree                           ; переход, если запись занята и нужно проверить следующую


                ; сохранение альтернативных HL, DE и BC в SavedHL, SavedDE и SavedBC
                EXX
                LD (IY + FVisualEffect.SavedHL), L
                LD (IY + FVisualEffect.SavedHL + 1), H
                LD (IY + FVisualEffect.SavedDE), E
                LD (IY + FVisualEffect.SavedDE + 1), D
                LD (IY + FVisualEffect.SavedBC), C
                LD (IY + FVisualEffect.SavedBC + 1), B
                ; получение признака состояния из альтернативного A, обратный обмен AF не выполняется
                EX AF, AF'
                LD (IY + FVisualEffect.State), A
                EXX
                ; инициализация режима, ресурса, его текущего указателя и параметров выбранного варианта
SetMode:        LD (IY + FVisualEffect.Mode), #00
                LD (IY + FVisualEffect.FramePointer), L
                LD (IY + FVisualEffect.FramePointer + 1), H
                LD (IY + FVisualEffect.FirstFrame), L
                LD (IY + FVisualEffect.FirstFrame + 1), H
                LD (IY + FVisualEffect.FrameCount), #01
LoadReload:     LD A, #00
                LD (IY + FVisualEffect.FrameReload), A
                LD (IY + FVisualEffect.FrameStride), E
                LD (IY + FVisualEffect.FrameStride + 1), D
SetWidth:       LD (IY + FVisualEffect.FrameWidth), #00
SetHeight:      LD (IY + FVisualEffect.FrameHeight), #00
                RET


                endmodule
                endmodule
