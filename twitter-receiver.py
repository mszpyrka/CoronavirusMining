from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
import credentials
import json
from time import sleep
from datetime import datetime


class FileStorageListener(StreamListener):

    def __init__(self, hashtags, storage_filename, storage_dir, chunk_size=1_000):
        super().__init__()
        self.hashtags = hashtags
        self.chunks_counter = 0
        self.chunk_size = chunk_size

        self.storage_filename = storage_filename
        self.storage_dir = storage_dir

        self.buffer = []
        self.backoff_time = 0

    def on_data(self, raw_data):
        """
        Appends new record to the buffer, saves whole buffer content into file if buffer size limit is exceeded.
        Additionally clears error backoff time.
        """
        self.buffer.append(raw_data)
        self.backoff_time = 0

        if len(self.buffer) >= self.chunk_size:
            self.save_chunk()
            self.chunks_counter += 1
            self.buffer = []

        return True

    def save_chunk(self, verbose=True):
        """
        Dumps buffer content into file. The name of the file is created by concatenating
        storage_filename parameter with chunk number.
        """
        new_file_path = f'{self.storage_dir}/{self.storage_filename}-{str(self.chunks_counter).zfill(4)}.json'
        data = {
            'hashtags': self.hashtags,
            'records': self.buffer
        }

        if verbose:
            print(f'{datetime.now()} ===> saving chunk {self.chunks_counter}')

        with open(new_file_path, 'w') as f:
            json.dump(data, f)

    def on_error(self, status_code):
        print(datetime.now())
        print(status_code)
        # self.backoff()
        return True

    def backoff(self):
        print(f'{datetime.now()} ====> starting backoff sleep for {self.backoff_time} seconds')
        sleep(self.backoff_time)
        self.backoff_time = max(1, self.backoff_time * 2)


if __name__ == "__main__":
    hashtags = ['coronavirus', 'covid19']
    listener = FileStorageListener(
        hashtags=hashtags,
        storage_filename='COVIDtweets',
        storage_dir='./twitter-data/',
        chunk_size=10_000
    )

    auth = OAuthHandler(credentials.API_KEY, credentials.API_KEY_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)

    stream = Stream(auth, listener)
    stream.filter(track=hashtags)
