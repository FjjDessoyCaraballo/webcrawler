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
7. Check `robot.txt` for permissions;
8. Use two classes (Crawler and Fetcher) for the whole process, ensuring modularity and later use;

## Why two classes for one task?

To make the code clearer and separate tasks more accordingly, I believe it was a better practice to separate one task into two. The `Crawler` bot can be responsible for checking updates, and if there is no update, there shouldn't be any extraction of the logo. This approach assures us that we are only going to make requests that are neccessary.

## External libraries

I am trying to work with built-in libraries as much as possible. So far, the only external libraries that have shown to be absolutely necessary are `sqlite3` and `aiohttp`.

## Sources

- About web crawling in general: [[1]](https://www.cloudflare.com/learning/bots/what-is-a-web-crawler/)
- About robot.txt: [[1]](https://developers.google.com/search/docs/crawling-indexing/robots/intro) [[2]](https://moz.com/learn/seo/robotstxt)
- About SVGs: [[1]](https://www.adobe.com/creativecloud/file-types/image/vector/svg-file.html) [[2]](https://developer.mozilla.org/en-US/docs/Web/SVG)
- Base64 encoding: [[1]](https://www.lifewire.com/base64-encoding-overview-1166412)
- aiohttp documentation: [[1]](https://docs.aiohttp.org/en/stable/)
- SQLite3 documentation: [[1]](https://www.sqlite.org/docs.html)

## Current schema of the database

**Table**: `domains`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier for each domain record |
| `domain` | TEXT | UNIQUE | The base domain name (e.g., "facebook.com") |
| `robots_txt` | INTEGER | CHECK (0,1) | Whether robots.txt allows crawling: `0` = disallowed, `1` = allowed |
| `html_body` | TEXT | | The complete HTML content of the website's index page |
| `final_url` | TEXT | | The final URL after following redirects (e.g., "https://www.facebook.com") |
| `logo_url` | TEXT | | The extracted logo image URL (if found) |
| `favicon_url` | TEXT | | The extracted favicon URL (if found) |
| `fetch_timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP | When the domain was last crawled |
| `fetch_status` | INTEGER | | HTTP status code received (200, 403, 404, etc.) or custom error codes |
| `error_type` | TEXT | | Type of error encountered during crawling |
| `extraction_method` | TEXT | | The method used to extract the logo (for debugging/optimization) |
| `confidence_score` | REAL | | Confidence level (0.0-1.0) in the extracted logo accuracy |

### Fetch Status Codes

*200*: Successful fetch
*403*: Access forbidden (bot blocking)
*404*: Page not found
*-1*: DNS resolution failed (domain doesn't exist)
*0*: Network error or timeout

### Extraction Methods (will definitely change with time)

*IMG_TAG_ALT*: Found logo via `<img>` tag with "logo" in alt text
*IMG_TAG_CLASS*: Found logo via `<img>` tag with "logo" in class name
*SVG_TAG*: Found logo via `<SVG>` tag with "logo"
*CUSTOM_TAG*: Found logo via, for example, `<a>` tag with "logo"
*CSS_BACKGROUND*: Found logo as CSS background image
*SVG_ELEMENT*: Found logo as inline SVG element
*FAVICON_LINK*: Used favicon as fallback logo
*MANUAL_HEURISTIC*: Custom logic-based extraction

### Confidence Scores

*1.0*: High confidence (clear logo indicators)
*0.7-0.9*: Medium confidence (probable logo)
*0.5-0.6*: Low confidence (uncertain match)
*0.0-0.4*: Very low confidence (likely false positive)
*NULL*: No extraction attempted or failed

## Log

### May 22nd to 26th

Came to a compromise that for the sole reasons of this project I will collect the `index.html` of websites that contain `robots.txt`. It does not follow etiquette, but this is not for a commercial reason and I was not told to *not* do it. I am signaling inside the database which domains contained `robots.txt` and I output to the `STDOUT` in terminal that the request went through regardless with a ☑️, while successful requests that did not circumvent the robots textfile are signaled with a ✅.

Fixed the connectivity issues by adding a more 'credible' information in the header, such as language and encoding preferences. The reason for this is to look more 'human-like' when making requests.

```Python
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate',
			'Connection': 'keep-alive',
			'Upgrade-Insecure-Requests': '1',
```

The `Accept-Encoding` key is the encoding preference mentioned before, and `Accept-Language` is the other example also mentioned.

I'm using random samples of the CSV to test the crawler as I enhance it. This way I won't get rate limited nor banned from certain websites:

```bash
☑️ mynewsletterbuilder.com -> https://mynewsletterbuilder.com: Success
☑️ serverintellect.com -> https://serverintellect.com: Success
❌ xfinity.com: Failed (Status : Network Error)
☑️ formstack.com -> https://formstack.com: Success
☑️ no-ip.com -> https://no-ip.com: Success
☑️ kajeet.com -> https://kajeet.com: Success
☑️ mobileread.com -> https://mobileread.com: Success
⚠️ Error - Cannot connect to host epaperflip.com:443 ssl:default [No address associated with hostname]
⚠️ Error - Cannot connect to host epaperflip.com:80 ssl:default [No address associated with hostname]
❌ epaperflip.com: Failed (Status : Network Error)
☑️ vzw.com -> https://vzw.com: Success
❌ yahoo.co.jp: Failed (Status : Network Error)

Completed fetching 10 domains

✅ Successfully fetched: 7

❌ Failed to fetch: 3
```

Some of the prints may not get through to the final version. The `epaperflip` domain is an example of outdated domains that just don't exist anymore. Additionally, the `yahoo.co.jp` is another good example of an outdated domain, but this one "exists". The problem here is that there is probably a regional ban. I am not taking care of this edge case.

Even though I tried to be careful with the time span of my tries, I think I might have gotten my IP banned from `facebook.com`. The only possible immediate solution for this would be to use official APIs, but this approach definitely won't work for us either because i) it is not escalable; ii) companies don't offer APIs for logos as much as I know.

### May 27th

Made a full run of Crawler and this was the result:

```bash
Completed fetching 1000 domains

✅ Successfully fetched: 704

❌ Failed to fetch: 296
```

At this point, it is safe to assume that some of those domains that failed were either overly protective or just plainly don't exist anymore. At least the number of remaining domains does not trigger me to enhance the crawler requests.
