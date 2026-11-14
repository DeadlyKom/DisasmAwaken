                module ArchiveFighterRules
                ; Документация [правила действий](../../../Docs/FighterAssets.md#клавиши-и-выбор-действия)
Action00:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For00And01                             ; Target, блок правил запроса #00
                }
Action01:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For00And01                             ; Target, блок правил запроса #01
                }
Action02:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For02                                  ; Target, блок правил запроса #02
                }
Action03:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For03                                  ; Target, блок правил запроса #03
                }
Action04:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For04And05And12                        ; Target, блок правил запроса #04
                }
Action05:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For04And05And12                        ; Target, блок правил запроса #05
                }
Action06:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #06
                }
Action07:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For07                                  ; Target, блок правил запроса #07
                }
Action08:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For08                                  ; Target, блок правил запроса #08
                }
Action09:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For09                                  ; Target, блок правил запроса #09
                }
Action0A:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #0A
                }
Action0B:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For0B                                  ; Target, блок правил запроса #0B
                }
Action0C:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #0C
                }
Action0D:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #0D
                }
Action0E:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #0E
                }
Action0F:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #0F
                }
Action10:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #10
                }
Action11:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #11
                }
Action12:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For04And05And12                        ; Target, блок правил запроса #12
                }
Action13:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #13
                }
Action14:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #14
                }
Action15:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #15
                }
Action16:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For16                                  ; Target, блок правил запроса #16
                }
Action17:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #17
                }
Action18:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.For18                                  ; Target, блок правил запроса #18
                }
Action19:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #19
                }
Action1A:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #1A
                }
Action1B:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #1B
                }
Action1C:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #1C
                }
Action1D:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #1D
                }
Action1E:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #1E
                }
Action1F:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #1F
                }
Action20:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #20
                }
Action21:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #21
                }
Action22:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #22
                }
Action23:       FArchiveInputRulePointer {
                    @ArchiveFighterRules.NoRules                                ; Target, блок правил запроса #23
                }

For00And01:     FArchiveInputRuleCount {
                    #0E                                                         ; Count, число правил в порядке проверки
                }
Rule00:         FArchiveInputRule {
                    #05,                                                        ; PrimaryMask
                    #05,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #07                                                         ; Action
                }
Rule01:         FArchiveInputRule {
                    #09,                                                        ; PrimaryMask
                    #09,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #08                                                         ; Action
                }
Rule02:         FArchiveInputRule {
                    #10,                                                        ; PrimaryMask
                    #10,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #09                                                         ; Action
                }
Rule03:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #01,                                                        ; ExtraMask
                    #01,                                                        ; ExtraValue
                    #0C                                                         ; Action
                }
Rule04:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #02,                                                        ; ExtraMask
                    #02,                                                        ; ExtraValue
                    #0D                                                         ; Action
                }
Rule05:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #04,                                                        ; ExtraMask
                    #04,                                                        ; ExtraValue
                    #0E                                                         ; Action
                }
Rule06:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #08,                                                        ; ExtraMask
                    #08,                                                        ; ExtraValue
                    #0F                                                         ; Action
                }
Rule07:         FArchiveInputRule {
                    #08,                                                        ; PrimaryMask
                    #08,                                                        ; PrimaryValue
                    #08,                                                        ; ExtraMask
                    #08,                                                        ; ExtraValue
                    #14                                                         ; Action
                }
Rule08:         FArchiveInputRule {
                    #08,                                                        ; PrimaryMask
                    #08,                                                        ; PrimaryValue
                    #04,                                                        ; ExtraMask
                    #04,                                                        ; ExtraValue
                    #15                                                         ; Action
                }
Rule09:         FArchiveInputRule {
                    #04,                                                        ; PrimaryMask
                    #04,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #01                                                         ; Action
                }
Rule0A:         FArchiveInputRule {
                    #08,                                                        ; PrimaryMask
                    #08,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #02                                                         ; Action
                }
Rule0B:         FArchiveInputRule {
                    #01,                                                        ; PrimaryMask
                    #01,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #03                                                         ; Action
                }
Rule0C:         FArchiveInputRule {
                    #02,                                                        ; PrimaryMask
                    #02,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #04                                                         ; Action
                }
Rule0D:         FArchiveInputRule {
                    #FF,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #00                                                         ; Action
                }

For02:          FArchiveInputRuleCount {
                    #04                                                         ; Count, число правил в порядке проверки
                }
Rule0E:         FArchiveInputRule {
                    #08,                                                        ; PrimaryMask
                    #08,                                                        ; PrimaryValue
                    #08,                                                        ; ExtraMask
                    #08,                                                        ; ExtraValue
                    #14                                                         ; Action
                }
Rule0F:         FArchiveInputRule {
                    #08,                                                        ; PrimaryMask
                    #08,                                                        ; PrimaryValue
                    #04,                                                        ; ExtraMask
                    #04,                                                        ; ExtraValue
                    #15                                                         ; Action
                }
Rule10:         FArchiveInputRule {
                    #09,                                                        ; PrimaryMask
                    #09,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #08                                                         ; Action
                }
Rule11:         FArchiveInputRule {
                    #FF,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #00                                                         ; Action
                }

NoRules:        FArchiveInputRuleCount {
                    #00                                                         ; Count, число правил в порядке проверки
                }

For04And05And12:FArchiveInputRuleCount {
                    #08                                                         ; Count, число правил в порядке проверки
                }
Rule12:         FArchiveInputRule {
                    #12,                                                        ; PrimaryMask
                    #12,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #0B                                                         ; Action
                }
Rule13:         FArchiveInputRule {
                    #02,                                                        ; PrimaryMask
                    #02,                                                        ; PrimaryValue
                    #04,                                                        ; ExtraMask
                    #04,                                                        ; ExtraValue
                    #10                                                         ; Action
                }
Rule14:         FArchiveInputRule {
                    #02,                                                        ; PrimaryMask
                    #02,                                                        ; PrimaryValue
                    #08,                                                        ; ExtraMask
                    #08,                                                        ; ExtraValue
                    #11                                                         ; Action
                }
Rule15:         FArchiveInputRule {
                    #02,                                                        ; PrimaryMask
                    #02,                                                        ; PrimaryValue
                    #01,                                                        ; ExtraMask
                    #01,                                                        ; ExtraValue
                    #13                                                         ; Action
                }
Rule16:         FArchiveInputRule {
                    #02,                                                        ; PrimaryMask
                    #02,                                                        ; PrimaryValue
                    #02,                                                        ; ExtraMask
                    #02,                                                        ; ExtraValue
                    #13                                                         ; Action
                }
Rule17:         FArchiveInputRule {
                    #06,                                                        ; PrimaryMask
                    #04,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #01                                                         ; Action
                }
Rule18:         FArchiveInputRule {
                    #0A,                                                        ; PrimaryMask
                    #08,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #02                                                         ; Action
                }
Rule19:         FArchiveInputRule {
                    #FF,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #06                                                         ; Action
                }

For09:          FArchiveInputRuleCount {
                    #02                                                         ; Count, число правил в порядке проверки
                }
Rule1A:         FArchiveInputRule {
                    #12,                                                        ; PrimaryMask
                    #12,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #04                                                         ; Action
                }
Rule1B:         FArchiveInputRule {
                    #FF,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #0A                                                         ; Action
                }

For0B:          FArchiveInputRuleCount {
                    #02                                                         ; Count, число правил в порядке проверки
                }
Rule1C:         FArchiveInputRule {
                    #12,                                                        ; PrimaryMask
                    #02,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #05                                                         ; Action
                }
Rule1D:         FArchiveInputRule {
                    #12,                                                        ; PrimaryMask
                    #10,                                                        ; PrimaryValue
                    #00,                                                        ; ExtraMask
                    #00,                                                        ; ExtraValue
                    #06                                                         ; Action
                }

For16:          FArchiveInputRuleCount {
                    #02                                                         ; Count, число правил в порядке проверки
                }
Rule1E:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #01,                                                        ; ExtraMask
                    #01,                                                        ; ExtraValue
                    #17                                                         ; Action
                }
Rule1F:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #02,                                                        ; ExtraMask
                    #02,                                                        ; ExtraValue
                    #1A                                                         ; Action
                }

For18:          FArchiveInputRuleCount {
                    #02                                                         ; Count, число правил в порядке проверки
                }
Rule20:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #01,                                                        ; ExtraMask
                    #01,                                                        ; ExtraValue
                    #19                                                         ; Action
                }
Rule21:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #02,                                                        ; ExtraMask
                    #02,                                                        ; ExtraValue
                    #1B                                                         ; Action
                }

For03:          FArchiveInputRuleCount {
                    #04                                                         ; Count, число правил в порядке проверки
                }
Rule22:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #01,                                                        ; ExtraMask
                    #01,                                                        ; ExtraValue
                    #1C                                                         ; Action
                }
Rule23:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #02,                                                        ; ExtraMask
                    #02,                                                        ; ExtraValue
                    #1C                                                         ; Action
                }
Rule24:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #04,                                                        ; ExtraMask
                    #04,                                                        ; ExtraValue
                    #1F                                                         ; Action
                }
Rule25:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #08,                                                        ; ExtraMask
                    #08,                                                        ; ExtraValue
                    #1F                                                         ; Action
                }

For07:          FArchiveInputRuleCount {
                    #04                                                         ; Count, число правил в порядке проверки
                }
Rule26:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #01,                                                        ; ExtraMask
                    #01,                                                        ; ExtraValue
                    #1D                                                         ; Action
                }
Rule27:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #02,                                                        ; ExtraMask
                    #02,                                                        ; ExtraValue
                    #1D                                                         ; Action
                }
Rule28:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #04,                                                        ; ExtraMask
                    #04,                                                        ; ExtraValue
                    #20                                                         ; Action
                }
Rule29:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #08,                                                        ; ExtraMask
                    #08,                                                        ; ExtraValue
                    #20                                                         ; Action
                }

For08:          FArchiveInputRuleCount {
                    #04                                                         ; Count, число правил в порядке проверки
                }
Rule2A:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #01,                                                        ; ExtraMask
                    #01,                                                        ; ExtraValue
                    #1E                                                         ; Action
                }
Rule2B:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #02,                                                        ; ExtraMask
                    #02,                                                        ; ExtraValue
                    #1E                                                         ; Action
                }
Rule2C:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #04,                                                        ; ExtraMask
                    #04,                                                        ; ExtraValue
                    #21                                                         ; Action
                }
Rule2D:         FArchiveInputRule {
                    #00,                                                        ; PrimaryMask
                    #00,                                                        ; PrimaryValue
                    #08,                                                        ; ExtraMask
                    #08,                                                        ; ExtraValue
                    #21                                                         ; Action
                }
                endmodule
