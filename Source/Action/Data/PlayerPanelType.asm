                module ActionPlayerPanelType
                ; Документация [исходное объявление PLAYER](../../../Docs/ActionPanelPhysicalData.md#архивное-объявление-player)
                assert $ == #A791
                ; -----------------------------------------
                ; исходная физическая запись Initial
Initial:        FArchivedPlayerPanelType {
                    #00,                                                        ; Byte0, исходный ноль после скорости, назначение неизвестно
                    #FF,                                                        ; TypeCode, полный класс игрока, большой эффект выбирает маску и допуск дочерних записей
                    #00                                                         ; Byte2, исходный ноль перед SHILD, назначение неизвестно
                }
                assert $ == #A794
                endmodule
