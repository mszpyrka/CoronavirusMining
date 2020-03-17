from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

if __name__ == "__main__":
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    fileList = drive.ListFile({'q': "'1gCy3UlgGHDPA1CW5-mNh8zr5SO7-_gI3' in parents and trashed=false"}).GetList()
    for file in fileList:
        print(file['title'] + ' ' + file['id'])
