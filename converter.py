import argparse
import lfiles3 as lf
import video as conv
import infogt5 as ig

def convert():
    pass

# Top-Level parser 
prime_parser = argparse.ArgumentParser(add_help=False)

# To handle Subparsers Level 1
main_parser = argparse.ArgumentParser(description="convert a/v or img, or get information about them.\n'av' = both audio and video files.\nOperation is either convert|info", prog="converter")
main_parser.add_argument('input', help='Input path string')

# ACTION Subparser L1 setup
action_subparsers = main_parser.add_subparsers(title='Actions', dest='action_cmd',help ="Choose convert or info")
# Subparser L1-A 'convert'
convert_parser = action_subparsers.add_parser('convert', help='Convert media', parents=[prime_parser])
# Subparser L1-B 'info'
info_parser = action_subparsers.add_parser('info', help='Get media info', parents=[prime_parser])


# Subparser L1-A CONVERT args
convert_parser.add_argument('type', choices=['video','audio','image'], help="Choose target media btwn video|audio|image")


video_subparser = convert_parser.add_subparsers(title='Video Convert Options', dest='video_opts')
audio_subparser = convert_parser.add_subparsers(title='Audio Convert Options', dest='audio_opts')
image_subparser = convert_parser.add_subparsers(title='Image Convert Options', dest='image_opts')

convert_parser.add_argument('-e', dest="ext", type=str, help="Choose output extension")
convert_parser.add_argument('-r', dest="fps", type=int, help="Adjust video frame rate, enter digits")
convert_parser.add_argument('-vc', dest="video_codec", type=str, help="Select video codec, name must be valid")
convert_parser.add_argument('-s', dest="size", type=str, help="Adjust size, enter in format '###x###'")
convert_parser.add_argument('-ac', dest="audio_codec", type=str, help="Select audio codec, name must be valid")
convert_parser.add_argument('-o',dest='output', type=str, help='Output path string (for conversion output)',required='convert')
# Sub-sub for video codec selection libx264
# IF Video codec = libx264, then enable these (not yet implemented)
x264_subparser = convert_parser.add_subparsers(title='x264 options', dest='crf')
x264_parser = x264_subparser.add_parser('cfr',parents=[prime_parser], help="IF libx264 selected as video codec,this is the quality; higher = lowerQ & smaller file [20 - 30]")
# Subparser 'info' args
info_parser.add_argument('type', choices=['video','audio','av','image'], help='select media to get info on from video|audio|av|image')
info_parser.add_argument('-e', dest='ext', help="returns the number of the given extension")
info_parser.add_argument('-lm', dest='long_media', help="returns the a/v media with the longest duration")
info_parser.add_argument('-sm', dest='short_media', help="returns the a/v media with the shortest duration")
info_parser.add_argument('-c', dest=None, help='returns printout of all codecs in collection of a/v files')
info_parser.add_argument('-li', dest='long_img',help='returns the image with the largest overall size (by pixels)')
info_parser.add_argument('-si', dest='short_img', help='returns the image with the smallest overall size (by pixels)')

args=main_parser.parse_args()
#args = prime_parser.parse_args()
print(args)


if args.action_cmd == 'convert':
    print("Convert Actions")
    if args.type == 'video':
        print("Video Convert")
        if args.ext:
            print(f"Ext {args.ext} given")
            ext = args.ext
        if args.fps:
            print(f"FPS {args.fps} given")
        if args.video_codec:
            print(f"Video codec {args.video_codec} given")
        if args.size:
            print(f"Size {args.size} given")
        if args.audio_codec:
            print(f"Audio codec {args.audio_codec} given")
        
    elif args.type == 'audio':
        print("Audio Convert")
    elif args.type == 'image':
        print("Image Convert")
    else: raise Exception("Bad type. Must be video, audio or image to convert")

if args.action_cmd == 'info':
    print("Info Actions")
    if args.type =='video':
        print("Video Info")
        # print list of videos in collection
    elif args.type == 'audio':
        print("Audio info")
        # print list of audios in collection
    elif args.type == 'image':
        # print list of images in collection
        print("Image info")


 
