import logging
UTTERANCE_LOG_LEVEL = 15
logging.addLevelName(UTTERANCE_LOG_LEVEL, "UTTERANCE_LOG_LEVEL")

class UtteranceFilter(logging.Filter):
    def filter(self, record):
        if record.levelno == UTTERANCE_LOG_LEVEL:
           return True
