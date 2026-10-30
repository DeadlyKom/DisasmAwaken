                module Station
                module SetBandFillMode
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [самомодификация режима полосовой рамки](../../Docs/StationSpans.md)
; -----------------------------------------
; Настройка заполненного либо обычного режима полосовой рамки по биту 0 FillMode
; исходная запись 4, файловые смещения #6CAF..#6CD3
; In:
;   AF - входной Carry участвует в старшем бите результата A, S, Z, PV сохраняются
;   StationRaster.FillMode - бит 0 выбирает обычный режим при единице, заполненный при нуле
;   код станционной страницы и шесть изменяемых операндов доступны для записи
; Out:
;   HL и BC сохранены, DE=#C1ED при обычном режиме, иначе DE=#C1CF
;   AF - A=(FillMode SHR 1) OR (входной Carry SHL 7), Carry=исходный бит 0 FillMode
;   F имеет S, Z, PV входного F, биты 5 и 3 от выходного A, H=N=0
;   шесть операндов переведены в выбранный режим, сам FillMode и текущий BandPattern не меняются
; Corrupt:
;   DE, AF
; Note:
;   альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   SetBandFillMode при бите 0 FillMode переходит в ResetBandMode, дополнительного CALL не создаёт
;   восстановление всегда задаёт исходный режим, не сохраняет произвольные прежние цели
;   эффект относится к последующим DrawBandFrame, рамка и пиксели здесь не рисуются
; -----------------------------------------
                ; выбор обычного установщика для строки 11 перед чтением режима заливки
Entry:          LD DE, @Station.SetOutlinePattern.Entry
                ; проверка бита 0 FillMode с сохранением остальных разрядов в результате RRA
                LD A, (@StationRaster.FillMode)
                RRA
                JR C, @Station.ResetBandMode.Entry                              ; переход, если бит 0 FillMode установлен, восстановить обычный режим рамки

                ; сохранение обычной боковой линии 11 и выбор заполненного узора для остальных изменяемых участков
                LD (@StationRaster.BandLine11), DE
                LD DE, @Station.SetCutoutPattern.Entry
                LD (@StationRaster.BandBottom0), DE
                LD (@StationRaster.BandLine12), DE
                LD (@StationRaster.BandSides), DE
                LD (@StationRaster.BandBottom1), DE
                LD (@StationRaster.BandDefault), DE
                RET

                endmodule
                endmodule
