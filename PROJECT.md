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

## Notes

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
