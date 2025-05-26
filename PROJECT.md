# Approach

## Challenges

1. There's not one way that websites put their logos. Some are gonna be in tags such as `<svg>`, `<img>`, even `<a>`; others may put it as CSS background;
2. Crawling and fetching strategy needs to take into consideration resources because fetching all the time is time and resource consuming;
3. External libraries should be used with caution and parsimoniously;
4. Even if I get results, I need to find a scalable way of checking the results;
5. Even though it was already mentioned, I need to avoid redundancies because they might cost a bit of time in this scale, but in larger scale will cost even more;
6. Document thoroughly for the interview. There's a lot of new stuff and I won't remember out of the top of my head;
7. Check for `robot.txt` in a first run.

## Plan

1. Fetch all index.html files into a SQLite3 database;
2. The database will contain domain, HTML BODY, logo, and favicon columns;
3. After I have that, I won't need to fetch the HTML bodies again in the next executions;
4. Since I have the HTML bodies, I can investigate possible tags with links to the logo;
5. For those that do not contain anything in logo yet, I will be left out with a group that I can investigate further why my original methodology did not work;
6. Add different methodologies to reach at least 51% extraction;
7. Check `robot.txt` for permissions.

## External libraries

So far, the only external libraries that have shown to be absolutely necessary are `sqlite3` and `aiohttp`

## Sources

- About web crawling in general: [1](https://www.cloudflare.com/learning/bots/what-is-a-web-crawler/)
- About robot.txt: [1](https://developers.google.com/search/docs/crawling-indexing/robots/intro) [2](https://moz.com/learn/seo/robotstxt)
