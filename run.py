from app import subscriber, cloud_config

if __name__ == '__main__':
    print('Starting SDX seft')
    cloud_config()
    subscriber.start()
