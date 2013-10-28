webtoon_crawler
===============

webtoon_crawler is an automatic crawler of webtoons from Naver, Daum, and Nate. You can download all image files from their webtoons, including the ones in Daum's league and Naver's challenge/best-challenge sections.

To use this software, add the title ids of webtoons as instructed in webtoon_crawler.py, and run the file with command "python webtoon_crawler.py". No additional installation is required.

If you want a particular crawl type (full, shallow, update), please specify it as a command line argument flag "-t". For example, a shallow crawl (default) can be specified as "python webtoon_crawler.py -t shallow". For more information, please execute webtoon crawler with help flag, "python webtoon_crawler.py -h"

webtoon_crawler was tested on Windows 7 with Python 3.3. It is not compatible with Python 2.x

This project has started for programming practice purposes, and will remain so. It should not be used against intellectual property law.