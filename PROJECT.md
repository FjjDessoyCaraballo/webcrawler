# Approach

## Challenges

1. There's not one way that websites put their logos. Some are gonna be in tags such as `<svg>` and `<img>`; others may put it as CSS background;
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
7. Check `robot.txt` for permissions;
8. Use two classes (Crawler and Fetcher) for the whole process, ensuring modularity and later use;

## Why two classes for one task?

To make the code clearer and separate tasks more accordingly, I believe it was a better practice to separate one task into two. The `Crawler` bot can be responsible for checking updates, and if there is no update, there shouldn't be any extraction of the logo. This approach assures us that we are only going to make requests that are neccessary.

## External libraries

I am trying to work with built-in libraries as much as possible. So far, the only external libraries that have shown to be absolutely necessary are `sqlite3` and `aiohttp`.

Built-in libraries used:

- csv
- random
- os
- sys
- ssl
- asyncio
- urllib
- re
- base64
- typing

## Sources

- About web crawling in general: [[1]](https://www.cloudflare.com/learning/bots/what-is-a-web-crawler/)
- About robot.txt: [[1]](https://developers.google.com/search/docs/crawling-indexing/robots/intro) [[2]](https://moz.com/learn/seo/robotstxt)
- About SVGs: [[1]](https://www.adobe.com/creativecloud/file-types/image/vector/svg-file.html) [[2]](https://developer.mozilla.org/en-US/docs/Web/SVG)
- Base64 encoding: [[1]](https://www.lifewire.com/base64-encoding-overview-1166412)
- aiohttp documentation: [[1]](https://docs.aiohttp.org/en/stable/)
- SQLite3 documentation: [[1]](https://www.sqlite.org/docs.html)
- Regular expression documentation: [[1]](https://docs.python.org/3/library/re.html)

### Fetch Status Codes

*200*: Successful fetch
*403*: Access forbidden (bot blocking)
*404*: Page not found
*-1*: DNS resolution failed (domain doesn't exist)
*0*: Network error or timeout

### Extraction Methods (will definitely change with time)

*IMG_TAG*: Found logo via `<img>` tag with "logo"
*SVG_TAG*: Found logo via `<SVG>` tag with "logo"
*FAVICON*: Used favicon as fallback logo

### Confidence Scores

*0.91-1.0*: Very high confidence
*0.71-0.9*: High confidence
*0.51-0.7*: Medium confidence
*0.21-0.5*: Low confidence
*0.0-0.2*: Very low confidence

### SQL Injections

While SQL injections are not feasible in `Crawler`, fetcher could retrieve SQL injections disguised  inside HTML bodies. one could easily leave comments inside the HTML body. Even though this is a farfetched possibility, it is still a possibility.
