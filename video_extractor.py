#!/usr/bin/env python
# Copyright (c) 2016, alunyov
# All rights reserved.

'''
Contains class VideoExtractor for extracting png from mp4, mkv, webm videos.
'''

import youtube_dl
import sys, os
import subprocess
import argparse

# Define work folder.
VIDEO_PNG_DIR = 'files'

class VideoPNGExtractor:
    #extension_list = ['mkv', 'mp4', 'webm']

    # video title
    title = ''

    # video url
    download_url = ''

    # size
    width = None
    height = None

    # fps
    fps = 5

    # file
    video_title = ''
    video_dirpath = ''
    video_filepath = ''

    # converted files
    video_gif = ''
    video_apng = ''

    # auth
    password = None

    def __init__(self, download_url = '', args = {}):
        # check if python modules are installed: youtube-dl
        # check if ffmpeg is installed
        # throw exception if no

        # Set width.
        if 'width' in args: self.width = args['width']

        # Set height.
        if 'height' in args: self.height = args['height']

        #if (self.width is None and self.height is not None) or (self.width is not None and self.height is None):
        #if bool(self.width is not None) ^ bool(self.height is not None):
        #  raise VideoPNGExtractorError("Size should be set as pair of Width and Height")

        # set FPS
        if 'fps' in args and args['fps'] is not None: self.fps = args['fps']

        # Set password
        if 'password' in args: self.password = args['password']

        # Set URL.
        self.download_url = download_url

    def create_work_folder(self, video_title):
        video_dirpath = os.path.join(VIDEO_PNG_DIR, video_title)
        if not os.path.exists(video_dirpath):
            os.makedirs(video_dirpath)

        self.video_dirpath = video_dirpath

    def load(self):
        path = self.download_url

        if not os.path.isfile(path):
            raise VideoPNGExtractorError("Selected file is not readable")

        self.video_filepath = path
        video_filename = os.path.basename(path)
        video_title = os.path.splitext(video_filename)[0]
        self.video_title = self.title = video_title
        self.create_work_folder(video_title)

    def download(self):
        # Get video meta info and then download using youtube-dl

        # @TODO: Add to options auth if provided.
        ydl_opts = {}

        # Get meta data of the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(self.download_url, download=False)

        self.title = meta['title']

        # renaming the file
        # remove special characters from the file name
        video_title = ''.join(c for c in meta['title'] if c.isalnum() or c == '-' or c == '_')
        self.video_title = video_title

        extension = meta['ext']
        video_filename = video_title + '.' + extension

        # create the folder for video
        self.create_work_folder(video_title)

        # create the full path for video file
        video_filepath = os.path.join(self.video_dirpath, video_filename)

        #
        cmd = ['youtube-dl', '-k', '-o', video_filepath, self.download_url]

        # if height was set then setting filter format for video
        if self.height is not None:
            filter_format = 'bestvideo[height <=? %(height)i]+bestaudio/best[height <=? %(height)i]' % {
                "height": self.height}
            cmd.extend(['-f', filter_format])

        print("request=%s" % cmd)

        # download the video
        subprocess.call(cmd)

        # set file path
        self.video_filepath = video_filepath

    def create_gif(self):
        video_filter = "fps=%(fps)i" % {"fps" : self.fps}

        # setting scale options
        # width scale
        if self.width is None or self.width <= 0:
            width = -1
        else:
            width = self.width

        # height scale
        if self.height is None or self.height <= 0:
            height = -1
        else:
            height = self.height

        # adding scale options to video filtering
        if width <> -1 and height <> -1:
            scale = "scale='if(gt(a,%(width)i/%(height)i),%(width)i,-1)':'if(gt(a,%(width)i/%(height)i),-1,%(height)i)'" % {"width" : width, "height" : height}
        else:
            scale = "scale='%(width)i:%(height)i'" % {"width" : width, "height" : height}

        video_filter += ",%(scale)s" % {"scale" : scale}


        video_gif = os.path.join(self.video_dirpath, self.video_title + '.gif')
        self.video_gif = video_gif
        cmd = ['ffmpeg', '-v','warning', '-i', self.video_filepath, '-vf', video_filter, '-vsync', 'vfr', video_gif]

        print("creating frames...")
        print(cmd)

        # create iframes
        subprocess.call(cmd)

    def create_apng(self):
        video_apng = os.path.join(self.video_dirpath, self.video_title + '.png')
        self.video_apng = video_apng
        cmd = ['gif2apng', self.video_gif, self.video_apng]

        subprocess.call(cmd)

class VideoPNGExtractorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def check_args(args=None):

    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--url',
                        help='youtube/vimeo video\'s url',
                        required='True')

    parser.add_argument('-width', '--width', type=int,
                        help='width of generated gif/apng')

    parser.add_argument('-height', '--height', type=int,
                        help='height of generated gif/apng')

    parser.add_argument('-fps', '--fps', type=int,
                        help='number of frames per second')


    results = parser.parse_args(args)
    return (results.url,
            results.width,
            results.height,
            results.fps)


if __name__ == "__main__":
    url, width, height, fps = check_args(sys.argv[1:])
    extractor = VideoPNGExtractor(url, {'width': width, 'height': height, 'fps': fps});
    extractor.download()
    extractor.create_gif()
    extractor.create_apng()

# python video_extractor.py -u https://vimeo.com/164152168