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
    with pytest.raises(SystemExit):
        args = main.parser.parse_args(['detect'])

    args = main.parser.parse_args(['detect', 'roCreate.mos.xml'])
    assert args.files == ['roCreate.mos.xml']

    args = main.parser.parse_args(
        ['detect', 'roCreate.mos.xml', 'roDelete.mos.xml'])
    assert args.files == ['roCreate.mos.xml', 'roDelete.mos.xml']

def test_inspect():
    # TODO
    # with pytest.raises(SystemExit):
    #     args = main.parser.parse_args(['inspect'])

    args = main.parser.parse_args(['inspect', '-f', 'roCreate.mos.xml'])
    assert args.file == 'roCreate.mos.xml'

    args = main.parser.parse_args(['inspect', '--file', 'roCreate.mos.xml'])
    assert args.file == 'roCreate.mos.xml'

    with pytest.raises(SystemExit):
        args = main.parser.parse_args(
            ['inspect', '-f', 'roCreate.mos.xml', 'roDelete.mos.xml'])

    args = main.parser.parse_args(['inspect', '-f', 'roCreate.mos.xml'])
    assert args.file == 'roCreate.mos.xml'
    assert not args.bucket_name
    assert not args.prefix
    assert not args.key
    assert not args.start_time
    assert not args.duration
    assert not args.stories
    assert not args.items
    assert not args.notes

    args = main.parser.parse_args(
        ['inspect', '-b', 'bucket', '-p', 'prefix', '-k', 'key'])
    assert not args.file
    assert args.bucket_name == 'bucket'
    assert args.prefix == 'prefix'
    assert args.key == 'key'
    assert not args.start_time
    assert not args.duration
    assert not args.stories
    assert not args.items
    assert not args.notes

    args = main.parser.parse_args(
        ['inspect', '-f', 'roCreate.mos.xml', '-t', '-d', '-s', '-i', '-n'])
    assert args.file == 'roCreate.mos.xml'
    assert not args.bucket_name
    assert not args.prefix
    assert not args.key
    assert args.start_time
    assert args.duration
    assert args.stories
    assert args.items
    assert args.notes

    args = main.parser.parse_args(
        ['inspect', '-f', 'roCreate.mos.xml', '--start-time', '--end-time',
        '--duration', '--stories', '--items', '--notes'])
    assert args.file == 'roCreate.mos.xml'
    assert not args.bucket_name
    assert not args.prefix
    assert not args.key
    assert args.start_time
    assert args.duration
    assert args.stories
    assert args.items
    assert args.notes


def test_merge():
    # TODO
    # with pytest.raises(SystemExit):
    #     args = main.parser.parse_args(['merge'])

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
