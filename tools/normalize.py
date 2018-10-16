#####
# Default Sampling Rate: 16000
# Default Bit Rate: 24K
#####

import os
import glob
import subprocess
import re
import shutil

FILES_PATTERN = 'rec-*.mp3'
SOURCE_FILE_PREFIX_CHAR_COUNT = 4
DEST_FILE_PREFIX = 'voice-'

if __name__ == '__main__':
    if os.name == 'nt': # Windows
        pipe_null = 'NUL'
    else:
        pipe_null = '/dev/null'
    files = glob.glob(FILES_PATTERN)

    for source_path in files:
        bare_path = source_path[SOURCE_FILE_PREFIX_CHAR_COUNT:]
        filtered_path = 'filtered-' + bare_path
        voice_path = DEST_FILE_PREFIX + bare_path
        if os.path.isfile(voice_path):
            continue
        subprocess.call('ffmpeg -i "%s" -af "highpass=f=200, lowpass=f=3000" -n "%s"' % (source_path, filtered_path),
            stderr=subprocess.STDOUT, shell=True)
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
