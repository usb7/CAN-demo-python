#!/usr/bin/env python3
# cython: language_level=3, always_allow_keywords=True
# vim:fileencoding=utf-8
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import os
from pprint import pprint

import can
import cantools

if __name__ == '__main__':
	import argparse
	desc = f'''
Example:
  {sys.argv[0]} --bus can0 --dbc ./Model3CAN.dbc
'''

	args_bus = 'can0'
	args_dbc = ''

	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('--bus', nargs = 1, help = f"can bus name. default: {args_bus}")
	parser.add_argument('--dbc', nargs = 1, help = "dbc file")
	if len(sys.argv) < 2:
		parser.print_help(sys.stderr)
		sys.exit(1)
	args = parser.parse_args()

	if args.bus:
		args_bus = args.bus[0]

	if not args.dbc:
		sys.exit("Error: no dbc file specified")
	else:
		if not os.path.exists(args.dbc[0]):
			sys.exit(f"Error: {args.dbc[0]} not exists")
		args_dbc = args.dbc[0]

	can_db = cantools.database.load_file(args_dbc)
	can_bus = can.interface.Bus(args_bus, interface='socketcan')
	print("Info: ready to receive", file=sys.stderr)

	while True:
		can_message = can_bus.recv()
		pprint(can_db.decode_message(can_message.arbitration_id, can_message.data))
		print("")