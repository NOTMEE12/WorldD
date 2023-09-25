import sys
import os
try:
	import colorama
	MAGENTA = colorama.Fore.MAGENTA
	RESET = colorama.Fore.RESET
	YELLOW = colorama.Fore.YELLOW
except ModuleNotFoundError:
	MAGENTA = ''
	RESET = ''
	YELLOW = ''

if len(sys.argv) <= 1:
	print('examples: ')
	scripts = {
		'1': 'visualizer',
		'2': 'visualizer-with-offset',
		'3': 'visualizer-with-collisions'
	}
	for id, name in scripts.items():
		print(f'{YELLOW}{id}{RESET} - {MAGENTA}{name}{RESET}')
	name = input("run: ")
	print(YELLOW + '=' * 32 + RESET)
	os.system(f'python {name if name not in scripts else scripts[name]}.py')
else:
	os.system(f'python {sys.argv[1]}.py')
