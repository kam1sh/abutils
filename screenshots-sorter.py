#!/usr/bin/env python3
"""
Utility for sorting screenshots captured by MSI Afterburner.
"""
import os
from pathlib import Path
import logging
import collections
import argparse
import re
from datetime import datetime

# DOOMx64_2016_05_17_14_21_03_678.jpg
# -> [DOOMx64, 2016_05_17_14_21_03_678]
PATTERN = re.compile(r'([^_]+)_([^.]+)')


parser = argparse.ArgumentParser(description='Screenshots sorter')
parser.add_argument(
	'dir', nargs='?',
	default=Path.home() / 'Pictures' / 'screen', # default for myself
	help='Directory with screenshots')
parser.add_argument('--log-level', default='info', help='Logging level')


def ispic(path: Path) -> bool:
	"""
	Checks if file belongs to picture by his filename.
	"""
	# path.suffix -> '.jpg'
	# path.suffix[1:] -> 'jpg
	return path.suffix[1:].upper() in {'PNG', 'JPG', 'GIF', 'JPEG', 'BMP'}

def sort_screenshots(directory: Path, destination: Path = None) -> dict:
	"""
	Sorts screenshots in the folder by game name and date.
	By default destination for folders is the same folder.
	returns dictionary with screenshots count like {'doom': 150}
	"""
	games = collections.defaultdict(lambda: 0)
	destination = destination or directory

	for pic in directory.iterdir():
		name = pic.name
		if not pic.is_file() or not ispic(pic):
			logging.info('%s is not file or pic, skipping', name)
			continue
		parsed = PATTERN.search(name)
		if parsed is None:
			logging.warn('Could not parse file name: %s', name)
			continue
		logging.debug('groups: %s', parsed.groups())
		game = parsed.group(1)
		dt = datetime(*map(int, parsed.group(2).split('_')))
		games[game] += 1

		game_dir = directory / game / str(dt.year)
		game_dir.mkdir(parents=True, exist_ok=True)
		dst = game_dir / name

		logging.info('Moving %s to %s', name, game_dir)
		pic.rename(dst)
	return games

if __name__ == '__main__':
	args = parser.parse_args()
	logging.basicConfig(level=getattr(logging, args.log_level.upper()))
	games = sort_screenshots(args.dir)
	for game, count in games.items():
		logging.info('%s screenshots count: %s', game, count)
	logging.info('Done!')
