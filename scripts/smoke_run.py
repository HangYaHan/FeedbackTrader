from src.system.log import get_logger
from src.data import fetcher
from src.data.adapters import csv_adapter, yfinance_adapter

logger = get_logger('smoke_run')

def main():
    logger.info('Starting smoke run to verify adapters')
    logger.info('csv_adapter has fetch: %s', hasattr(csv_adapter, 'fetch'))
    logger.info('yfinance_adapter has fetch: %s', hasattr(yfinance_adapter, 'fetch'))
    # call fetcher.select_adapter to ensure import path works
    logger.info('select_adapter(csv) -> %s', fetcher.select_adapter('csv'))
    logger.info('select_adapter(yfinance) -> %s', fetcher.select_adapter('yfinance'))

if __name__ == '__main__':
    main()
