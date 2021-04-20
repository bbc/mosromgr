# mosromgr: Python library for managing MOS running orders
# Copyright 2021 BBC
# SPDX-License-Identifier: Apache-2.0

from mosromgr.cli import main
import pytest


def test_args_incorrect():
    with pytest.raises(SystemExit):
        main(['--nonexistentarg'])

def test_help(capsys):
    with pytest.raises(SystemExit) as ex:
        main(['--help'])
    out, err = capsys.readouterr()
    assert "managing MOS running orders" in out

    with pytest.raises(SystemExit) as ex:
        main(['-h'])
    out, err = capsys.readouterr()
    assert "managing MOS running orders" in out

    with pytest.raises(SystemExit) as ex:
        main(['help'])
    out, err = capsys.readouterr()
    assert "managing MOS running orders" in out

def test_detect():
    args = main.parser.parse_args(['detect', '-f', 'roCreate.mos.xml'])
    assert args.files == ['roCreate.mos.xml']

    args = main.parser.parse_args(
        ['detect', '-f', 'roCreate.mos.xml', 'roDelete.mos.xml'])
    assert args.files == ['roCreate.mos.xml', 'roDelete.mos.xml']

def test_inspect():
    args = main.parser.parse_args(['inspect', '-f', 'roCreate.mos.xml'])
    assert args.files == ['roCreate.mos.xml']
    assert not args.bucket_name
    assert not args.key

    args = main.parser.parse_args(['inspect', '--file', 'roCreate.mos.xml'])
    assert args.files == ['roCreate.mos.xml']
    assert not args.bucket_name
    assert not args.key

    args = main.parser.parse_args(['inspect', '-b', 'bucket', '-k', 'key'])
    assert not args.files
    assert args.bucket_name == 'bucket'
    assert args.key == 'key'


def test_merge():
    args = main.parser.parse_args(['merge', '-f', 'roCreate.mos.xml'])
    assert args.files == ['roCreate.mos.xml']

    args = main.parser.parse_args(
        ['merge', '-f', 'roCreate.mos.xml', 'roDelete.mos.xml'])
    assert args.files == ['roCreate.mos.xml', 'roDelete.mos.xml']

    args = main.parser.parse_args(['merge', '--files', 'roCreate.mos.xml'])
    assert args.files == ['roCreate.mos.xml']

    args = main.parser.parse_args(
        ['merge', '--files', 'roCreate.mos.xml', 'roDelete.mos.xml'])
    assert args.files == ['roCreate.mos.xml', 'roDelete.mos.xml']

    args = main.parser.parse_args(
        ['merge', '-b', 'bucket', '-p', 'prefix'])
    assert not args.files
    assert args.bucket_name == 'bucket'
    assert args.prefix == 'prefix'
    assert not args.outfile
    assert not args.incomplete

    args = main.parser.parse_args(
        ['merge', '-f', 'roCreate.mos.xml', 'roDelete.mos.xml', '-o', 'outfile',
        '-i'])
    assert args.files == ['roCreate.mos.xml', 'roDelete.mos.xml']
    assert args.bucket_name is None
    assert args.prefix is None
    assert args.outfile == 'outfile'
    assert args.incomplete

    args = main.parser.parse_args(
        ['merge', '-f', 'roCreate.mos.xml', 'roDelete.mos.xml', '--outfile',
        'outfile', '--incomplete'])
    assert args.files == ['roCreate.mos.xml', 'roDelete.mos.xml']
    assert args.bucket_name is None
    assert args.prefix is None
    assert args.outfile == 'outfile'
    assert args.incomplete
