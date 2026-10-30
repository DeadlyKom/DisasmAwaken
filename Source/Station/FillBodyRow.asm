                module Station
                module FillBodyRow
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [иконка, внутреннее тело и заимствованный стек](../../Docs/WindowGraphics.md)
; -----------------------------------------
; Развёрнутая запись до 30 байтов одной строки с восстановлением младшего адреса и RET
; исходная запись 4, файловые смещения #40C4..#4101
; In:
;   HL - сохраняемый адрес выбранного входа, DE - экранный адрес первой записи, BC - C содержит исходный E
;   AF - A байт заливки, входной Carry сохраняется в итоговых флагах
;   на стеке адрес следующего участка, запись экрана не перекрывает код и используемую цепочку
; Out:
;   HL и BC сохранены, A сохранён, D=(входной D+1) AND #FF,E=входной C
;   F соответствует INC исходного D с сохранением входного Carry, остальные изменяемые флаги от последнего INC D
;   с Entry записаны 30 байтов, с WriteN записаны N байтов, с ZeroBytes ни одного
; Corrupt:
;   DE, AF
; Note:
;   каждый адрес записи сохраняет исходный старший байт, младший увеличивается по модулю 256 без переноса в D
;   последняя запись не имеет INC E, затем E восстанавливается из C и D увеличивается
;   ZeroBytes входит непосредственно в INC D, поэтому заранее требуется C=E
;   альтернативные и индексные регистры, I и IFF сохраняются, RET потребляет одно слово таблицы либо обычный возврат
; -----------------------------------------
                ; запись 30 байтов полного входа, укороченные входы пропускают первые пары
Entry:          LD (DE), A
                INC E
Write29:        LD (DE), A
                INC E
Write28:        LD (DE), A
                INC E
Write27:        LD (DE), A
                INC E
Write26:        LD (DE), A
                INC E
Write25:        LD (DE), A
                INC E
Write24:        LD (DE), A
                INC E
Write23:        LD (DE), A
                INC E
Write22:        LD (DE), A
                INC E
Write21:        LD (DE), A
                INC E
Write20:        LD (DE), A
                INC E
Write19:        LD (DE), A
                INC E
Write18:        LD (DE), A
                INC E
Write17:        LD (DE), A
                INC E
Write16:        LD (DE), A
                INC E
Write15:        LD (DE), A
                INC E
Write14:        LD (DE), A
                INC E
Write13:        LD (DE), A
                INC E
Write12:        LD (DE), A
                INC E
Write11:        LD (DE), A
                INC E
Write10:        LD (DE), A
                INC E
Write9:         LD (DE), A
                INC E
Write8:         LD (DE), A
                INC E
Write7:         LD (DE), A
                INC E
Write6:         LD (DE), A
                INC E
Write5:         LD (DE), A
                INC E
Write4:         LD (DE), A
                INC E
Write3:         LD (DE), A
                INC E
Write2:         LD (DE), A
                INC E
Write1:         LD (DE), A
                ; восстановление младшего адреса после последней записи без лишнего INC E
RestoreLow:     LD E, C
                ; расчёт старшего адреса следующей пиксельной строки, этот вход также обслуживает нулевую ширину
ZeroBytes:      INC D
                RET

                endmodule
                endmodule
