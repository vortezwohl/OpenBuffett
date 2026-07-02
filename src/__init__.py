import logging
from dotenv import load_dotenv

NEW_LINE = '\n'
BLANK = ' '

load_dotenv()
logger = logging.getLogger('resume-maker')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(name)s : %(message)s')

if not any(
    getattr(handler, "name", "") == "resume-maker-console"
    for handler in logger.handlers
):
    console_handler = logging.StreamHandler()
    console_handler.set_name("resume-maker-console")
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logging.getLogger('resume-maker.llm').setLevel(logging.DEBUG)
