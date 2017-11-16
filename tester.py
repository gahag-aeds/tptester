import io
import resource
import subprocess

from tptester.console import Colors, Print
from tptester.util import compare_streams
from tptester.plot import plot_to_file


# tp_test:
#  indexes: list of numerical indexes for the tests.
#
#  program_name: name of the executable to test.
#  input_file: index -> input file name.
#  answer_file: index -> answer file name, or None.
#
#  valgrind: boolean to use valgrind or not.
#  
#  graph: whether to plot the graph of the run time.
#  graph_title: title of the plot.
#  graph_x: x axis title.
#  graph_y: y axis title.
#
#  args: index -> list of command line arguments.
#  stdin: input file -> stream.
#  output: index -> stdout stream -> stream.
def tp_test(
  indexes,
  
  program_name,
  input_file,
  answer_file = lambda ix: None,
  
  valgrind = False,
  
  graph = False,
  graph_title = "Tempo de execução",
  graph_x = "N",
  graph_y = "Tempo (s)",
  
  args = lambda ix: [],
  stdin = lambda ifile: ifile,
  output = lambda ix, stdout: stdout,
):
  Print(Colors.Yellow, "Running tests for " + program_name)
  print()
  
  passed_count = 0
  
  if graph:
    times = []
  
  for ix in indexes:
    try:
      ifile_name = input_file(ix)
      ifile = open(ifile_name, 'rb') if ifile_name is not None else None
      
      afile_name = answer_file(ix)
      afile = open(afile_name, 'rb') if afile_name is not None else None
      
      passed, time = _run_test(
        ix,
        ifile_name,
        
        program_name,
        afile,
        
        valgrind,
        
        args(ix),
        stdin(ifile),
        output,
      )
      
      if graph:
        times.append(time)
      
      if passed:
        passed_count += 1
      
      if ifile is not None:
        ifile.close()
      
      if afile is not None:
        afile.close()
        
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
  
  
  if graph:
    Print(Colors.Blue, "Graph saved to file ", end = '')
    print(plot_to_file(graph_title, graph_x, graph_y, indexes, times))



# _run_test:
#  ix: index of the test.
#
#  program_name: name of the executable to test.
#  answer_file: answer stream, or None.
#
#  valgrind: boolean to use valgrind or not.
#  
#  args: list of command line arguments.
#  stdin: stream.
#  output: index -> stdout stream -> stream.
#
#  returns passed, time:
#  passed: boolean indicating whether the program passed the test.
#  time: the user time the program took to complete the test.
def _run_test(
  ix,
  ifile_name,
  
  program_name,
  afile,
  
  valgrind,
  
  args,
  stdin,
  output,
):
  Print(Colors.Blue, "Test #" + str(ix), end = '')
  print(" " + ifile_name)
  print(
    ("Executing " if not valgrind else "Valgrinding ") + program_name + ": ",
    end = '',
    flush = True
  )
  
  
  usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
  
  
  try:
    command_line = [program_name] + args
    program = subprocess.run(
      [ "/usr/bin/valgrind" ] + command_line if valgrind else command_line,
      stdin = stdin,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )
  except (subprocess.SubprocessError):
    Print(Colors.Red, "Error: failed to execute.")
    return False, -1
  
  
  usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
  
  Print(Colors.Result(program.returncode == 0), str(program.returncode))
  
  cpu_user = usage_after.ru_utime - usage_before.ru_utime
  cpu_sys = usage_after.ru_stime - usage_before.ru_stime
  
  print("User time: {0:.3f}s".format(cpu_user))
  print("System time: {0:.3f}s".format(cpu_sys))
  
  
  if (program.stderr):
    if valgrind:
      _color = Colors.Yellow
      _name = "valgrind"
    else:
      _color = Colors.Red
      _name = "stderr"
    
    Print(_color, _name + " {")
    print(program.stderr.decode('utf8'), end = '')
    Print(_color, "}")
  
  
  if afile is not None:
    with output(ix, io.BytesIO(program.stdout)) as out:
      output_match = compare_streams(afile, out)
    
    Print(
      Colors.Result(output_match),
      "Output matched!" if output_match else "Output differed!"
    )
    
    passed = output_match and program.returncode == 0
    
    Print(Colors.Result(passed), "Passed!" if passed else "Failed!")
    
    return passed, cpu_user
  
  
  return True, cpu_user;
