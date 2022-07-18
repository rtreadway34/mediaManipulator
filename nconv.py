import argparse as a

def argparser():
    # PRIME PARSER
    prime_parser = a.ArgumentParser()

    # MAIN PARSER
    parser = a.ArgumentParser()
    parser.add_argument('input') # INPUT PATH for Collector

    # Init SUBS
    action_subparsers = parser.add_subparsers(title='Media File Actions', dest='action_cmd',help="Choose the general action to perform. Either Conversion of Media, or Info Retrieval")
    action_subparsers.required = True

    # SUB: CONVERT
    convert_parser = action_subparsers.add_parser('convert',help='Convert media using ffmpeg')
    # SUB: INFO
    info_parser = action_subparsers.add_parser('info', help='Get info aboutcollected media files')

    # Info ARGS
    # NOTE: I'm thinking 'type' below should be an option to return a list of media of given type. It's not making sense to make it mandatory as it would muck up the coding for the other options
    info_parser.add_argument('-gt',dest='get', choices=['video', 'audio', 'av', 'image'], help="get a listing from the collection of a selected media type")
    info_grp = info_parser.add_mutually_exclusive_group()
    info_grp.add_argument('-e', dest='ext', help='returns the number of files in the collection with the given extension')
    info_grp.add_argument('-lm', dest='long_media', choices=['video','audio','both'],help='returns the media with the longest duration, only works with video, audio or both')
    info_grp.add_argument('-sm', dest='short_media', choices=['video','audio','both'],help='returns the media with the shortest duration, only works with video, audio or both')
    info_grp.add_argument('-c', dest='codecs', action='store_true', help='returns printout of all codecs in the collection of a/v files')
    info_grp.add_argument('-li', dest='large_img', action='store_true', help='returns information about the image with the largest overall size (by pixels)')
    info_grp.add_argument('-si', dest='small_img', action='store_true', help='returns information about the image with the smallest overall size (by pixels)')

    # Init CONVERT SUBS
    conversion_cmds = convert_parser.add_subparsers(title='Conversion Options',dest='convert_opts')

    # CONVERT_SUBS: Video/Audio/Image
    # VIDEO
    conv_vid = conversion_cmds.add_parser('video')
    conv_vid.add_argument('-vc', dest='vc',metavar='[ffmpeg video codec]', type=str, help='Video codec for output video')
    conv_vid.add_argument('-ac', dest='ac', metavar='[ffmpeg audio codec]', type=str, help='Audio codec for output video')
    conv_vid.add_argument('-e', dest='ext', type=str, help='output file extension')
    conv_vid.add_argument('-r', dest='fps',type=int, help='Output video FPS')
    conv_vid.add_argument('-s', dest='size', type=str,metavar='[width x height]', help='Adjust output video size, enter in format ###x### (numbers separated by "x")')
    conv_vid.add_argument('-af', dest='vid_freq', type=int, metavar='[freq in Hz]',help='Frequency for the audio track of the output video')
    conv_vid.add_argument('-vb', dest='vid_bitrt', help='Bitrate for video track')
    conv_vid.add_argument('-ab', dest='aud_bitrt', type=int, help='Bitrate for audio track')
    conv_vid.add_argument('-o',dest='output', metavar='[output path]',type=str,help='output file path')
    # VIDEO: x264 quality
    conv_vid.add_argument('-crf', dest='crf', type=int, help='If libx264 selected as video codec, this adjusts the quality; higher = lowerQ & smaller file [20-30]')

    # AUDIO
    conv_aud = conversion_cmds.add_parser('audio')
    conv_aud.add_argument('-ac', dest='ac',metavar='[FFmpeg AC name]', help='Audio codec for output file')
    conv_aud.add_argument('-e', dest='ext', help='output file extension, should match the codec/container type desired')
    conv_aud.add_argument('-f', dest='freq', metavar='[freq in Hz]', help='output file frequency in Hz')
    conv_aud.add_argument('-b', dest='bitrt', type=int, metavar='[Bitrate number]', help='output file bitrate')
    conv_aud.add_argument('-o',dest='output',metavar='[Output Path]',help='output file path')
    # IMAGE
    conv_img = conversion_cmds.add_parser('image')
    conv_img.add_argument('-s', dest='size', help='Change image dimensions')
    conv_img.add_argument('-f', dest='fmt', help='Change image format')
    conv_img.add_argument('-c', dest='comp', help='Change image compression value, where applicable')
    conv_img.add_argument('-x', dest='crop', help='Crop image according to given dimensions')


    args=parser.parse_args()
    return args

if __name__ == "__main__":
    args = argparser()

def cmd_builder(args):
    '''NOTE: For A/V, temporarily returns an ffmpeg cmd.  Must be modified or implemented to call ffmpeg (Not sure if it should be integrated into the class?) '''
    input_dir = args.input
    ff_cmd_base = f'ffmpeg -i {input_dir} '

    if args.action_cmd == 'convert':
        # VIDEO CONVERT ARGUMENT BUILD
        if args.convert_opts == 'video':
            v_opts = ['vc', 'ac', 'ext','fps','size','vid_freq','vid_bitrt','aud_bitrt','crf']
            ff_vidopts = {k:v for (k,v) in vars(args).items() if v != None and k in v_opts}
            if 'vc' in ff_vidopts.keys():
                ff_cmd_base += f'-c:v {ff_vidopts["vc"]} '
                if ff_vidopts['vc'] == 'libx264':
                    if 'crf' in ff_vidopts.keys():
                        ff_cmd_base += f'-crf {ff_vidopts["crf"]} '
            if 'ac' in ff_vidopts.keys():
                ff_cmd_base += f'-c:a {ff_vidopts["ac"]} '
            if 'ext' in ff_vidopts.keys():
                pass
            if 'fps' in ff_vidopts.keys():
                ff_cmd_base += f'-r {ff_vidopts["fps"]} '
            if 'size' in ff_vidopts.keys():
                ff_cmd_base += f'-s {ff_vidopts["size"]} '
            if 'vid_freq' in ff_vidopts.keys():
                ff_cmd_base += f'-ar {ff_vidopts["aud_bitrt"]} '
            if 'vid_bitrt' in ff_vidopts.keys():
                ff_cmd_base += f'-b:v {ff_vidopts["vid_bitrt"]} '
            if 'aud_bitrt' in ff_vidopts.keys():
                ff_cmd_base += f'-ab {ff_vidopts["aud_bitrt"]} '
            ff_cmd_base += f'{args.output}'
            return ff_cmd_base
        # AUDIO CONVERT ARGUMENT BUILD
        elif args.convert_opts == 'audio':
            a_opts = ['ac', 'ext', 'freq', 'bitrt']
            ff_audopts = {k:v for (k,v) in vars(args).items() if v!= None and k in a_opts}
            if 'ac' in ff_audopts.keys():
                ff_cmd_base += f'-c:a {ff_audopts["ac"]} '
            if 'freq' in ff_audopts.keys():
                ff_cmd_base += f'-ar {ff_audopts["freq"]} '
            if 'bitrt' in ff_audopts.keys():
                ff_cmd_base += f'-ab {ff_audopts["bitrt"]} '
            ff_cmd_base += f'{args.output}'
            return ff_cmd_base
        # IMAGE CONVERT ARGUMENT BUILD
        elif args.convert_opts == 'image':
            print("Image conversion")
            i_opts = ['size','fmt','comp','crop']
            imgopts = {k:v for (k,v) in vars(args).items() if v != None and k in i_opts}
            if 'size' in imgopts.keys():
                print("Call image converter size change")
            if 'fmt' in imgopts.keys():
                print("Call image converter format change")
            if 'comp' in imgopts.keys():
                print("Depending on selected format, modify compression")
            if 'crop' in imgopts.keys():
                print("Crop image according to given dimensions")

    elif args.action_cmd == 'info':
        # info block
        if args.ext:
            print(f"Call numofext('{args.ext}')")
        elif args.get:
            if args.get == 'video':
                print("Print detail list of video files")
            elif args.get == 'audio':
                print("Print detail list of audio files")
            elif args.get == 'image':
                print("Print detail list of image files")
        elif args.long_media != None:
            print(f"Call longestmedia('{args.long_media}', size='long')")
        elif args.short_media != None:
            print(f"Call longestmedia('{args.short_media}', size='short')")
        elif args.codecs == True:
            print("Call codecs(), returns dict, perhaps create a formatter func")
        elif args.large_img == True:
            print("Call largestimg(size='large')")
        elif args.small_img == True:
            print("Call largestimg(size='small')")
            
print(cmd_builder(args))
