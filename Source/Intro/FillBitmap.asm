                module Intro
                module FillBitmap
                ; Документация [точная заливка 128 строк](../../Docs/IntroBitmapFill.md)
                ; Имена внутренних входов [алгоритмы вступления](../../Docs/IntroInternalLabels.md)
                ; -----------------------------------------
                ; Заполнение 128 экранных строк байтом C с учётом адресации Spectrum
                ; исходная запись 3, файловые смещения #0767..#07C0
                ; In:
                ;   BC содержит C, байтовый заполнитель первых 128 строк bitmap, входной B не используется
                ;   INTRO загружен по исходным адресам, экран 4000..4FFF доступен для записи
                ;   CPU-стек с адресом возврата не пересекает заполняемую область и код, IRQ/NMI исключены
                ; Out:
                ;   HL=5000, DE содержит сохранённый D и E=E0, BC содержит B=0 и сохранённый C
                ;   AF=0041, Z и Carry установлены последним переходом строки, N/H/PV и биты 5/3 сброшены
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохранены, SP после RET равен входному+2
                ;   первые 128 экранных строк 4000..4FFF заполнены C, каждый из 4096 байтов записан ровно один раз
                ;   R получает 9069 M1 с сохранением бита 7, CPU-стек не записывается
                ; Corrupt:
                ;   HL, DE, BC, AF, R, bitmap 4000..4FFF
                ; Note:
                ;   атрибуты и последние 64 экранные строки не затрагиваются
                ;   на каждую строку приходится 32 развёрнутые записи, L восстанавливается перед переходом ULA
                ;   младший экранный адрес меняется на 20 после каждых восьми строк, переполнение различает переход части экрана
                ;   проверка относится к плоскому загруженному INTRO без аппаратных прерываний, точные T не проверены
                ; -----------------------------------------
Entry:          LD HL, #4000
                LD B, #80
FillScanline:   LD E, L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                INC L
                LD (HL), C
                LD L, E
                INC H
                LD A, H
                AND #07
                JP NZ, @Intro.FillBitmap.CountScanline                          ; переход, если следующая строка остаётся внутри восьмистрочного знакоместа


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Intro.FillBitmap.CountScanline                           ; переход, если переход к следующему знакоместу переполнил L


                LD A, H
                SUB #08
                LD H, A
CountScanline:  DJNZ @Intro.FillBitmap.FillScanline

                RET


                endmodule
                endmodule
