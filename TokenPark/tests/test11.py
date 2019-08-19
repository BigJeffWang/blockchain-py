#boto3
import boto3
s3 = boto3.resource('s3')

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

# Upload a new file
data = open('C:\\1.jpg', 'rb')
s3.Bucket('tokenpark-test').put_object(Key='2018年12月4日17:19:16/test.jpg', Body=data)



# Create an S3 client
#s3 = boto3.client('s3')

#filename = 'C:\\1.jpg'
#bucket_name = 'tokenpark-test'

# Uploads the given file using a managed uploader, which will split up large
# files automatically and upload parts in parallel.
#s3.upload_file(filename, bucket_name, "sss/999.jpg")