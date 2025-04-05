from time import time_ns


class Time:
    counter = 1

    def __init__(self, comment=''):
        self.name = f'Timer {Time.counter}'
        if comment:
            self.name += f': {comment}'
        Time.counter += 1

    def __enter__(self):
        self.t0 = time_ns()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.time = time_ns() - self.t0
        print(
            f'\n'
            f'{self.name}\n'
            f'{self.time / 10 ** 9:.3f} seconds passed\n'
        )
