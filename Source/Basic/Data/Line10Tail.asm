                module BasicProgramLine10Tail
                ; Документация [исходная BASIC-программа](../../../Docs/BasicProgram.md)
                assert $ == #5D59
Padding:        ds 70, #20                                                      ; семьдесят исходных пробелов внутри REM, байты не удаляются
EndLine:        db #0D                                                          ; завершение первой строки BASIC
                assert $ == #5DA0
                endmodule
