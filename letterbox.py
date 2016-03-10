#!/usr/bin/python

import sys
import os
import subprocess
import json
from fractions import gcd


# Check if video is 16:9 using ffprobe
def is_16_9(video_path):
    p = subprocess.Popen(['ffprobe',
                          '-v', 'error',
                          '-show_entries',
                          'stream=width,height',
                          '-of', 'json',
                          video_path],
                          stdout=subprocess.PIPE)
    result = p.communicate()
    aspect_info = json.loads(result[0])
    # Create tuple of resolution i.e. (1280, 720)
    resolution = (int(aspect_info['streams'][0]['width']),
              int(aspect_info['streams'][0]['height']))

    # Check if video is 16:9
    if not (gcd(resolution[0], 16) == 16 and gcd(resolution[1], 9) == 9):
        return (False, resolution)

    return (True,)


# If not 16:9, resize video and add letterbox to make 16:9
def letterbox(video_path, resolution):
    new_path = os.path.join(os.path.dirname(video_path),
                            'LETTERBOXED_' + os.path.basename(video_path))

    if resolution[0] <= 1280:
        width = 1280
        height = 720
    else:
        width = 1920
        height = 1080

    p = subprocess.Popen(['ffmpeg',
                          '-i', video_path,
                          '-filter:v',
                          ('scale=(sar*iw)*min({width}/(sar*iw)\,{height}/ih)'
                           ':ih*min({width}/(sar*iw)\,{height}/ih),'
                           ' pad={width}:{height}:({width}-(sar*iw)*min'
                           '({width}/(sar*iw)\,{height}/ih))/2:({height}-'
                           'ih*min({width}/(sar*iw)\,'
                           '{height}/ih))/2').format(width=width,
                                                    height=height),
                           new_path])
    p.communicate()
    return new_path


def main():
    try:
        video_path = sys.argv[1]
    except IndexError:
        print 'Enter filepath of video as argument please!'
        sys.exit()

    resolution = is_16_9(video_path)
    if resolution[0]:
        print 'Already 16:9'
        return

    letterbox(video_path, resolution[1])


if __name__ == '__main__':
    main()
