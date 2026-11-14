                module Intro
                module PresentAttributes
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Документация [алгоритм и проверка](../../Docs/IntroPresentAttributes.md)
                ; Особый контекст [IY столбцового эффекта](../../Docs/IntroGeneratedEffects.md#iy-столбцового-вывода-и-перенос-frames)
; -----------------------------------------
; Ожидание кадра, выбор таблицы #60C0 либо #61C0 и вызов генерируемого писателя
; исходная запись 3, файловые смещения #0683..#0692
                ; In:
                ;   HL, DE, BC и AF содержат сохраняемый до IRQ контекст, затем HL и AF становятся выходными значениями
                ;   IM=1, IFF=1, IY=5C3A, проверенный 48K ROM, клавиши не нажаты и KSTATE по 5C00 и 5C04 равны FF
                ;   FramePhase содержит байт выбора матрицы, FirstMatrix и SecondMatrix содержат по 32 слова
                ;   код 68A9..6928 создан BuildAttributeWriter, проверены назначения с исходным IXL=80 либо C0
                ;   SP указывает внешний возврат, 14 байтов ниже него доступны для IM 1, назначения не пересекаются с кодом, матрицами и CPU-стеком
                ;   HALT принимает ближайший периодический IRQ, до завершения писателя следующий IRQ не принимается
                ; Out:
                ;   HL - последнее слово выбранной матрицы, DE и BC сохранены, A=FramePhase, F от OR A этого байта
                ;   HL', DE', BC', AF', IX и IY сохраняются, I и IM сохраняются, IFF остаётся равным единице
                ;   при FramePhase=0 выбрана FirstMatrix по 60C0, при любом ненулевом байте выбрана SecondMatrix по 61C0
                ;   64 байта матрицы записаны по 32 адресам созданного писателя, SavedSP содержит входной CPU SP
                ;   FRAMES увеличен на один modulo 16777216, SP после RET равен входному SP+2
                ; Corrupt:
                ;   HL, AF, R, FRAMES, SavedSP, 64 байта назначений и 14 временных байтов ниже входного SP
                ; Note:
                ;   вызовы из InitializeColumnEffect, InitializeLookupEffect и InitializeScrolledTexture при исходном 69A2=FF приходят с IY=5C0F, отдельные контексты и запись 5C4F описаны в IntroGeneratedEffects.md
                ;   это самостоятельный дополнительный вход, а не продолжение CombineAttributeNibbles
                ;   HALT требует разрешённых IRQ на входе, сам вход EI и DI не выполняет
                ;   ROM после IRQ возвращает IFF=1, писатель завершается в том же кадре и не запрещает прерывания
                ;   1536 сценариев исполнили настоящий ROM, периодический планировщик и созданные POP/LD при всех байтах FramePhase, двух назначениях и трёх фазах времени
                ;   в проверенном периоде 69888 не было IRQ во время временного SP, все регистры кроме R, восемь банков RAM и кратность записей совпали
                ;   другие ROM, клавиши, KSTATE, периоды IRQ, NMI, точное время и нативный показ не доказаны
                ; -----------------------------------------
                ; Ожидание ближайшего IRQ с уже разрешённым IFF, ROM сохранит регистры и вернёт IFF=1.
Entry:          HALT
                ; Проверка байта фазы после IRQ, ноль выбирает первую матрицу, остальные значения вторую.
                LD A, (@IntroAttrState.FramePhase)
                OR A
                LD HL, @IntroAttrConst.FirstMatrix
                JR Z, @Intro.PresentAttributes.WriteSelected                    ; переход, если FramePhase равен нулю и выбрана FirstMatrix


                LD HL, @IntroAttrConst.SecondMatrix
                ; Передача управления писателю без дополнительного адреса возврата на CPU-стеке.
WriteSelected:  JP @Intro.RunAttributeWriter.Entry


                endmodule
                endmodule
