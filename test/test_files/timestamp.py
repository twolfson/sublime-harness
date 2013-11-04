import time

def run():
    with open('%s', 'w') as f:
        f.write(str(time.time()))
