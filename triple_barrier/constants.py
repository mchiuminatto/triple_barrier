import pathlib
from datetime import datetime

ROOT_FOLDER = str(pathlib.Path(__file__).parent.resolve().parent.resolve())

OPEN = "open"
HIGH = "high"
LOW = "low"
CLOSE = "close"
ENTRY = "entry"
EXIT = "exit"

INFINITE_DATE = datetime(datetime.now().year + 1000, month=1, day=1)

# region barrier
STOP_LOSS: str = "stop-loss"
TAKE_PROFIT: str = "take-profit"
DYNAMIC_CLOSE: str = "dynamic-close"
TIME_LIMIT: str = "time-limit"
OPEN_PRICE: str = "open-price"
# endregion
