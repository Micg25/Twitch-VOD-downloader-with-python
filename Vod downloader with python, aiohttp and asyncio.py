import aiohttp
import asyncio
import re
import ffmpeg
import os
from bs4 import BeautifulSoup

url = "https://dgeft87wbj63p.cloudfront.net/" #base url to the server you are gonna download the VOD from
link = ""  #put the url of the vod you want to download
path_ts="" # put here the path and the name of the ".ts" initial video (in the complete path include ".ts" at the end)
path_mp4=""  # put here the path and the name of the file  ".mp4" final video  (in the complete path include ".mp4" at the end)

headers={

    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/115.0",
    "Referer":link,
}

# async function to download a single chunk
async def download_chunk(session, vod_id, chunk):
    url_ = f"{url}{vod_id}/chunked/{chunk}.ts" # forging the url
    while True:
        try:
            async with session.get(url_, timeout=30,headers=headers) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    print(f"Downloaded chunk {chunk} (size: {len(content)} bytes)")
                    break # the code is gonna break the "While" cycle only if it gets the current chunk
                else:
                    print(f"Failed to download chunk {chunk}, status: {resp.status}")
        except Exception as e:
            print(f"Error downloading chunk {chunk}: {e}")  # if it fails fetching is gonna try again until it fetched
            await asyncio.sleep(5)  # Waits 5 second if the previous request was bad, and then retries 
    return (chunk,content)


async def main():
    async with aiohttp.ClientSession() as session:
        # Obtaining m3u8 url
        while True:
            try: 
                async with session.get(link,headers=headers) as resp:
                    text = await resp.text()
                    soup = BeautifulSoup(text, "html.parser")
                    div = soup.find('meta', {"name": 'twitter:image'}).get('content') # getting the VOD id which is needed to forge the m3u8 url 
                    pattern = r"https://static-cdn\.jtvnw\.net/cf_vods/[^/]+/([^/]+)/" 
                    vod_id = re.search(pattern, div).group(1)
                    m3u8_url = f"https://dgeft87wbj63p.cloudfront.net/{vod_id}/chunked/index-dvr.m3u8" # forgin mru8 url
                    break
            except: continue

        # Obtaining m3u8 file that contains the ".ts" chunks which will be downloaderd    
        async with session.get(m3u8_url,headers=headers) as resp:
            m3u8_file = await resp.text()
            chunks = re.findall(r"(\d+)\.ts", m3u8_file)

        print("TOTAL NUMBER OF CHUNKS TO BE DOWNLOADED: ", chunks[-1])
        
        # Creating the tasks that'll download the chunks
        tasks = [download_chunk(session, vod_id, chunk) for chunk in chunks]
        
        # Wait for the tasks to finish
        results = await asyncio.gather(*tasks)
        # Sorting the chunks
        merged_results=sorted(results,key=lambda x: int(x[0]))
        
        # Saving vod, merging it in a ".ts" file
        with open(path_ts, "wb") as merged_file:
            print("SAVING VOD IN A FILE....")
            for chunk,content in merged_results:
                merged_file.write(content)

        # Converting the previous .ts file to .mp4
        print("CONVERTING TO MP4...")
        ffmpeg.input(path_ts).output(path_mp4, codec='copy').run()
        print("CONVERSION COMPLETE")

        os.remove("D:\\Desktop\\downloaded Live\\stream_merged.ts")

asyncio.run(main())
