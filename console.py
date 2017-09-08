import sys


class Colors:
  Blue = '\033[94m';
  Green = '\033[92m';
  Yellow = '\033[93m';
  Red = '\033[91m';
  Reset = '\033[0m';
  
  def Result(boolean):
    return Colors.Green if boolean else Colors.Red


if sys.stdout.isatty():
  def Print(color, str, end = '\n', flush = False):
    print(color + str + Colors.Reset, end = end, flush = flush)
else:
  def Print(color, str, end = '\n', flush = False):
    print(str, end = end, flush = flush)
