''' Consolidate pertinent ffmpeg conversion options for A & V '''

import os
import infogt5 as igt



def outdir(path='out'):
# Get output path from user, or use default "./out" in current dir
    path = input("Choose output path (leave blank for default './out'> ")
    if os.path.isdir(path) == True:
        print("Path already exists")
        #return path
    else:
        try:
            os.mkdir(path)
            print("Path '{}' created successfully".format(path)) 
            #return path
        except Exception as err:
            print("Something went wrong with the specified path.  Check your syntax")
            print(err.__class__, '-', err)
    return path


def convertIt(tgtdict, args):
    for k,v in tgtdict.items():
        fcmd = f"ffmpeg -i {k} {args} -hide_banner {v}"
        os.system(fcmd)

def vidprep(paths):
    output = {}
    outpath = outdir()
    if type(paths) == list:
        for path in paths:
            vinput = path
            p_idx = path.rindex('/')
            filenm = path[p_idx:].lstrip('/')
            e_idx = filenm.rindex('.')
            filenm_ext = filenm[e_idx:]
            justname = filenm[:e_idx]
            #print("Input file is: ",filenm, "with extension: ",filenm_ext)
            # Accounting for a new extension or not, and producing the appropriate output file target
            oext = input("Enter new extension, or leave blank for original: ")
            if oext == "":
                oext = filenm_ext
                voutput = outpath+'/'+filenm
            else:
                oext = "."+oext
                voutput = outpath+'/'+justname+oext
            #print("Out extension: ",oext)
            print("Output file: ",voutput)
            print("*************")
            output[vinput] = voutput
        
        args = ffargcollect()
    return output, args

def audconv(paths):
    outpath = outdir()
    if type(paths) == list:
        for path in paths:
            ainput = path
            p_idx = path.rindex('/')
            filenm = path[p_idx:].lstrip('/')
            aoutput = outpath+'/'+filenm
            args = ffargcollect() 
            convertIt(ainput,aoutput,args)

def ffargcollect():
    vc = input("Video Codec? ")
    ac = input("Audio Codec? ")
    # VIDEO
    if vc != '':
        if vc == 'libx264':
            crf = input("Set CRF for x264 [20-30, 30 = lower qual ")
            vc = f"-c:v {vc} -crf {crf}"
        vc = f"-c:v {vc}"
    else:
        vc = f"-c:v copy"
    # AUDIO    
    if ac != '':
        ac = f"-c:a {ac}"
    else:
        ac = f"-c:a copy"
    out = vc + ' ' + ac
    return out

