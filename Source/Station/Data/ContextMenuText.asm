                module ContextMenuText
; Документация [контекстное меню](../../../Docs/PopupItems.md)
; байты исходного текста, человекочитаемые комментарии декодированы как CP866
                assert $ == #E32E
Entry:          db #91, #AA, #E0, #EB, #E2, #EC, #20, #A2                       ; Скрыть все
                db #E1, #A5, #0D                                                ; продолжение команды и CR
CloseAll:       db #87, #A0, #AA, #E0, #EB, #E2, #EC, #20                       ; Закрыть все
                db #A2, #E1, #A5, #0D                                           ; продолжение команды и CR
RememberEnv:    db #87, #A0, #AF, #AE, #AC, #AD, #A8, #E2                       ; Запомнить среду
                db #EC, #20, #E1, #E0, #A5, #A4, #E3, #0D                       ; продолжение команды и CR
Arrange:        db #90, #A0, #E1, #E1, #E2, #A0, #A2, #A8                       ; Расставить
                db #E2, #EC, #0D                                                ; продолжение команды и CR
EnvOptions:     db #93, #E1, #E2, #A0, #AD, #AE, #A2, #AA                       ; Установки среды
                db #A8, #20, #E1, #E0, #A5, #A4, #EB, #0D                       ; продолжение команды и CR
GameOptions:    db #93, #E1, #E2, #A0, #AD, #AE, #A2, #AA                       ; Установки игры
                db #A8, #20, #A8, #A3, #E0, #EB, #0D                            ; продолжение команды и CR
Restore:        db #82, #AE, #E1, #E1, #E2, #A0, #AD, #AE                       ; Восстановиться
                db #A2, #A8, #E2, #EC, #E1, #EF, #0D                            ; продолжение команды и CR
Save:           db #91, #AE, #E5, #E0, #A0, #AD, #A8, #E2                       ; Сохраниться
                db #EC, #E1, #EF, #0A                                           ; продолжение команды и LF
                assert $ == #E39A
                endmodule
