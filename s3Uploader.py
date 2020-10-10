#!/usr/bin/python -tt
import sys
import boto3

S3_BUCKET_NAME = '<BUCKET_NAME>'
S3_ROOT_KEY = '<ROOT_PATH>/' 
def upload(localFile, targetKey):
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(S3_BUCKET_NAME)
  rootDir = S3_ROOT_KEY
  # '<path>/Music Lists/Oct2020/Alicia Keys/The Element Of Freedom/02 Love Is Blind.mp3'
  #source3/Alicia Keys/test.mp3'
  data = open(localFile, 'rb')
  print "Uploading... key:" + targetKey + ' binary:' + localFile
  bucket.put_object(Key=rootDir + targetKey, Body=data)

def main():
  if len(sys.argv) >= 3:
    localBinary = sys.argv[1]
    targetDir = sys.argv[2]
  else:
    print 'Specify the s3 directory and local binary to upload'

  upload(localBinary, targetDir)

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
