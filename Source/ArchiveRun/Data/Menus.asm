                module ArchiveRunMenus
                ; Документация [состав обоих списков](../../../Docs/StartArchiveMenu.md)
Memory:         FArchiveRunModeState {
                    #00,                                                        ; Current, исходный Pentagon
                    #03                                                         ; Count, число режимов
                }
PentagonText:   FArchiveRunCaption {
                    @ArchiveRunMenus.PentCaption                                ; Target, режим 0
                }
ScorpionText:   FArchiveRunCaption {
                    @ArchiveRunMenus.ScorpCaption                               ; Target, режим 1
                }
AtmText:        FArchiveRunCaption {
                    @ArchiveRunMenus.AtmCaption                                 ; Target, режим 2
                }

MainCount:      db #03                                                          ; заголовок и два выбираемых пункта
MainHeading:    FArchiveRunMenuItem {
                    @ArchiveRunMenus.EmptyCaption,                              ; Caption, пустой заголовок
                    @ArchiveRun.LoadStartFile.Entry                             ; Handler, заголовок не выбирается
                }
StartItem:      FArchiveRunMenuItem {
                    @ArchiveRunMenus.StartCaption,                              ; Caption, Start
                    @ArchiveRun.LoadStartFile.Entry                             ; Handler, загрузка START
                }
OptionsItem:    FArchiveRunMenuItem {
                    @ArchiveRunMenus.OptionsCaption,                            ; Caption, Options
                    @ArchiveRun.ShowOptions.Entry                               ; Handler, смена списка
                }
EmptyCaption:   db #00                                                          ; нулевой терминатор без символов
StartCaption:   db "Start", #00                                                 ; подпись запуска
OptionsCaption: db "Options", #00                                               ; подпись настройки

OptionsCount:   db #03                                                          ; заголовок и два выбираемых пункта
OptionsHeading: FArchiveRunMenuItem {
                    @ArchiveRunMenus.OptionsTitle,                              ; Caption, заголовок OPTIONS
                    @ArchiveRun.LoadStartFile.Entry                             ; Handler, заголовок не выбирается
                }
ModeItem:       FArchiveRunMenuItem {
                    @ArchiveRunMenus.PentCaption,                               ; Caption, меняется при смене режима
                    @ArchiveRun.CycleMemoryMode.Entry                           ; Handler, выбор следующего режима
                }
DoneItem:       FArchiveRunMenuItem {
                    @ArchiveRunMenus.DoneCaption,                               ; Caption, DONE!
                    @ArchiveRun.ShowMainMenu.Entry                              ; Handler, возврат к основному списку
                }
OptionsTitle:   db "OPTIONS", #00                                               ; заголовок настройки
PentCaption:    db "256k:Pent", #00                                             ; подпись режима 0
ScorpCaption:   db "256k:Scorp", #00                                            ; подпись режима 1
AtmCaption:     db "256k:ATM-2", #00                                            ; подпись режима 2
DoneCaption:    db "DONE!", #00                                                 ; возврат
                endmodule
