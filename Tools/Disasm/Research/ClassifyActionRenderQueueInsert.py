"""Публикация доказанного производителя runtime-очереди, сборка не запускается."""
from ClassifyActionRegionType import main
import ActionRenderQueueInsertFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionRenderQueueInsert', 'ActionRenderQueueInsert', (
        ('Head', 0x9BA1, 'младший байт головы страницы 8F, 01 конец цепочки'),
        ('FreeOffset', 0x9BA2, 'свободное смещение с шагом 14, FC буфер исчерпан'),
        ('HeaderWord0', 0x9B8D, 'первое исходное слово снимка, полный игровой смысл неизвестен'),
        ('PhasePair', 0x9B12, 'слово первых двух байтовых фаз Phase0 и Phase1'),
        ('Phase2', 0x9B14, 'третья байтовая фаза Phase2')),
        include_blocks=facts.INCLUDE_BLOCKS)
