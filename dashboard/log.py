import logging

logger = logging.getLogger('dunya')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

