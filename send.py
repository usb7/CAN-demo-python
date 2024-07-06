#!/usr/bin/env python3
# cython: language_level=3, always_allow_keywords=True
# vim:fileencoding=utf-8
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import os
import re
import time

from ast import literal_eval

import can
import cantools


if __name__ == '__main__':
	import argparse
	desc = f'''
Example:
  {sys.argv[0]} --bus can0 --dbc ./Model3CAN.dbc --signal VCFRONT_turnSignalLeftStatus --value 1 --cycles 100
'''

	args_bus = 'can0'
	args_dbc = ''
	args_signal = ''
	args_value = 0
	args_cycles = 1

	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('--bus', nargs = 1, help = f"can bus name. default: {args_bus}")
	parser.add_argument('--dbc', nargs = 1, help = "dbc file")
	parser.add_argument('--signal', nargs = 1, help = "signal name")
	parser.add_argument('--value', nargs = 1, help = "signal value, hex(0xHH) or int")
	parser.add_argument('--cycles', nargs = 1, help = f"singal send cycles. default: {args_cycles}")
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

	if not args.signal:
		sys.exit("Error: no signal specified")
	else:
		args_signal = args.signal[0]

	if not args.value:
		sys.exit("Error: no signal value specified")
	else:
		args_value = literal_eval(args.value[0])

	if args.cycles:
		if(not re.match(r'[1-9][0-9]*', args.cycles[0])):
			sys.exit("Error: invalid test cycles value: "+args.cycles[0])
		args_cycles = int(args.cycles[0])

	can_db = cantools.database.load_file(args_dbc)

	can_message_name = ''
	for can_msg in can_db.messages:
		for can_sig in can_msg.signals:
			if can_sig.name == args_signal:
				can_message_name = can_msg.name
				break

	if not can_message_name:
		sys.exit("Error: no signal '{signal}' specified in dbc")

	can_msg = can_db.get_message_by_name(can_message_name)
	can_sig = can_msg.get_signal_by_name(args_signal)
	assert(can_sig.minimum <= args_value <= can_sig.maximum)

	can_sig_default = {}
	for can_sig in can_msg.signals:
		can_sig_default[can_sig.name] = can_sig.minimum

	can_sig_default[args_signal] = args_value
	data = can_db.encode_message(can_message_name, can_sig_default)
	# NOTE: without is_extended_id=False, arbitration_id=0x200 will become arbitration_id=0x80000200
	data = can.Message(arbitration_id=can_msg.frame_id, data=data, is_extended_id=False)

	can_bus = can.interface.Bus(args_bus, interface='socketcan')

	while args_cycles > 0:
		can_bus.send(data)
		# NOTE: if we don't sleep and send with --cycles 1000, the socketcan peer's recvbuf will be full, and pkg is dropped
		time.sleep(1)
		args_cycles -= 1

	# suppress ab-normal close warning
	can_bus.shutdown()

