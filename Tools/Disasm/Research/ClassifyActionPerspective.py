"""Выделение доказанной перспективы из большого бинарного диапазона с сохранением обоих соседей."""
from PublishActionRawFunction import main
import ActionPerspectiveFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionPerspective', 0xD7A0, 0xDBBD, 284672, allow_subrange=True)
