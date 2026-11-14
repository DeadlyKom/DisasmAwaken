                module ArchiveStartModes
                ; Документация [выбор аппаратного режима](../../../Docs/BankStripArchiveConsumer.md)
Targets:        FArchiveEngineModeTargets {
                    @ArchiveStart.SelectPentagonPage.Entry,                     ; режим 0, Pentagon
                    @ArchiveStart.SelectScorpionPage.Entry,                     ; режим 1, Scorpion
                    @ArchiveStart.SelectAtmPage.Entry                           ; режим 2, ATM-2
                }
                endmodule
