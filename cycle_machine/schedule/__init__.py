from cycle_machine.brain.delta import DeltaSolutionConfig
from apscheduler.schedulers.background import BlockingScheduler

from cycle_machine.schedule.market_feed import get_market_feed
from cycle_machine.repository import get_repository

from datetime import datetime, timedelta

def sync_new_bars(delta_solution_config: DeltaSolutionConfig, period: int):
    feed = get_market_feed(delta_solution_config)
    repository = get_repository(delta_solution_config)
    last_bar = repository.get_last_bar(period)
    bars = feed.get_bars_for(period, last_bar.date_time, datetime.now())

    for i in range(0, len(bars)):
        if last_bar.date_time == bars[i].date_time:
            bars.pop(i)
            break

    new_bars = []

    for b in bars:
        new_bars.append(repository.save_bar(period, b))

    return new_bars

def log_and_summarize_created_bars(symbol: str, period: int, created_bars: []):
    bar_or_bars = "bar"

    if len(created_bars) > 1:
        bar_or_bars = "bars"

    log_line = "%s - %d synced %d new %s" % (symbol, period, len(created_bars), bar_or_bars)

    print(log_line)

    return log_line

if __name__ == '__main__':
    market_feeds_for_symbols = []

    scheduler = BlockingScheduler()

    symbol = "GOLD"
    delta_solution_config = DeltaSolutionConfig(symbol)

    for p in delta_solution_config.periods_asc():
        p = 1920
        # p = 60
        created_bars = sync_new_bars(delta_solution_config, p)
        log_and_summarize_created_bars(symbol, p, created_bars)

    print("z")
    # scheduler.start()

