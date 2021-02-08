import argparse

import os
import re

from cycle_machine.brain.delta import DeltaSolutionConfig
from cycle_machine.repository import MongoDbRepository
from cycle_machine.tools.mt4reader import History, get_bars_from_csv

parser = argparse.ArgumentParser(description='This tool imports MetaTrader history .hst files '
                                             'into the cycle machine repository')

parser.add_argument('--dir', dest='import_dir', required=True, help="Directory with .hst files")
parser.add_argument('--symbol', dest='import_symbol', required=True, help="Example: EURUSD, USDCAD, USCASH500, GOLD")

args = parser.parse_args()


def import_hst_file(hst_file, symbol, period):
    with open(hst_file, 'rb') as f:
        print("Inserting data for %s at period %d..." % (symbol, period), end=" ")

        history = History(f)
        delta_solution_config = DeltaSolutionConfig(symbol)
        repository = MongoDbRepository(delta_solution_config)
        # repository.
        bars_inserted = repository.save_mt4_history(history, period)

        print("%d bars inserted. [OK]" % bars_inserted)


def import_mt4_csv_file(csv_file, symbol, period):
    delta_solution_config = DeltaSolutionConfig(symbol)
    repository = MongoDbRepository(delta_solution_config)

    bars = get_bars_from_csv(csv_file)
    bars_inserted = repository.save_mt4_history_bars(bars, period)
    print("%d bars inserted. [OK]" % bars_inserted)


def available_hst_files_for_symbol(symbol: str, directory: str):
    files_to_import = [f for f in os.listdir(directory) if f.startswith(symbol) and f.endswith('.hst')]

    for f in files_to_import:
        numbers = [int(n) for n in re.findall('\d+', f)]

        if len(numbers) == 1:
            try:
                import_hst_file(os.path.join(directory, f), symbol, numbers[0])
            except Exception as e:
                print("Unable to process %s trying csv." % f, end=" ")
                import_mt4_csv_file(os.path.join(directory, os.path.splitext(f)[0] + ".csv"), symbol, numbers[0])


if os.path.exists(args.import_dir):
    available_hst_files_for_symbol(args.import_symbol, args.import_dir)
else:
    print("Directory: %s does not exist." % args.import_dir)

