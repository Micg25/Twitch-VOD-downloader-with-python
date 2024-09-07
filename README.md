# Twitch-VOD-downloader-with-python
Twitch VOD downloader made in python with the following libraries: aiohttp, asyncio, re, ffmpeg and bs4.
In order to make it work install all the dependencies, download the code and put values on the variables where is needed (I checked it with comments).
The code will download the VOD you want at a very high speed thanks to the implementation of asyncio requests. I chose to use aiohttp because requests didn't support asyncronous requests.
Basically the code will get the VOD Id, then get the m3u8 file which is the file that contains all the chunks. Once it gets the m3u8 file it starts downloading every ".ts" chunks. Then is gonna put all the chunks together in a ".ts" video file
and finally with "ffmpeg" converts it into a ".mp4" file.
The download is always at the best quality.
