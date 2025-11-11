import logging
import os
from datetime import datetime


LOG_DIR = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)


def _make_log_path():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(LOG_DIR, f"run_{timestamp}.log")


def configure_root_logger(level=logging.INFO):
    """Configure root logger to write to a timestamped file and stdout.

    This is idempotent: calling multiple times won't add duplicate handlers.
    """
    root = logging.getLogger()
    if getattr(root, '_feedbacktrader_configured', False):
        return

    root.setLevel(level)

    # file handler
    fh = logging.FileHandler(_make_log_path(), encoding='utf-8')
    fh.setLevel(level)
    fh_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    fh.setFormatter(fh_formatter)
    root.addHandler(fh)

    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch_formatter = logging.Formatter('%(levelname)s [%(name)s] %(message)s')
    ch.setFormatter(ch_formatter)
    root.addHandler(ch)

    root._feedbacktrader_configured = True


def get_logger(name: str = None):
    configure_root_logger()
    return logging.getLogger(name)
