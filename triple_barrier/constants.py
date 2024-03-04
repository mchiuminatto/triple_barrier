import pathlib
from datetime import datetime

ROOT_FOLDER = str(pathlib.Path(__file__).parent.resolve().parent.resolve())

OPEN = "open"
HIGH = "high"
LOW = "low"
CLOSE = "close"

INFINITE_DATE = datetime(datetime.now().year + 1000, month=1, day=1)
