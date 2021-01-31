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




    delta_solution_config = DeltaSolutionConfig("GOLD")
    feed = get_market_feed(delta_solution_config)
    # bars = feed.get_bars_for(1440)

    repository = get_repository(delta_solution_config)
    # repository.load_series(1440)
    last_bar = repository.get_last_bar(1440)
    feed.get_bars_for(1440, last_bar.date_time, datetime.now())

    print("z")
    # scheduler.start()

