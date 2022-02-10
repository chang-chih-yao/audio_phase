import os
import shutil

if os.path.exists('gen_sv_test.py'):
    os.remove('gen_sv_test.py')

src=r'C:\Users\cychang\Documents\GitHub\audio_phase\gen_sv_test.py'
des=r'C:\Users\cychang\Documents\RTK\audio_data_phase\5575\gen\gen_sv_test.py'

shutil.copy(src, des)

print('------------------------------------------')
os.system('python gen_sv_test.py')