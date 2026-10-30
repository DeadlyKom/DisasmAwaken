                module Music
                module RenderChannelA
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Начало кадрового синтеза канала A, сэмпл, орнамент, тон, шум и амплитуда
; исходная запись 10, файловые смещения #04E3..#05AF
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   байт разрешения канала находится в операнде #DFEF, #FF означает обход расчёта амплитуды
;   обычный расчёт использует временный SP для заголовка и шага сэмпла, затем для орнамента и таблицы нот
;   итоговый тон канала A записывается в #DC00, амплитуда в #DC08 через общий хвост
;   SP сохраняется в операнде #E30E и восстанавливается до вывода регистров AY
; -----------------------------------------
                ; начало синтеза канала A, подготовка общего накопителя и сохранение настоящего стека
Entry:          LD L, #00
                EXX
                LD IX, #0000
                LD (#E30E), SP
                LD A, #FF
                LD H, A
                INC A
                JP Z, @Music.UnknownE0CD.PointE0D3                              ; переход, если флаг Z установлен


                LD SP, #0000
                POP DE
                LD A, #00
                LD L, A
                INC A
                CP D
                JR C, @Music.RenderChannelA.PointE001                           ; переход, если флаг Carry установлен


                LD A, E
PointE001:      LD (#DFFA), A
                ADD HL, HL
                SLA L
                ADD HL, SP
                LD SP, HL
                POP DE
                LD A, D
                OR #F0
                LD L, A
                LD A, E
                ADD A, A
                LD A, #00
                JR NC, @Music.RenderChannelA.PointE022                          ; переход, если флаг Carry сброшен


                JP M, @Music.RenderChannelA.PointE01B                           ; переход, если флаг Sign установлен


                SUB #01
                JR @Music.RenderChannelA.PointE01D


PointE01B:      CP #1F
PointE01D:      ADC A, #00
                LD (#E011), A
PointE022:      ADD A, L
                JR C, @Music.RenderChannelA.PointE026                           ; переход, если флаг Carry установлен


                XOR A
PointE026:      CP #10
                JR C, @Music.RenderChannelA.PointE02C                           ; переход, если флаг Carry установлен


                LD A, #0F
PointE02C:      ADD A, #00
                LD L, A
                LD H, #DC
                LD A, (HL)
                SRL E
                JR C, @Music.RenderChannelA.PointE038                           ; переход, если флаг Carry установлен


                OR #00
PointE038:      EX AF, AF'
                LD A, D
                RLCA
                JR C, @Music.RenderChannelA.PointE04B                           ; переход, если флаг Carry установлен


                LD A, #00
                ADD A, E
                BIT 5, D
                JR Z, @Music.RenderChannelA.PointE047                           ; переход, если флаг Z установлен


                LD (#E03E), A
PointE047:      LD IXH, A
                JR @Music.RenderChannelA.PointE061


PointE04B:      LD A, E
                AND #1F
                CP #10
                JR C, @Music.RenderChannelA.PointE054                           ; переход, если флаг Carry установлен


                OR #F0
PointE054:      ADD A, #00
                BIT 5, D
                JR Z, @Music.RenderChannelA.PointE05D                           ; переход, если флаг Z установлен


                LD (#E055), A
PointE05D:      EXX
                ADD A, L
                LD L, A
                EXX
PointE061:      LD A, D
                RLCA
                RLCA
                RLCA
                RLCA
                AND #09
                LD IXL, A
                POP BC
                LD HL, #0000
                ADD HL, BC
                BIT 6, D
                JR Z, @Music.RenderChannelA.PointE076                           ; переход, если флаг Z установлен


                LD (#E06C), HL
PointE076:      EX DE, HL
                LD SP, #0000
                POP BC
                LD A, #00
                LD L, A
                INC A
                CP B
                JR C, @Music.RenderChannelA.PointE083                           ; переход, если флаг Carry установлен


                LD A, C
PointE083:      LD (#E07C), A
                LD H, #00
                ADD HL, SP
                LD A, (#E0BB)
                ADD A, (HL)
                ADD A, A
                JR NC, @Music.RenderChannelA.PointE091                          ; переход, если флаг Carry сброшен


                XOR A
PointE091:      LD L, A
                LD H, #DD
                LD SP, HL
                POP HL
                ADD HL, DE
                LD BC, #0000
                ADD HL, BC
                LD (#DC00), HL
                LD A, #00
                DEC A
                JP M, @Music.UnknownE0CD.PointE0D2                              ; переход, если флаг Sign установлен


                JR NZ, @Music.UnknownE0CD.PointE0CF                             ; переход, если флаг Z сброшен


                EX DE, HL
                LD HL, #0000
                ADD HL, BC
                LD (#E098), HL
                JR @Music.UnknownE0CD.Entry


                endmodule
                endmodule
