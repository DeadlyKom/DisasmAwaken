                module PointerBackground
; Документация [указатель](../../../Docs/Pointer.md)
; исходные значения, во время работы каждая запись хранит два экранных байта
                assert $ == #6575
Row0:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
Row1:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
Row2:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
Row3:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
Row4:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
Row5:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
Row6:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
Row7:           FPointerSavedRow {
                    #00,                                                        ; FPointerSavedRow.Left
                    #00                                                         ; FPointerSavedRow.Right
                }
                assert $ == #6585
                endmodule
