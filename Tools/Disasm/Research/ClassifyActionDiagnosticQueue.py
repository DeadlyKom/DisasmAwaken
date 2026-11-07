"""Публикация подтверждённого тела диагностической процедуры, соседние строки сохраняются."""
from PublishActionRawFunction import main
import ActionDiagnosticQueueFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionDiagnosticQueue', 0xACAB, 0xACD6, 1088, allow_subrange=True)
