"""Публикация исходного байта 29 по E59F через отдельный кандидат."""

from PublishActionRawFunction import main
import ActionRecordScaleExtraEntryFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionRecordScaleExtraEntry', 0xE59F, 0xE5A0, 65538)
