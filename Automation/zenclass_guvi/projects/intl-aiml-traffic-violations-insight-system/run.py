import subprocess
import sys

if __name__ == '__main__':
    print('Starting Flask backend...')
    subprocess.run([sys.executable, 'backend/app.py'])
