                module Station
                module ResetBandMode
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [самомодификация режима полосовой рамки](../../Docs/StationSpans.md)
; -----------------------------------------
; Восстановление шести исходных операндов обычной полосовой рамки
; исходная запись 4, файловые смещения #6CD4..#6CF2
; In:
;   шесть слов StationRaster для обычной полосовой рамки доступны для записи
; Out:
;   HL и BC сохранены, DE=#C1ED, AF сохранён побитно
;   шесть операндов восстановлены, StationRaster.FillMode и BandPattern не меняются
; Corrupt:
;   DE
; Note:
;   альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   восстанавливается фиксированный обычный набор, прежние значения не читаются
;   режим нужен последующим рисователям, текущие пиксели не меняются
; -----------------------------------------
                ; восстановление обычных боковых узоров в шести исходных операндах
Entry:          LD DE, @Station.SetOutlinePattern.Entry
                LD (@StationRaster.BandSides), DE
                LD (@StationRaster.BandBottom1), DE
                LD (@StationRaster.BandDefault), DE
                LD (@StationRaster.BandLine11), DE
                ; восстановление нулевых разделителей строки 12 и начала нижнего знакоместа
                LD DE, @Station.ClearSpanPattern.Entry
                LD (@StationRaster.BandBottom0), DE
                LD (@StationRaster.BandLine12), DE
                RET

                endmodule
                endmodule
