# CS 4675 Group 10 Project



### To Run

Run "python multiple_spiders.py" inside of postscrape/spiders directory

Python code for scraper in postscrape\postscrape\spiders\post_spyder.py. Distrubution managed by multiple_spiders.py



### Design

Currently running DFS for each scraper

Once we reach a certain level of depth from base URL (cc.gatech.edu ->c.gatech.edu/abc -> ...), we force the text after (c.gatech.edu/TEXT) to be in the prefix list provided to the class, otherwise URL is not considered

```python
    custom_settings = {
        "DEPTH_LIMIT": 10
    }
```

This code manages the global settings var for how deep we can go- so if we set filter_depth to 10 and this var to 20, we could go 10 pages deeper all matching cc.gatech.edu/a if the prefix list was simply ['a']



```python
process.crawl(SuperSpider, allowed_suffix = ["d", "e", "f"], name="second")
```

SuperSpider - class name of each individual spider

allowed_suffix - suffix we want to match (set up for 1 char at the moment)

name- name of scraper for output





## File structure

postscrape/postscrape/spiders/multiple_spiders.py is the manager for the distribution of suffixes and different subprocesses. This is where multiple processes are spawned. This is alaso where the database/ tables are initialized. 

postscrape/postscrape/spiders/post_spyder.py is an individual subprocess, or where each spider runs on its own. This is where links are actually processed.



## Data storage

SQLite takes output from Scrapy and stats we modified. These stats can be found inside of the postscrape/postscrape/spiders/db file. CSV files are dated/ no longer how we manage our data output.





### Resources

https://www.youtube.com/watch?v=ALizgnSFTwQ

https://docs.scrapy.org/en/latest/topics/spiders.html