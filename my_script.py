import os
import shutil

if os.path.exists('gen_sv_test.py'):
    os.remove('gen_sv_test.py')

src=r'C:\Users\cychang\Documents\GitHub\audio_phase\gen_sv_test.py'
shutil.copy(src, os.getcwd())
print('------------------------------------------')
os.system('python gen_sv_test.py')