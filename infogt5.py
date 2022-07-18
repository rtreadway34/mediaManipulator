'''Parse ffpmeg -i <file> output & display pertinent info about the file
'''
from pymediainfo import MediaInfo as mi
import os, filetype
import nconv

def listselect(paths):
    '''Snoop through a tdict containing DirObjects and determine how many different filetypes there are.  If more than one, pass to sortfile().  Otherwise pass to printfile()
    NOTE: Have to rewrite this docstring, since sortfile, printfile and process are now merged into listselect
    '''
    tdict = {}
    # convert list of paths to a dict, or a single path to a dict
    if type(paths) == list:
        for i in range(len(paths)):
            tdict[i] = paths[i] 
    else:
        tdict[0] = paths
    for k, v in tdict.items():
        filelist = []
        obj = os.scandir(v)
        for j in obj:
            if j.is_dir() == False:
                filelist.append(j)
        obj.close()
        tdict[k] = filelist 
    copy = tdict
    mtch = True
    # Get a first target for comparisons. NOTE: Better to use the function made for this?
    first = filetype.guess_mime(copy[0][0].path).split('/')[0]

    for k,v in tdict.items():
        for file in v:
            #print("FILE IS: ", file)
            if filetype.guess_mime(file.path) == None:
                pass
            elif filetype.guess_mime(file.path).split('/')[0] != first:
                #print("FIRST NOT MATCH", file)
                mtch = False
                break
        if mtch == False:
            break
    if mtch == False:
        types = ["video","audio","image"]
        output = {
            types[0]: [],
            types[1]: [],
            types[2]: []
            }
        for k, v in tdict.items():
        #print("k is:",k," and v is :",v)
            for file in v:
           # print("FILE is: ",file)
                if filetype.guess_mime(file.path) == None:
                    pass
                elif filetype.guess_mime(file.path).split('/')[0] == "video":
                    output['video'].append(file.path)
                elif filetype.guess_mime(file.path).split('/')[0] == "audio":
                    output['audio'].append(file.path)
                elif filetype.guess_mime(file.path).split('/')[0] == "image":
                    output['image'].append(file.path)
                else: pass
    else: 
        output = []
        types = ["video","audio","image"]
        for k,v in tdict.items():
            for file in v:
                if filetype.guess_mime(file.path) == None:
                    pass
                elif filetype.guess_mime(file.path).split('/')[0] in types :
                    output.append(file.path)
    return output

class MediaInfoCollector:
    def __init__(self, paths=os.getcwd()):
        basket = listselect(paths)

        if type(basket) == dict:
            for k,v in basket.items():
                if k == 'video':
                    self.videos = basket.get('video')
                elif k == 'audio':
                    self.audios = basket.get('audio')
                else: self.images = basket.get('image')
        else:
            print("OTHER TYPE", type(basket))
            raise TypeError("Input is the wrong type or none given.  Input argument must be a dict.")

        self.vidct, self.audct, self.imgct = len(self.videos), len(self.audios), len(self.images)
        self.total_items = self.vidct + self.audct + self.imgct
        self.vinfo, self.ainfo, self.iinfo = [], [], []
        if self.videos != []:
            for i in self.videos:
                self.vinfo.append(self.__getinfo__(i))
        if self.audios != []:
            for i in self.audios:
                self.ainfo.append(self.__getinfo__(i))
        if self.images != []:
            for i in self.images:
                self.iinfo.append(self.__getinfo__(i))
        self.collect = self.vinfo + self.ainfo + self.iinfo
            
    def __str__(self):
        return f"****************\nMedia Collection object: Collected {self.total_items} media files with\n{self.vidct} videos\n{self.audct} audios\n{self.imgct} images\n****************"

    def __getinfo__(self, inpt):
        ''' populates the dict of information for a media file. Takes a path to a file, parses it with pymediainfo, and gathers info from each available media track
        Returns a single dict with file information as the first 4 keys, and 1-2 inner dicts containing A/V/I informations, depending on the media'''

        # Initialize the output dict and parse the input path
        fileinfo = {}
        inpt = mi.parse(inpt)
        
        for track in inpt.tracks:
            # Do we have a "General" track? Most of the time we should
                if track.track_type == 'General':
                    # Get index for last instance of '/' in the complete_name str, which includes the path
                    idx = track.complete_name.rindex('/')
                    # We use that index to slice off the filename from the path, and strip off the leading '/'
                    second = track.complete_name[idx:].lstrip('/')
                    # In filename, get index of last instance of '.', so we can account for extra periods in filenames
                    lastdot = second.rindex('.')
                    # set k/v pairs in output dict
                    fileinfo['filename'] = second[:lastdot]
                    fileinfo['extension'] = second.split('.')[-1]
                    fileinfo['path'] = track.complete_name[:idx+1]
                    fileinfo['filetype'] = track.internet_media_type.split('/')[0]
                if track.track_type == "Video":
                    fileinfo['video_info'] = {
                    'track_type' : track.track_type,
                    'format' : (track.format_info, track.format_profile),
                    'codec' : (track.codec_id, track.codec_id_info),
                    'size' : (track.height, track.width),
                    'duration' : track.other_duration[4],
                    'stream location' : (track.stream_identifier, track.stream_order, track.track_id),
                    'framerate' : (track.other_frame_rate, f"Total Frames: {track.frame_count}")
                    }
                if track.track_type == "Audio":
                    fileinfo['audio_info'] = {
                    'track_type' : track.track_type,
                    'format' : track.format_info,
                    'codec' : track.codec_id,
                    "compression" : track.compression_mode,
                    'duration' : track.other_duration[4],
                    'stream location' : (track.stream_identifier, track.stream_order, track.track_id),
                    'framerate' : (track.other_frame_rate, f"Total Frames: {track.frame_count}"),
                    'channels' : (track.channels, track.channel_positions),
                    'sample_rate' : track.sampling_rate
                    }
                if track.track_type == 'Image':
                    fileinfo['image_info'] = {
                    'track_type': track.track_type,
                    'size' : (track.height, track.width), 
                    'format' : track.format_info,
                    'colorspace' : track.color_space,
                    "compression" : track.compression_mode,
                    'bit depth': track.bit_depth,
                    'stream location' : (track.stream_identifier, track.stream_order, track.track_id)
                    }
        return fileinfo


    def __getone__(self,mode,attrib):
        # Method to get initial "first target" file values for external methods dealing with min/max style searches
        # Mode = video|audio|image, and enables selection of a type
        # attrib = which data to pull for that first file
        # Returns the 'attrib' and the file's name
        # Handles exceptions for wrong mode type given

        # Make a quick dictionary for more readable code
        d = {'video':'video_info', 'audio':'audio_info','image':'image_info'}
        if mode == 'video':
            # first ensure the target mode list not empty
            if self.vinfo != []:
                # Select first video from list
                v = self.vinfo[0]
                return v[d[mode]][attrib], v['filename']+'.'+v['extension']
            else: 
                raise Exception("No videos in selection, select a mode corresponding to existing media.")
        elif mode == 'audio':
            if self.ainfo != []:
                a = self.ainfo[0]
                return a[d[mode]][attrib], a['filename']+'.'+a['extension']
            else: 
                raise Exception("No audio files in selection, select a mode corresponding to existing media.")
        elif mode =='image':
            if self.iinfo != []:
                i = self.iinfo[0]
                return i[d[mode]][attrib], i['filename']+'.'+i['extension']
            else: 
                raise Exception("No images in selection, select a mode corresponding to existing media.")
        else:
            raise TypeError("Bad type, choose from 'video', 'audio' or 'image' as mode ONLY")


    def numofext(self, ext:str):
        # get # of extensions of specified 3 char type
        # first qualify the length of the given extension
        if 2 <= len(ext) <= 4:
            count = 0
            for file in self.collect:
                if file['extension'] == ext:
                    count += 1
        else:
            raise ValueError("Detected inappropriate file length.  Value must be between 2 and 4, and must be a real media extension")
        # Account for the case where the entered extension is valid by length, but is not in the set of media.
        if count == 0:
            return "'{}' is not in the collection of media".format(ext)
        else:
            return count


    def longestmedia(self,which,size='long'): 
        '''Arg 'which' must be of audio|video|both
        Arg 'size' must be short|long, defaults to long
        Returns string with results'''

        # verify arguments, quit if incorrect
        if not which or which not in ['audio','video','both']:
            raise TypeError("You forgot to specify 'which' from audio|video|both, or you entered a wrong value")
        if size not in ['short','long']:
            raise ValueError("Argument 'size' selection '{}' is not a valid selection. Please choose from 'short' or 'long', or omit arg to default to 'long'".format(size))

        def parseone(parsed):
            # called for video OR audio
            #check input 'which'
            if parsed == 'video': 
                # Grab initial data for further comparison, using __getone__()
                dur, tgt = self.__getone__('video', 'duration')
                p = ['video', 'video_info']
                # iter over list of file dicts
                for file in self.vinfo:
                    # assign video_info intrnl dict to var
                    v = file[p[1]]   
                    # check for size toggle
                    if size == 'short':
                        # do shorter dur compare
                        if v['duration'] < dur:
                        #update dur if current is shorter and update a full filename var
                            dur = v['duration']
                            tgt = file['filename']+'.'+file['extension'] 
                    # check for size toggle
                    elif size == 'long':
                        #do longer dur compare
                        if v['duration'] > dur:
                            #update dur if current is longer and update a full filename var
                            dur = v['duration']
                            tgt = file['filename']+'.'+file['extension']        
                    else: 
                        raise ValueError("Choose 'long' or 'short' for size argument, or leave blank for 'long'")

            # same shit as 'video' section above, but for audio files
            elif parsed == 'audio':
                dur, tgt = self.__getone__('audio', 'duration')
                p = ['audio','audio_info']
                for file in self.ainfo:
                    a = file[p[1]]
                    if size == 'short':
                        if a['duration'] < dur:
                            dur = a['duration']
                            tgt = file['filename']+'.'+file['extension']
                    elif size == 'long':
                        if a['duration'] > dur:
                            dur = a['duration']
                            tgt = file['filename']+'.'+file['extension']
                    else: 
                        raise ValueError("Choose 'long' or 'short' for size argument, or leave blank for 'long'")
            return "{} file {} has the {}est duration at {}".format(parsed.title(),tgt,size,dur)
            
        def parseall():
            # Since 'both', check to ensure there are elements in BOTH vinfo and ainfo lists of info dicts
            if self.vinfo and self.ainfo:
                avcomb = self.vinfo + self.ainfo
                # set initial duration and target file, doesn't matter if from audio or video since BOTH
                dur, tgt = self.__getone__('video', 'duration')
                # iter through file info collection, check for 'size' value, then perform appropriate comparisons and variable updates
                for file in avcomb:
                    if size == 'long':
                        if 'video_info' in file.keys():
                            v = file['video_info']     
                            if v['duration'] > dur:
                                dur = v['duration']
                                tgt = file['filename']+'.'+file['extension']
                        elif 'audio_info' in file.keys():
                            a = file['audio_info']
                            if a['duration'] > dur:
                                tgt = file['filename']+'.'+file['extension']
                                dur = a['duration']
                    if size == 'short':
                        if 'video_info' in file.keys():
                            v = file['video_info']     
                            if v['duration'] < dur:
                                dur = v['duration']
                                tgt = file['filename']+'.'+file['extension']
                        elif 'audio_info' in file.keys():
                            a = file['audio_info']
                            if a['duration'] < dur:
                                tgt = file['filename']+'.'+file['extension']
                                dur = a['duration']
            else:
                # in the case where vinfo and/or ainfo are empty, end program with error raised
                empty = ""
                if self.vinfo == [] and self.ainfo == []:
                    empty = "video & audio"
                elif self.ainfo == []:
                    empty = "audio"
                elif self.vinfo == []:
                    empty = "video"
                raise RuntimeError("BOTH Audio and Video files required for 'both'... {} list empty".format(empty))
            # if all goes well, return string with result
            return "File {} has the duration at {}, {}est of both Video and Audio".format(tgt,dur,size)
        
        # CALL SECTION FOR INTERNAL METHODS
        # deals with the 'which' type selection, and calls the appropriate method 
        if which == 'both':
            return parseall()
        elif which == 'video':
            return parseone('video')
        elif which == 'audio': 
            return parseone('audio')
        else: 
            raise ValueError("Argument 'which' selection '{}' is not a valid selection. Please choose from 'video', 'audio' or 'both'".format(which))


    def codecs(self):
        '''Returns a dict containing a dict each for parsed video and audio codecs.  The inner video dict's values are a set of respective video and audio codecs for each video. Dict can then be parsed by user 
        v['codec'] represents the 2 member set (video_codec_id, video_codec_id_info) and a['codec'] represents the single audio codec per media file
        '''
        vCodec={}
        aCodec={}        
        for file in self.vinfo + self.ainfo:
            if file['filetype'] == 'video':
                v, a = file['video_info'], file['audio_info']
                vCodec[file['filename']] = [(v['codec'][0], a['codec'])]
                continue
            elif file['filetype'] == 'audio':
                a = file['audio_info']
                aCodec[file['filename']] = [a['format']]
                continue
        cDict = {
                'videoCodecs': vCodec, 
                'audioCodecs': aCodec}
        return cDict


    def largestimg(self,size='large'):
        '''Parses through list of images comparing total sizes in pixels and returns a result string.
        'size' arg can be short|long, with default = long'''
        # Verify size arg
        if size not in ['large','small']:
            raise ValueError("Bad value for 'size' argument.  Must be 'small' or 'large'")
        # Using try/except experimentally in this case since I'm a noob 
        try:
            #initialize first values, which will be used to compare to the images in the list
            firstimgsz, firstname = self.__getone__('image','size')
            firstimgpix = firstimgsz[0] * firstimgsz[1]
            tgtname = ''
            filexy = (firstimgsz[0], firstimgsz[1])
            # SMALLER IMG check
            if size =='small':
                for file in self.iinfo:
                    i = file['image_info']
                    x, y = i['size'][0], i['size'][1]
                    filename = file['filename']+'.'+file['extension']
                    # if the current file is the same as the "first", skip it
                    if filename == firstname and x*y == firstimgpix:
                        continue
                    if x*y < firstimgpix:
                        filexy = (x,y)
                        firstimgpix = x*y
                        tgtname = filename  
            
            # LARGER IMG check
            elif size == 'large' or None:
                for file in self.iinfo:
                    i = file['image_info']
                    x, y = i['size'][0], i['size'][1]
                    filename = file['filename']+'.'+file['extension']
                    if filename == firstname and x*y == firstimgpix:
                        continue
                    if x*y > firstimgpix:
                        filexy = (x,y)
                        firstimgpix = x*y
                        tgtname = filename
            return "{}-est image is {} at {}x{} or total {} pixels.".format(size, tgtname, filexy[0], filexy[1], firstimgpix)
        # Account for issues in input and args 
        except TypeError as era:
            print("Exception in type. Must always be 'image' for this function")
            print(era.__class__, '-', era)
        except Exception as err:
            print("Something went wrong.  Make sure you're passing images to this function")
            print(err.__class__, '-', err)
            

    def convert(self, mode='video',verbose=False):
        output_path = input("Choose output path (leave blank for default './out'> ")
        if os.output_path.isdir(path) == True:
            print("Path already exists")
        #return output_path
        else:
            try:
                os.mkdir(output_path)
                print("Path '{}' created successfully".format(output_path)) 
                #return output_path
            except Exception as err:
                print("Something went wrong with the specified output_path.  Check your syntax")
                print(err.__class__, '-', err)

        
        if mode == 'video':
            pass
        elif mode == 'audio':
            pass
