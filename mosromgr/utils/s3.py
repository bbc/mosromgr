# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, List

import boto3


class S3:
    """
    Class to defer initialising S3 resources until needed
    """
    def __init__(self):
        self._resource = None
        self._client = None

    @property
    def resource(self):
        if self._resource is None:
            self._resource = boto3.resource('s3')
        return self._resource

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('s3')
        return self._client


def get_mos_files(
        bucket_name: str,
        prefix: Optional[str] = None,
        *,
        suffix: str = '.mos.xml'
    ) -> List[str]:
    """
    Retrieve MOS files from given S3 bucket in location defined by *prefix*.
    Returns a list of file keys.
    """
    if prefix is None:
        prefix = ''
    paginator = s3.client.get_paginator('list_objects')
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


def get_file_contents(bucket_name, file_key):
    """
    Open the S3 file and return its contents as a string
    """
    o = s3.resource.Object(bucket_name, file_key).get()
    b = o['Body']
    return b.read()


s3 = S3()