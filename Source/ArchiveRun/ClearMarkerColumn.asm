                module ArchiveRun
                module ClearMarkerColumn
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; очистка восьми вертикальных байтов стрелки в выбранном экране
                ; In:
                ;   HL - первый байт стрелки на выровненной знакоместной строке
                ; Out:
                ;   восемь байтов обнулены, H продвинут на восемь
                ; Corrupt:
                ;   HL, AF
                ; -----------------------------------------
                ; очистка одного столбца растра с шагом #100
Entry:          XOR A
                LD (HL), A
                INC H
                LD (HL), A
                INC H
                LD (HL), A
                INC H
                LD (HL), A
                INC H
                LD (HL), A
                INC H
                LD (HL), A
                INC H
                LD (HL), A
                INC H
                LD (HL), A
                INC H
                RET

                endmodule
                endmodule
