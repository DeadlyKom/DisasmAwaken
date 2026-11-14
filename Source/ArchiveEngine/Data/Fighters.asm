                module ArchiveFighters
                ; Документация [физическая запись бойца](../../../Docs/FighterAssets.md#физические-записи-бойцов)
First:          FArchiveEngineFighter {
                    #00,                                                        ; Side, сторона бойца
                    {                                                           ; FrameSource, адрес кадра
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    {                                                           ; FrameDest, адрес рабочего растра
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    #00,                                                        ; Request, запрошенное действие
                    #FF,                                                        ; LoadedAction, FF требует первичной загрузки
                    #00,                                                        ; PreviousWidth, ширина прежнего кадра
                    #00,                                                        ; Unknown08, назначение не установлено
                    #00,                                                        ; PreviousHeight, высота прежнего кадра
                    #00,                                                        ; Unknown0A, назначение не установлено
                    {                                                           ; PreviousAddress, прежний адрес рисования
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    {                                                           ; BarBase, база таблицы BAR
                        #00,                                                    ; Low
                        #C0                                                     ; High
                    },
                    #00,                                                        ; StepIndex, номер шага
                    #00,                                                        ; StepTicks, задержка шага
                    #00,                                                        ; FrameWidth, ширина кадра
                    #00,                                                        ; FrameHeight, высота кадра
                    #00,                                                        ; PreviousMirror, сторона предыдущего кадра
                    #25,                                                        ; PositionX, начальный X
                    #0C,                                                        ; PositionY, начальный Y
                    #00,                                                        ; PreviousY, прежняя рисуемая строка
                    #00,                                                        ; SpriteBank, индекс BD
                    #00,                                                        ; StepCount, число шагов
                    {                                                           ; Steps, адрес шагов
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    #23,                                                        ; DrawX, начальный рисуемый X
                    #00,                                                        ; DrawY, рисуемая строка
                    #00,                                                        ; ActionFlags, флаг, бит 6 задаёт повтор
                    {                                                           ; Primary0, W, прыжок
                        #FBFE,                                                  ; Port
                        #02                                                     ; Mask
                    },
                    {                                                           ; Primary1, S, приседание
                        #FDFE,                                                  ; Port
                        #02                                                     ; Mask
                    },
                    {                                                           ; Primary2, D, движение вправо
                        #FDFE,                                                  ; Port
                        #04                                                     ; Mask
                    },
                    {                                                           ; Primary3, A, движение влево
                        #FDFE,                                                  ; Port
                        #01                                                     ; Mask
                    },
                    {                                                           ; Primary4, V, блок
                        #FEFE,                                                  ; Port
                        #10                                                     ; Mask
                    },
                    {                                                           ; Mirror0, клавиша W
                        #FBFE,                                                  ; Port
                        #02                                                     ; Mask
                    },
                    {                                                           ; Mirror1, клавиша S
                        #FDFE,                                                  ; Port
                        #02                                                     ; Mask
                    },
                    {                                                           ; Mirror2, клавиша A
                        #FDFE,                                                  ; Port
                        #01                                                     ; Mask
                    },
                    {                                                           ; Mirror3, клавиша D
                        #FDFE,                                                  ; Port
                        #04                                                     ; Mask
                    },
                    {                                                           ; Mirror4, клавиша V
                        #FEFE,                                                  ; Port
                        #10                                                     ; Mask
                    },
                    {                                                           ; Extra0, C, нижний удар рукой
                        #FEFE,                                                  ; Port
                        #08                                                     ; Mask
                    },
                    {                                                           ; Extra1, F, верхний удар рукой
                        #FDFE,                                                  ; Port
                        #08                                                     ; Mask
                    },
                    {                                                           ; Extra2, B, нижний удар ногой
                        #7FFE,                                                  ; Port
                        #10                                                     ; Mask
                    },
                    {                                                           ; Extra3, G, верхний удар ногой
                        #FDFE,                                                  ; Port
                        #10                                                     ; Mask
                    },
                    #00,                                                        ; RepeatStep, шаг повтора
                    #00,                                                        ; PrimaryBits, пока нет основных нажатий
                    #00,                                                        ; ExtraBits, пока нет дополнительных нажатий
                    {                                                           ; Rules, таблица правил перехода
                        LOW(@ArchiveFighterRules.Action00),                     ; Low
                        HIGH(@ArchiveFighterRules.Action00)                     ; High
                    },
                    #00,                                                        ; FramePending, ожидание шага
                    #00,                                                        ; PreviousExtra, предыдущие дополнительные нажатия
                    #00,                                                        ; NextAction, следующее действие
                    {                                                           ; MoveX, знаковое смещение
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    #00                                                         ; TurnPending, отложенный разворот
                }

Second:         FArchiveEngineFighter {
                    #01,                                                        ; Side, сторона бойца
                    {                                                           ; FrameSource, адрес кадра
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    {                                                           ; FrameDest, адрес рабочего растра
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    #00,                                                        ; Request, запрошенное действие
                    #FF,                                                        ; LoadedAction, FF требует первичной загрузки
                    #00,                                                        ; PreviousWidth, ширина прежнего кадра
                    #00,                                                        ; Unknown08, назначение не установлено
                    #00,                                                        ; PreviousHeight, высота прежнего кадра
                    #00,                                                        ; Unknown0A, назначение не установлено
                    {                                                           ; PreviousAddress, прежний адрес рисования
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    {                                                           ; BarBase, база таблицы BAR
                        #00,                                                    ; Low
                        #D0                                                     ; High
                    },
                    #00,                                                        ; StepIndex, номер шага
                    #00,                                                        ; StepTicks, задержка шага
                    #00,                                                        ; FrameWidth, ширина кадра
                    #00,                                                        ; FrameHeight, высота кадра
                    #00,                                                        ; PreviousMirror, сторона предыдущего кадра
                    #34,                                                        ; PositionX, начальный X
                    #0C,                                                        ; PositionY, начальный Y
                    #00,                                                        ; PreviousY, прежняя рисуемая строка
                    #00,                                                        ; SpriteBank, индекс BD
                    #00,                                                        ; StepCount, число шагов
                    {                                                           ; Steps, адрес шагов
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    #36,                                                        ; DrawX, начальный рисуемый X
                    #00,                                                        ; DrawY, рисуемая строка
                    #00,                                                        ; ActionFlags, флаг, бит 6 задаёт повтор
                    {                                                           ; Primary0, 7, прыжок
                        #EFFE,                                                  ; Port
                        #08                                                     ; Mask
                    },
                    {                                                           ; Primary1, U, приседание
                        #DFFE,                                                  ; Port
                        #08                                                     ; Mask
                    },
                    {                                                           ; Primary2, I, движение вправо
                        #DFFE,                                                  ; Port
                        #04                                                     ; Mask
                    },
                    {                                                           ; Primary3, Y, движение влево
                        #DFFE,                                                  ; Port
                        #10                                                     ; Mask
                    },
                    {                                                           ; Primary4, Enter, блок
                        #BFFE,                                                  ; Port
                        #01                                                     ; Mask
                    },
                    {                                                           ; Mirror0, клавиша 7
                        #EFFE,                                                  ; Port
                        #08                                                     ; Mask
                    },
                    {                                                           ; Mirror1, клавиша U
                        #DFFE,                                                  ; Port
                        #08                                                     ; Mask
                    },
                    {                                                           ; Mirror2, клавиша Y
                        #DFFE,                                                  ; Port
                        #10                                                     ; Mask
                    },
                    {                                                           ; Mirror3, клавиша I
                        #DFFE,                                                  ; Port
                        #04                                                     ; Mask
                    },
                    {                                                           ; Mirror4, клавиша Enter
                        #BFFE,                                                  ; Port
                        #01                                                     ; Mask
                    },
                    {                                                           ; Extra0, K, нижний удар рукой
                        #BFFE,                                                  ; Port
                        #04                                                     ; Mask
                    },
                    {                                                           ; Extra1, O, верхний удар рукой
                        #DFFE,                                                  ; Port
                        #02                                                     ; Mask
                    },
                    {                                                           ; Extra2, L, нижний удар ногой
                        #BFFE,                                                  ; Port
                        #02                                                     ; Mask
                    },
                    {                                                           ; Extra3, P, верхний удар ногой
                        #DFFE,                                                  ; Port
                        #01                                                     ; Mask
                    },
                    #00,                                                        ; RepeatStep, шаг повтора
                    #00,                                                        ; PrimaryBits, пока нет основных нажатий
                    #00,                                                        ; ExtraBits, пока нет дополнительных нажатий
                    {                                                           ; Rules, таблица правил перехода
                        LOW(@ArchiveFighterRules.Action00),                     ; Low
                        HIGH(@ArchiveFighterRules.Action00)                     ; High
                    },
                    #00,                                                        ; FramePending, ожидание шага
                    #00,                                                        ; PreviousExtra, предыдущие дополнительные нажатия
                    #00,                                                        ; NextAction, следующее действие
                    {                                                           ; MoveX, знаковое смещение
                        #00,                                                    ; Low
                        #00                                                     ; High
                    },
                    #00                                                         ; TurnPending, отложенный разворот
                }

                endmodule
