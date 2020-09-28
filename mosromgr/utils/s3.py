import boto3


s3r = boto3.resource('s3')
s3c = boto3.client('s3')


def get_mos_files(bucket_name, prefix, suffix='.mos.xml'):
    """
    Retrieve MOS files from given S3 bucket in location defined by *prefix*.
    Returns a list of file keys.
    """
    paginator = s3c.get_paginator('list_objects')
    files = []
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        try:
            contents = page['Contents']
        except KeyError:
            break

        for file in contents:
            key = file['Key']
            if key.endswith(suffix):
                files.append(key)
    return files


def get_file_contents(bucket_name, mos_file_key):
    "Open the S3 file and return its contents as a string."
    o = s3r.Object(bucket_name, mos_file_key).get()
    b = o['Body']
    return b.read()
