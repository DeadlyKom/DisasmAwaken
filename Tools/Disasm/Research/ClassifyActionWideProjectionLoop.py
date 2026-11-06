"""Публикация проверенного обхода широких векторов."""
import ActionWideProjectionLoopFacts as facts
from ClassifyActionRegionType import main


if __name__ == '__main__':
    main(facts, 'ActionWideProjectionLoop', 'ActionWideProjectionInput', (
        ('Published0', 0x9B87, 'старший байт первого результата выбранной записи'),
        ('Published1', 0x9B88, 'старший байт второго результата выбранной записи'),
        ('Published2', 0x9B89, 'старший байт третьего результата выбранной записи'),
        ('SelectedIndex', 0x9BCA, 'индекс для публикации при совпадении пар контекста'),
    ))
