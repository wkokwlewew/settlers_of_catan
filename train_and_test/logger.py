import logging


class ScorePrintingFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().startswith('|')

logging.basicConfig(level=logging.INFO,
                    format='%(relativeCreated)-6d | %(levelname)-2s | %(message)s')
logger = logging.getLogger()
logger.addFilter(ScorePrintingFilter())
