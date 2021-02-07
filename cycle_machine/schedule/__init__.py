from cycle_machine.brain.delta import DeltaSolutionConfig
from apscheduler.schedulers.background import BlockingScheduler

from cycle_machine.schedule.market_feed import get_market_feed
from cycle_machine.repository import get_repository

from datetime import datetime, timedelta

symbols = ['GOLD']


def time_gap(symbol, period):
    pass


def round_down_time(time: datetime, period: int):
    if period % 1440 == 0:
        datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)

        days = period / 1440

        if(days > 1):
            pass


    if period % 60 == 0:
        datetime.now().replace(microsecond=0, second=0, minute=0)

    pass


def sync_new_bars(delta_solution_config: DeltaSolutionConfig, period: int):
    feed = get_market_feed(delta_solution_config)
    repository = get_repository(delta_solution_config)
    last_bar = repository.get_last_bar(period)
    bars = feed.get_bars_for(period, last_bar.date_time, datetime.now())

    if len(bars) > 0:
        bars.pop(0)

    return None

    new_bars = []
    for b in bars:
        new_bars.append(repository.save_bar(period, b))

    return new_bars

# def log_and_summarize_created_bars(symbol: str, period: int, created_bars: [Bar]):
#    pass

if __name__ == '__main__':
    market_feeds_for_symbols = []

    scheduler = BlockingScheduler()

    """
    for s in symbols:
        delta_solution_configuration = DeltaSolutionConfig(s)
        feed = get_market_feed(delta_solution_configuration)

        for p in delta_solution_configuration.periods_asc():
            
            pass

        p = 5

        job_id = s + "_" + str(p)
        scheduler.add_job(lambda: print("Lambda WTF"), seconds=3, id=job_id)

        break

        # Do we thread this here?
    """

    #
    delta_solution_config = DeltaSolutionConfig("GOLD")

    for p in delta_solution_config.periods_asc():
        p = 120
        created_bars = sync_new_bars(delta_solution_config, p)
        break

    print("z")
    # scheduler.start()

