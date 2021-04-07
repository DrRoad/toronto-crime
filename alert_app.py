from src.data.tweet_scrapper import TweetScrapper
from src.utils.build_user_df import BuildUserDf
from src.utils.email_users import EmailUsers
import coloredlogs
import logging
import os
logger = logging.getLogger(__name__)
import time
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)

def get_user_df_and_send_emails(tweet_df):
    builder = BuildUserDf()
    builder.get_and_set_customer_df()
    for ix, row in tweet_df.iterrows():
        # if row.lat != "null":
        #     import ipdb; ipdb.set_trace()
        user_df = builder.build_user_df()
        if user_df.shape[0] > 0:
            email_users = EmailUsers(user_df)
            sel_users = email_users.filter_to_users_near_the_event(row.lat, row.lon)
            email_users.email_the_right_users(
                sel_users,
                row
            )

def append_to_streaming_raw_tweet_tables_every_n_secs(secs=10, log_every=1000):
    logger.info('Starting to listen')
    logger.info(f'Making requests every {secs}s, logging every {log_every}s')
    scrapper = TweetScrapper()
    i = 0
    while True != False:
        if i % log_every == 0:
            logger.info(f'Making request number: {i+1}')
        res_df = scrapper.get_tweets_from_last_n_secs("TPSOperations", secs, ops_tweet=True)
        if res_df.shape[0] > 0:
            get_user_df_and_send_emails(res_df)
        scrapper.save_tweetdf_to_db(res_df, "streaming_raw_tps_ops_tweets", if_exists="append")
        res_df = scrapper.get_tweets_from_last_n_secs("TorontoPolice", secs)
        scrapper.save_tweetdf_to_db(res_df, "streaming_raw_to_police_tweets", if_exists="append")
        i += 1
        time.sleep(secs)


if __name__ == "__main__":
    append_to_streaming_raw_tweet_tables_every_n_secs(secs=10, log_every=10000)