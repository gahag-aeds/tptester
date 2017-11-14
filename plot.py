import matplotlib.pyplot as plt

from tptester.util import unique_filename


def plot_to_file(graph_title, graph_x, graph_y, data_x, data_y):
  filename = unique_filename('graph', '.svg')
  
  plt.title(graph_title)
  plt.xlabel(graph_x)
  plt.ylabel(graph_y)
  plt.plot(data_x, data_y)
  plt.savefig(filename)
  
  return filename
