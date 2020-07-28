# This file is (C) 2020 by the Computational Memory Lab
#
# Permission is hereby granted, free of charge, to any person or organization
# obtaining a copy of this CMLLoad class (the "Software") to deal in the
# Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


import os
import h5py
import numpy as np
import pandas as pd

class CMLLoad():
  '''Index():        Returns a Pandas DataFrame of all available sessions.
     LoadEEG(...):   Returns a tuple of eegdata, samplingrate, channels.
     LoadPTSA(...):  Returns a PTSA TimeSeries object with eeg data.
     LoadMNE(...):   Returns an MNE object with eeg data.
     Load(...):      Returns other data such as channels and events.'''
  def __init__(self, data_dir, strict=False):
    '''data_dir: the pathname of the exported data directory
       strict=True enables some data validation exceptions'''
    self.data_dir = data_dir
    self.strict = strict

  def _GetStrict(self, strict):
    if strict is not None:
      return strict
    return self.strict

  def _GetLabel(self, dr):
    return f'{dr["subject"]} {dr["experiment"]} {dr["session"]}'

  def Index(self):
    '''Returns a Pandas DataFrame of all available sessions'''
    return pd.read_json(os.path.join(self.data_dir, 'index.json'))

  def DFRtoDict(self, df_row):
    '''Convenience function for turning a DataFrame row into a dict.'''
    try:  # Check if dict-like
      dr = dict(df_row)
    except Exception as e:
      try:
        dr = df_row._asdict() # Try for pandas.core.frame.Pandas
      except AttributeError:
        dr = df_row.to_dict() # Try for pandas.core.series.Series
    return dr

  def GetFilename(self, dr, key):
    '''dr: A dictionary corresponding to a DataFrame row.
       Returns the data file corresponding to a given key.'''
    return os.path.join(self.data_dir, dr[key+'_file'])

  def LoadEEG(self, df_row, ev_start=0, ev_len=None, buf=None, strict=None):
    '''df_row: A selected DataFrame row.
       ev_start: The relative offset for starting each event in milliseconds.
       ev_len: The length to make of each event in milliseconds.
         dividing the eeg into time around event boundaries.
       buf: Extra time in millieconds to add to both ends of each event.
       strict: A bool enabling ArithmeticError for nans.
       Returns a 3 element tuple of:
         (numpy array [events, channels, time], samplingrate, channels).'''
    dr = self.DFRtoDict(df_row)
    strict = self._GetStrict(strict)
    pathname = self.GetFilename(dr, 'eeg')

    try:
      with h5py.File(pathname, 'r') as fr:
        sr = fr['data'].attrs['samplerate']
        data = fr['data'][()]
    except OSError as e:
      raise FileNotFoundError(str(e))

    channels = self.Load(dr, 'channels')

    buf_trim = 0
    if ev_len is not None:
      if buf is not None:
        ev_start -= buf
        ev_len += 2*buf
        buf_trim = int(round(buf*sr/1000.))

      self.events = self.Load(dr, 'events')
      samp_start = int(round(ev_start*sr/1000.))
      samp_len = int(round(ev_len*sr/1000.))
      samp_end = samp_start + samp_len
      if samp_len <= 2*buf_trim:
        raise ValueError('ev_len yields 0 or fewer samples')
      evarr = np.full((len(self.events), data.shape[1], samp_len), np.nan)
      for i,ev in enumerate(self.events.itertuples()):
        st = ev.eegoffset + samp_start
        en = ev.eegoffset + samp_end
        if st >= 0 and en <= data.shape[2]:
          evarr[i] = data[0, :, st:en]
      data = evarr
  
    if strict:
      if np.any(np.isnan(data)):
        raise ArithmeticError('nans in eeg data for '+self._GetLabel(dr))

    return data, sr, channels

  def LoadPTSA(self, df_row, ev_start=0, ev_len=None, buf=None, strict=None):
    '''df_row: A selected DataFrame row.
       ev_start: The relative offset for starting each event in milliseconds.
       ev_len: The length to make of each event in milliseconds.
         dividing the eeg into time around event boundaries.
       buf: Extra time in millieconds to add to both ends of each event.
       strict: Is a bool enabling ArithmeticError for nans.
       Returns a PTSA TimeSeries object.'''
    from ptsa.data.timeseries import TimeSeries
    data, sr, channels = self.LoadEEG(df_row, ev_start, ev_len, buf, strict)
    if ev_len is None:
      st = 0
    else:
      st = ev_start
      if buf is not None:
        st -= buf
    en = st + (data.shape[-1]-1)*1000./sr
    time = np.linspace(st, en, data.shape[-1])

    coords = {'channel':[str(c) for c in channels.label], 'time':time}
    if ev_len is not None:
      coords['event'] = \
          [{k:v for k,v in r._asdict().items()}
            for r in self.events.itertuples()]
    return TimeSeries.create(data, sr, coords=coords,
        dims=('event', 'channel', 'time'))

  def LoadMNE(self, df_row, ev_start=0, ev_len=None, buf=None, strict=None):
    '''df_row: A selected DataFrameRow.
       ev_start: The relative offset for starting each event in milliseconds.
       ev_len: The length to make of each event in milliseconds.
         dividing the eeg into time around event boundaries.
       buf: Extra time in millieconds to add to both ends of each event.
       strict: A bool enabling ArithmeticError for nans.
       Returns an MNE RawArray (no events) or EpochsArray (events).'''
    import mne
    data, sr, channels = self.LoadEEG(df_row, ev_start, ev_len, buf, strict)
    info = mne.create_info([str(c) for c in channels.label], sr,
        ch_types='eeg')

    if ev_len is None:
      return mne.io.RawArray(data[0], info, first_samp=0)
    else:
      if buf is not None:
        ev_start -= buf
      return mne.EpochsArray(data, info, tmin=ev_start / 1000.)

  def Load(self, df_row, key):
    '''df_row: A selected DataFrame row.
       key: Any tabular data available such as 'events' or 'channels'.
       Returns a Pandas DataFrame of the selected key type.'''
    dr = self.DFRtoDict(df_row)
    pathname = self.GetFilename(dr, key)

    return pd.read_csv(pathname)

