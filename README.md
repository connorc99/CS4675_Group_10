# CS 4675 Group 10 Project



### To Run

Run "python multiple_spiders.py" inside of postscrape/spiders directory

Python code for scraper in postscrape\postscrape\spiders\post_spyder.py. Distrubution managed by multiple_spiders.py

Keyword list is in postscrape\current_stats_keyword_current_output as a csv mapping keyword to list of keywords



### Design

Currently running BFS for each scraper

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



## CSV Files

These files are needed for the final analysis- for project 1, I took these into a Jupyter notebook and analyzed accordingly. We will want to alter these functions. I think it may be a good idea to add class variables inside of SuperSpider tracking each spiders current progress



## To Do

- Persistence of URLs for duplicate checking across spiders

  https://stackoverflow.com/questions/51225781/how-to-prevent-duplicates-on-scrapy-fetching-depending-on-an-existing-json-list

  - Brute force solution: add all URLs we have scraped to DB or JSON file, check for occurance of current URL in that database
  - Could be a little wonky w/ 2 scrapers at once w/ read write issues, but should be sufficient for this project

- Analysis of unique URLs scraped by each scraper, levels of recursion reached
- Analysis of optimal DEPTH_LIMIT, max_depth, number of subprocesses and different distribution of suffix list for base URL
- Unlikely we will end up doing recommendation system, enough work to do here for project





### Resources

https://www.youtube.com/watch?v=ALizgnSFTwQ

https://docs.scrapy.org/en/latest/topics/spiders.html