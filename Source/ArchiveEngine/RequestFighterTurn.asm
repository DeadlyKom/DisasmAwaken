                module ArchiveEngine
                module RequestFighterTurn
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; запрос немедленного либо отложенного разворота бойца
                ; In:
                ;   IX - запись с текущим запросом действия
                ; Out:
                ;   для действий 34 и 35 запрос не меняется
                ;   для 0, 1, 2, 4, 9 и 11 запрашивается 34, для остальных устанавливается TurnPending
                ; Corrupt:
                ;   AF
                ; -----------------------------------------
                ; проверка, что разворот ещё не запрошен и не завершается
Entry:          LD A, (IX + @FArchiveEngineFighter.Request)
                CP #22
                RET Z                                                           ; выход, если уже запрошено начало разворота

                CP #23
                RET Z                                                           ; выход, если запрошено завершение разворота

                ; проверка списка действий, допускающих немедленный переход
                CP #00
                JR Z, @ArchiveEngine.RequestFighterTurn.TurnNow                 ; переход, если действие 0, запросить разворот сейчас

                CP #01
                JR Z, @ArchiveEngine.RequestFighterTurn.TurnNow                 ; переход, если действие 1, запросить разворот сейчас

                CP #02
                JR Z, @ArchiveEngine.RequestFighterTurn.TurnNow                 ; переход, если действие 2, запросить разворот сейчас

                CP #04
                JR Z, @ArchiveEngine.RequestFighterTurn.TurnNow                 ; переход, если действие 4, запросить разворот сейчас

                CP #09
                JR Z, @ArchiveEngine.RequestFighterTurn.TurnNow                 ; переход, если действие 9, запросить разворот сейчас

                CP #0B
                JR Z, @ArchiveEngine.RequestFighterTurn.TurnNow                 ; переход, если действие 11, запросить разворот сейчас

                ; запоминание отложенного разворота
                LD A, #01
                LD (IX + @FArchiveEngineFighter.TurnPending), A
                RET

                ; установка запроса начала разворота
TurnNow:        LD A, #22
                LD (IX + @FArchiveEngineFighter.Request), A
                RET

                endmodule
                endmodule
