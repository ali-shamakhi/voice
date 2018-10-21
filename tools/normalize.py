#####
# Default Sampling Rate: 16000
# Default Bit Rate: 24K
#####

import os
import glob
import subprocess
import re
import shutil

MP3_REC_PATTERN = 'rec-*.mp3'
M4A_REC_PATTERN = 'rec-*.m4a'
SOURCE_FILE_PREFIX_CHAR_COUNT = 4
DEST_FILE_PREFIX = 'voice-'

if __name__ == '__main__':
    if os.name == 'nt': # Windows
        pipe_null = 'NUL'
    else:
        pipe_null = '/dev/null'

    files = glob.glob(MP3_REC_PATTERN)
    files.extend(glob.glob(M4A_REC_PATTERN))
    for source_path in files:
        bare_path = source_path[SOURCE_FILE_PREFIX_CHAR_COUNT:]
        filtered_path = 'filtered-' + bare_path
        voice_path = DEST_FILE_PREFIX + bare_path
        if os.path.isfile(voice_path):
            continue
        subprocess.call('ffmpeg -i "%s" -af "highpass=f=200, lowpass=f=3000" -n "%s"' % (source_path, filtered_path),
            stderr=subprocess.STDOUT, shell=True)
        if source_path[-4:].lower() == '.m4a':
            bare_path_mp3 = source_path[SOURCE_FILE_PREFIX_CHAR_COUNT:-4] + '.mp3'
            filtered_path_mp3 = 'filtered-' + bare_path_mp3
            voice_path_mp3 = DEST_FILE_PREFIX + bare_path_mp3
            subprocess.call('ffmpeg -i "%s" -vn -sn -dn -c:v copy -b:a 24k -ar 16000 -f mp3 "%s"' % (filtered_path, filtered_path_mp3))
            try:
                os.remove(filtered_path)
            except:
                pass
            filtered_path = filtered_path_mp3
            voice_path = voice_path_mp3
        vol_output = subprocess.check_output('ffmpeg -i "%s" -af "volumedetect" -vn -sn -dn -f null %s' % (filtered_path, pipe_null), 
            stderr=subprocess.STDOUT, shell=True).decode()
        vol = None
        for line in vol_output.splitlines():
            m = re.search('max_volume: -(.+?) ?dB', line)
            if m:
                vol = m.group(1)
                break
        if vol:
            print('vol: %s dB' % vol)
            subprocess.call('ffmpeg -i "%s" -af "volume=%sdB" -n "%s"' % (filtered_path, vol, voice_path),
                stderr=subprocess.STDOUT, shell=True)
        elif not os.path.isfile(voice_path):
            shutil.copyfile(filtered_path, voice_path)
        try:
            os.remove(filtered_path)
        except:
            pass