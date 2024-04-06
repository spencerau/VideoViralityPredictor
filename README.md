
The goal is to predict the virality of a tiktok video based on solely the video itself. We will use the video and audio data to predict the virality of the video. We will use the count columns as the target variable.

So the output of the video understanding model will be just a virality score.

We need to create some virality score from the count columns in the csv


We may need to extract the duration of the videos to use as a feature or to grab all videos under 15 seconds to make it easier to train.

If you want to scrape more data, you have to use your own ms token, which you get from the cookies in the browser on the tiktok website but make sure you aren't logged in to tiktok so you don't get your account banned for scraping.

Used this for scraping tiktok: https://github.com/davidteather/TikTok-Api/tree/main


Can probably use this for models and training: https://github.com/facebookresearch/pytorchvideo/tree/main

Main Requirements:
pip install TikTokApi
python -m playwright install
pip install yt-dlp




Things to note for future improvement of dataset/ future works to include in presentation:
- tiktok watermark is included in video
- should scrape unpopular videos to have a wide array and make it generalizable
- keep note of timespan from when video was downloaded to when it was uploaded since tiktoks that have been up longer will have more like counts and view counts inherently
    - maybe filter to only use videos that have been uploaded for 30 days
- could use location uploaded as input also?
- could use hashtags in future or include description
- could maybe make it predict the caption as another project
- Might be more useful information in the video_dict that I couldn't find
