def ClusterRun(function, parameter_list, max_cores=100):
  '''function: The routine run in parallel, which must contain all necessary
     imports internally.
  
     parameter_list: should be an iterable of elements, for which each element
     will be passed as the parameter to function for each parallel execution.
     
     max_cores: Standard Rhino cluster etiquette is to stay within 100 cores
     at a time.  Please ask for permission before using more.
     
     In JupyterLab, the number of engines reported as initially running may
     be smaller than the number actually running.  Check usage from an ssh
     terminal using:  qstat -f | egrep "$USER|node" | less
     
     Undesired running jobs can be killed by reading the JOBID at the left
     of that qstat command, then doing:  qdel JOBID
  '''
  import cluster_helper.cluster
  from pathlib import Path

  num_cores = len(parameter_list)
  num_cores = min(num_cores, max_cores)

  myhomedir = str(Path.home())

  # scheduler, queue, and extra_params will need adjusting if using this on
  # a cluster other than Rhino.
  with cluster_helper.cluster.cluster_view(scheduler="sge", queue="RAM.q",
      num_jobs=num_cores, cores_per_job=1,
      extra_params={'resources':'pename=python-round-robin'},
      profile=myhomedir + '/.ipython/') as view:
    # 'map' applies a function to each value within an interable.
    res = view.map(function, parameter_list)
      
  return res


def ClusterChecked(function, parameter_list, *args, **kwargs):
  '''Calls ClusterRun, then if any results return False it prints out which
     parameters triggered a failure, and raises an exception which can,
     for example, halt further JupyterLab execution.  To use this, design
     your called function to return True for success and False for failure.
  '''
  res = ClusterRun(function, parameter_list, *args, **kwargs)
  if all(res):
    print('All', len(res), 'jobs successful.')
  else:
    failed = sum([not bool(b) for b in res])
    if failed == len(res):
      raise RuntimeError('All '+str(failed)+' jobs failed!')
    else:
      print('Error on job parameters:\n  ' +
          '\n  '.join(str(parameter_list[i]) for i in range(len(res))
            if not bool(res[i])))
      raise RuntimeError(str(failed)+' of '+str(len(res))+' jobs failed!')


class Settings():
  '''settings = Settings()
     settings.somelist = [1, 2, 3]
     settings.importantstring = 'saveme'
     settings.Save()

     settings = Settings.Load()
  '''
  def __init__(self, **kwargs):
    for k,v in kwargs.items():
      self.__dict__[k] = v

  def Save(self, filename='settings.pkl'):
    import pickle
    with open(filename, 'wb') as fw:
      fw.write(pickle.dumps(self))

  def Load(filename='settings.pkl'):
    import pickle
    return pickle.load(open(filename, 'rb'))

  def __repr__(self):
    return ('Settings(' +
      ', '.join(str(k)+'='+repr(v) for k,v in self.__dict__.items()) +
      ')')

  def __str__(self):
    return '\n'.join(str(k)+': '+str(v) for k,v in self.__dict__.items())


def LogErr(*args, sep=', ', logfile='logfile.txt', suffix='', **kwargs):
  '''Error logging function suitable for single process or parallel use.
     All parameters other than ones specified below are formatted with a
     preceding date/time stamp, and then printed to output as well as
     appended to the logfile.  Extra named parameters are printed along
     with their names as labels.  Any exceptions passed in are formatted
     on the main output line, and then the traceback is appended in
     subsequent lines to the output.
     sep: The separator between printable outputs (default: ', ').
     logfile: The starting filename for the output log file
              (default: 'logfile.txt').
     suffix: For example, with logfile='logfile.txt', makes the new
             logfile be 'logfile_'+str(suffix)+'.txt'.  Use this to label
             log files by parameter.'''
  import datetime
  import traceback
  import os

  arglist = []
  exclist = []
  for a in args:
    if isinstance(a, BaseException):
      arglist.append(traceback.format_exception_only(type(a), a)[0].strip())
      exclist.append(a)
    else:
      arglist.append(a)

  s = datetime.datetime.now().strftime('%F_%H-%M-%S') + ': '
  s += sep.join(str(a) for a in arglist)
  if arglist:
    s += sep
  s += sep.join(str(k)+'='+str(v) for k,v in kwargs.items())
  for e in exclist:
    s += '\n' + \
        ''.join(traceback.format_exception(type(e), e, e.__traceback__))

  logfile,ext = os.path.splitext(logfile)
  suffix = str(suffix)
  if suffix:
    logfile += '_'+suffix
  logfile += ext

  with open(logfile, 'a') as fw:
    print(s)
    fw.write(s+'\n')


def DFRLabel(df_row):
  '''Given a DataFrame row with 'subject', 'experiment', and 'session'
     column labels, provide a formatted output string identifying these.'''
  try:  # Check if dict-like
    dr = dict(df_row)
  except Exception as e:
    try:
      dr = df_row._asdict() # Try for pandas.core.frame.Pandas
    except AttributeError:
      dr = df_row.to_dict() # Try for pandas.core.series.Series
  return 'Sub=' + str(dr['subject']) + ', Exp=' + str(dr['experiment']) + \
      ', Sess=' + str(dr['session'])

