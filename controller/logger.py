import datetime
from config import ensure_dirs, LOG_DIR


def log(message, logfile=None):
	ensure_dirs()
	if logfile is None:
		logfile = f"{LOG_DIR}/run.log"

	timestamp = datetime.datetime.now().isoformat()
	line = f"[{timestamp}] {message}\n"

	print(line, end='')
	with open(logfile, "a") as f:
		f.write(line)
