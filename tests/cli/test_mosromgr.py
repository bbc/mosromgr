from mosromgr.cli.mosromgr import main
import pytest


def test_args_incorrect():
    with pytest.raises(SystemExit) as ex:
        main(['mosromgr', '--nonexistentarg'])

def test_args_directory():
    args = main.parser.parse_args(['-d', 'somedir1'])
    assert args.directory == 'somedir1'
    args = main.parser.parse_args(['--directory', 'somedir2'])
    assert args.directory == 'somedir2'

def test_args_aws_s3():
    args = main.parser.parse_args(['-b', 'my_bucket'])
    assert args.bucket_name == 'my_bucket'
    args = main.parser.parse_args(['--bucketname', 'my_bucket'])
    assert args.bucket_name == 'my_bucket'
    args = main.parser.parse_args(['-p', 'my_prefix'])
    assert args.bucket_prefix == 'my_prefix'
    args = main.parser.parse_args(['--prefix', 'my_prefix'])
    assert args.bucket_prefix == 'my_prefix'
