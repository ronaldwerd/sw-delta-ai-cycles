from datetime import datetime


class Bar:
    def __init__(self, date_time, high_price, low_price, open_price, close_price):
        if type(date_time) is str:
            if date_time.isdigit():
                self.date_time = datetime.fromtimestamp(int(date_time))

        if type(date_time) is int:
            self.date_time = datetime.fromtimestamp(date_time)

        if type(date_time) is datetime:
            self.date_time = date_time

        self.high = float(high_price)
        self.low = float(low_price)
        self.open = float(open_price)
        self.close = float(close_price)
