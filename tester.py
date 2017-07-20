import resource
import subprocess

from tptester.console import Colors, Print
from tptester.util import compare_streams


# Input:
#  program name
#
#  args provider : index -> string list
#  stdin provider : input file -> stream
#  output provider : index -> stdout stream -> stream
#
#  indexes : string list
#  input file provider : index -> input file name
#  answer file provider : index -> answer file name
def tp_test(
  program_name,
  args,
  stdin,
  output,
  indexes,
  input_file,
  answer_file
):
  Print(Colors.Yellow, "Running tests for " + program_name)
  print()
  
  passed_count = 0
  
  for ix in indexes:
    try:
      with open(input_file(ix), 'rb') as ifile, \
           open(answer_file(ix), 'rb') as afile:
        
        passed = _run_test(
          ix,
          program_name,
          args = args(ix),
          stdin = stdin(ifile),
          output = output,
          afile = afile
        )
        
        if passed: passed_count += 1
        
    except (FileNotFoundError, PermissionError) as err:
      Print(Colors.Red, "Failed to open file " + err.filename)
    
    print()
      
  Print(Colors.Yellow, "Summary:")
  
  total = len(indexes)
  
  if passed_count == total:
    Print(Colors.Green, "All passed!")
  else:
    Print(Colors.Green, str(passed_count) + " passed")
    Print(Colors.Red, str(total - passed_count) + " failed")


def _run_test(ix, program_name, args, stdin, output, afile):
  Print(Colors.Blue, "Test #" + str(ix))
  print("Executing " + program_name + ": ", end = '', flush = True)
  
  usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
  
  try:
    program = subprocess.run(
      [program_name] + args,
      stdin = stdin,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )
  except (subprocess.SubprocessError):
    Print(Colors.Red, "Error: failed to execute.")
    return False
  
  usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
  
  Print(Colors.Result(program.returncode == 0), str(program.returncode))
  
  cpu_user = usage_after.ru_utime - usage_before.ru_utime
  cpu_sys = usage_after.ru_stime - usage_before.ru_stime
  
  print("User time: {0:.3f}s".format(cpu_user))
  print("System time: {0:.3f}s".format(cpu_sys))
  
  if (program.stderr):
    Print(Colors.Red, "stderr {")
    print(program.stderr.decode('utf8'))
    Print(Colors.Red, "}")
  
  with output(ix, program.stdout) as out:
    output_match = compare_streams(afile, out)
  
  Print(
    Colors.Result(output_match),
    "Output matched!" if output_match else "Output differed!"
  )
  
  passed = output_match and program.returncode == 0
  
  Print(Colors.Result(passed), "Passed!" if passed else "Failed!")
  
  return passed
