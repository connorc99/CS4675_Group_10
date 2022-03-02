# CS 4675 Project 1

### Executable and code bade

Executable: located in ./postscrape/output/scrapy/scrapy.exe

Run from ./postscrape scrapy crawl extractor

Python code for scraper in postscrape\postscrape\spiders\post_spyder.py

Keyword list is in postscrape\current_stats_keyword_current_output as a csv mapping keyword to list of keywords

![image-20220203135418824](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203135418824.png)



### Design

The algorithms runs BFS by enqueing new links extracted from web pages. I started with a seed URL of 'https://www.cc.gatech.edu'. Initially, I limited the scraper to only enque pages to visit in the domain of 'cc.gatech.edu'; however, after long enough, we were scraping archieved info from early 2000s class websites- I discovered a whole subset of sites with a prefix (ABC.cc.gatech.edu, XYZ.cc.gatech.edu). After ~40,000 results (in postscrape/ oldstats), I realized very few pages were being scraped with pertient info, and shifted my strategy.

I then forced the domain of the website to be 'www.cc.gatech.edu', which helped somewhat in limiting my results. 

Checks for keywords from dictionary, if found keywords are added to a CSV updated every 100 pages crawled containing mappings of keyword to list of website containing said words

The pros of running BFS is that we will reached a wide subset of pages, and explored many avenues we would not have reached initially. "Important pages" were reached quickly as we explored the links on our first page first, then on each subsequent page without running down a rabbit hole on the first link we fond.

For cons, since I did not have a max recursion like I would in DFS, all links from each page were added to the queue. This ended up being time consuming and resulted in a lot of pages being visited. As there was also no filtering past the  'www.cc.gatech.edu', many of these pages were of little interest- for example, index.php/calender links did not need to be scraped, but were.

### Screenshots of crawler

![image-20220203121158943](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203121158943.png)

*Crawler command line running*

![image-20220203121247741](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203121247741.png)

*Intermediate CSV outputs w/ stats* 

![image-20220203121327059](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203121327059.png)

*Keyword extraction stats at the same point*

## Stats

![image-20220203132651947](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203132651947.png)





![image-20220203132720019](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203132720019.png)



![image-20220203132807063](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203132807063.png)



![image-20220203133120744](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203133120744.png)

![image-20220203133808342](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203133808342.png)

![image-20220203134359029](C:\Users\connor\AppData\Roaming\Typora\typora-user-images\image-20220203134359029.png)

My computer did struggle to run consistently, but I was able to monitor its status for a while. These are the key findings I discovered. As time went on, more and more sites were either already visited or were outside of the supplied domain.Computing was the most common word found, and undergrad was less common. A log pattern is seen, with initial sites containing these words very frequently and less so later on.

My crawler showed struggles with filtering through already visited links, which I think is due to running BFS and not having a max recursion property like I would on a DFS algorithm. As a result, pages linking back to popular pages were processed over and over. My ratio of enqueued vs dequed over time gets closer and closer to 1, although this is expectede as the dequed pages builds up. More interesting is the last graph in grey, showing how many pages are remaining. It seems to steady out arounf 600, it did gradualy go down in future data (I resumed running at a different time point, which would have broken the axis)

Overall, it would have taken a long time to complete given how quickly the filtered out websites were growing, while we were still enqueing websites that do need to be visited at a steady rate. I would predict a log scale of time for how long this would take, with perhaps 10x as long to scrape 2x the amount of current website it has scraped. Reaching a million/ billion seems infeasable given the lack of contraint of depth of the search.



### Lessons Learned

I learned how hard scraping is, and how brute force isn't feasable. I also learned the importance of supplying good filters on sites to visit, as my first try allowed any domain preceding cc.gatech.edu to be scraped. I saw how much computing power is required to scrape, and how getting an inital set of sites isn't too hard, but scraping everything is extremely challenging due to repeated links/ external links. This project showed me just how important a smart algorithm is in scraping.



### Resources

https://www.youtube.com/watch?v=ALizgnSFTwQ

https://docs.scrapy.org/en/latest/topics/spiders.html