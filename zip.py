import zipfile
import os

def create_code_zip(excludes=[]):
    print('Start zipping code into code.zip...')
    zf = zipfile.ZipFile('/tmp/code.zip', mode='w')
    try:
        for root, dirs, files in os.walk('.'):
            for filename in files:
                if filename.startswith('.'):
                    continue
                file_path = os.path.join(root, filename)
                if os.path.islink(file_path):
                    print('Skip symbol link:', file_path)
                    continue
                is_excluded = False
                for exclude in excludes:
                    if file_path.startswith(exclude):
                        is_excluded = True
                        break
                if not is_excluded:
                    zf.write(file_path)
    except Exception as e:
        print('Exception when creating /tmp/code.zip:', e)
        exit(1)
    finally:
        print('zip complete')
        zf.close()
