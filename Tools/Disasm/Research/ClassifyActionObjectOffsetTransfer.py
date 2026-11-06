"""Публикация F0F8..F137 в исходной верхней области ACTION."""
from PublishActionRawFunction import main
import ActionObjectOffsetTransferFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionObjectOffsetTransfer', 0xF0F8, 0xF138, 196608, allow_subrange=True)
