"""Точные исходные условия двух клавиатурных писателей SignedWord."""
LAYOUT=((0x7680,0x76A3,'IncreaseGaugeWord','ActionKeyGaugeIncrease'),(0x76A3,0x76C7,'DecreaseGaugeWord','ActionKeyGaugeDecrease'))
CONST_BLOCK='\n                ; Исходные проверки опкода и шага слова шестой шкалы\n                module ActionGaugeKeyConst\n'
for name,value,note in (('MotionOpcode',0x3A,'опкод LD A,(nn) в начале координатной цепочки 6E72'),
    ('StepWord',8,'величина изменения слова по модулю 65536'),('NegAllowBit',4,'бит младшего байта, допускающий уменьшение отрицательного слова')):
    CONST_BLOCK+=name.ljust(16)+('equ #'+format(value,'04X' if name=='StepWord' else '02X')).ljust(64)+'; '+note+'\n'
CONST_BLOCK+='                endmodule\n\n'


def create(start):
    _,end,name,tag=next(row for row in LAYOUT if row[0]==start);increase=start==0x7680
    local={} if increase else {0x76BB:'SubtractStep'}
    notes=['все пары SkipDetail и MotionOpcode проверены для обоих входов, все 65536 слов проверены для уменьшения и семи границ увеличения',
        'все 65536 ограничений проверены отдельно, точные регистры включая R, записи и восемь банков RAM сопоставлены',
        'исходное знаковое условие не заменяется общим насыщением, переполнения слова сохраняются',
        'полное произведение слова и ограничения, игровые единицы, IRQ, точные T, сборка и нативный запуск не доказаны']
    outputs=(
        ['при SkipDetail не ноль A=SkipDetail, F соответствует OR A, HL, DE и BC сохраняются',
         'иначе при MotionOpcode не 3A A=MotionOpcode, F соответствует CP 3A, HL, DE и BC сохраняются',
         'иначе HL=(SignedWord+8) AND FFFF, DE=LimitWord, BC сохранён',
         'если знак обёрнутой разности HL-LimitWord отрицателен, SignedWord=HL, SixthRequest=1 и A=1, иначе память сохранена и A=3A',
         'F сохраняет S/Z/PV от SBC и получает остальные биты от обратного ADD, точная формула приведена в документации',
         'R получает 3, 6, 15 либо 19 M1 в зависимости от пути, бит 7 R сохраняется'] if increase else
        ['при MotionOpcode не 3A A=MotionOpcode, F соответствует CP 3A, HL, DE и BC сохраняются',
         'иначе при SkipDetail не ноль A=SkipDetail, F соответствует AND A, HL, DE и BC сохраняются',
         'иначе HL=SignedWord, DE=8, BC сохранён, отрицательное слово с нулевым битом 4 младшего байта не записывается',
         'при этом отказе A=0, F=54 OR (L AND 28), в остальных случаях HL=(SignedWord-8) AND FFFF',
         'при записи SignedWord=HL, SixthRequest=1, A=1, F соответствует 16-битному вычитанию с Carry=0',
         'R получает 3, 6, 14, 18 либо 21 M1 в зависимости от пути, бит 7 R сохраняется'])
    outputs += ["HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и 7FFD сохраняются, CPU-стек не записывается"]
    contracts={('Action',start):(
        ['HL, DE, BC, AF входных аргументов не задают',
         'SkipDetail, MotionOpcode и SignedWord доступны, '+('LimitWord является стабильным изменяемым операндом этого входа' if increase else 'старшее и младшее слова SignedWord не меняются параллельно'),
         'перенесённый код доступен в фиксированном банке 5, CPU-стек содержит внешний возврат, IRQ не вмешиваются'],
        outputs,['HL, DE, AF, R, при записи SignedWord и SixthRequest'],notes)}
    comments=({
        0x7680:(['Проверка общего запроса SkipDetail, ненулевой байт запрещает увеличение слова.'],None),
        0x7684:([], 'выход, если SkipDetail ненулевой, сохранить слово и запрос шкалы'),
        0x7685:(['Проверка исходного опкода 3A координатной цепочки, остальные байты не допускают изменение.'],None),
        0x768A:([], 'выход, если MotionOpcode отличается от 3A, сохранить слово'),
        0x768B:(['Расчёт кандидата SignedWord+8 по модулю 65536.'],None),
        0x7692:(['Чтение изменяемого LimitWord, исходное значение 0088 может восстанавливаться падающим фронтом запроса.'],None),
        0x7695:(['Проверка знака обёрнутой разности кандидата и ограничения, Carry предварительно очищается.'],None),
        0x7698:(['Восстановление кандидата обратным сложением, флаг Sign остаётся от SBC.'],None),
        0x7699:([], 'выход, если разность кандидата и ограничения неотрицательна по биту 15, сохранить SignedWord'),
        0x769A:(['Обновление SignedWord только после исходной знаковой проверки.'],None),
        0x769D:(['Создание запроса перерисовки шестой шкалы после изменения слова.'],None)} if increase else {
        0x76A3:(['Проверка опкода координатной цепочки до чтения общего запроса.'],None),
        0x76A8:([], 'выход, если MotionOpcode отличается от 3A, сохранить слово'),
        0x76A9:(['Проверка общего запроса SkipDetail через AND A, флаг H отличается от OR увеличивающего входа.'],None),
        0x76AD:([], 'выход, если SkipDetail ненулевой, сохранить слово и запрос шкалы'),
        0x76AE:(['Чтение слова и проверка знака, отрицательная половина имеет дополнительное условие допуска.'],None),
        0x76B6:([], 'переход, если слово неотрицательное, уменьшить его без проверки младшего бита 4'),
        0x76B8:(['Проверка бита 4 младшего байта отрицательного слова, это исходное побитовое условие.'],None),
        0x76BA:([], 'выход, если у отрицательного слова бит 4 младшего байта нулевой, сохранить SignedWord'),
        0x76BB:(['Расчёт SignedWord-8 с предварительно очищенным Carry.'],None),
        0x76BE:(['Обновление SignedWord результатом вычитания по модулю 65536.'],None),
        0x76C1:(['Создание запроса перерисовки шестой шкалы после изменения слова.'],None)})
    def name_operands(region,address,operation):
        if (region,address)!=('Action',start):return operation
        for old,new in (('#6F59','@ActionProjectionClipState.SkipDetail'),('#6E72','@ActionGaugeWordKeysState.MotionOpcode'),
            ('#A78F','@ActionPanelGaugesState.SignedWord'),('#669F','@ActionPanelGaugesState.SixthRequest'),
            ('#0008','@ActionGaugeKeyConst.StepWord'),('#0088','@ActionControlDecayConst.ResetWord'),
            ('CP #3A','CP @ActionGaugeKeyConst.MotionOpcode'),('BIT 7, H','BIT @ActionAbs32Const.SignBit, H'),
            ('BIT 4, L','BIT @ActionGaugeKeyConst.NegAllowBit, L'),('LD A, #01','LD A, @ActionControlDecayConst.RequestOn')):
            operation=operation.replace(old,new)
        return operation
    def qualify_mutations(records,regions,functions,pieces):
        for item in records:
            if item['region']!='Action':continue
            if start<=item['writer']<end:
                item.update(writer_bank=5,writer_offset=item['writer']-0x6000+0x23D,writer_source_classified=True,
                    target_region='Action',target_bank=5,target_slot=17,target_offset=item['target']-0x6000+0x23D,
                    target_source_classified=True,target_path='Source/Action/UpdatePanelGauges.asm')
            if start<=item['target']<end:
                item.update(target_source_classified=True,target_path='Source/Action/'+name+'.asm',target_region='Action',target_bank=5)
    return dict(FUNCTIONS={start:(name,('Увеличение' if increase else 'Уменьшение')+' слова шестой шкалы с исходными клавиатурными ограничениями')},
        LOCAL=local,CONTRACTS=contracts,COMMENTS=comments,name_operands=name_operands,qualify_mutations=qualify_mutations,
        MODIFIED_WRITERS=((0x769F if increase else 0x76C3,0x669F,0x669E,1),),
        STATE_MODULE='ActionGaugeWordKeysState',STATE_FIELDS=(('MotionOpcode',0x6E72,'исходный опкод LD A,(nn), только 3A допускает изменение слова'),) if increase else (),
        INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionGaugeKeyConst',CONST_BLOCK),) if increase else (),
        UNCLASSIFIED_PREFIX_PATH='Source/Resources/17_ACTION/Unclassified018_BeforeGaugeKeys.bin',
        UNCLASSIFIED_SUFFIX_PATH='Source/Resources/17_ACTION/Unclassified018_AfterIncreaseGaugeWord.bin')
