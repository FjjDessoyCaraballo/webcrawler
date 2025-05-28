# Log

## May 22nd to 23rd

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

Even though I tried to be careful with the time span of my tries, I think I might have gotten my IP banned from `facebook.com`. The only possible immediate solution for this would be to use official APIs, but this approach definitely won't work for us either because i) it is not scalable; ii) companies don't offer APIs for logos as much as I know.

## May 26th

Made a full run of Crawler and this was the result:

```bash
Completed fetching 1000 domains

✅ Successfully fetched: 704

❌ Failed to fetch: 296
```

At this point, it is safe to assume that some of those domains that failed were either overly protective or just plainly don't exist anymore. At least the number of remaining domains does not trigger me to enhance the crawler requests.

## May 27th

I've divided the code into two clases: `Crawler` and `Fetcher` for modularization. `Crawler` can be ran independently to renew the `final_url` domains so we do not have just the basic form of the domain (without `http`, `https`, `https://www`, or `http://www`). Therefore, the `Fetcher` can also be used independently and more times, and theoretically I would wish to not do any requests in here, assuring that we are doing all interactions with domains only in `Crawler`. This means less traffic from my side and less likelihood of being banned/blackholed.

At this stage I need to start thinking about tests, and this assignment would require fancy tools to evaluate if the images are indeed compatible with the logos since there's >700 possibilities. I do not have all the time to thoroughly test all those, neither I want to automate this task because it would probably require external libraries. The solution seems to fetch batches of results an manually check corresponding results. This unit test may not be the most efficient, but it is a baseline.

A more scalable solution for this issue would be to use Pillow (`PIL`) with `Imagehash` for image comparison.

## May 28th

I've made the conscious decision to not handle edge cases where the logo might've been linked to any tags but `<img>` and `<svg>`. The regex for those cases would've been overly complicated and was unfruitful in more than 90% of the `Fetcher` runs. For future reference, and to save my sanity, I should use the HTML parser instead of regexes.

Tomorrow I should work on some tests and data visualizations for the interview.