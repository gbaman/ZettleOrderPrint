### Zettle Order Print config file ###
from datetime import datetime

zettle_api_key = ""

zettle_client_id = ""

# How frequent to poll Zettle. Be careful you don't hit the rate limit! In seconds.
delay_between_zettle_queries = 3

initial_start_date = datetime(2023, 1, 1)