# RRLStoryFetcher
This package allow the user to fetch Story or Chapters of a story from Royal  Legends.

## Sample Code
This sample code fetches the content of a story "The Good Student" from Royal Road Legends and store it in a single HTML file.
```python
import contextlib

from RRLStory.RoyalRoad import Story, Chapter

log_file = open("chrome_logs.log", 'a')
s = None

with contextlib.redirect_stdout(log_file):
    s = Story("https://royalroadl.com/fiction/10286/the-good-student")

story_file = open(s.title.replace(" ", "-") + ".html", 'w')
story_file.write("<h1>" + s.title + "</h1>\n")

for chap in s.chaptersUrl:
    c = Chapter(chap[1])
    story_file.write("<div>\n")
    story_file.write("<h2>" + c.title + "</h2>\n")
    story_file.write(c.content.text.replace('\n','<br />\n'))
    story_file.write("</div>\n")
story_file.close()
```
