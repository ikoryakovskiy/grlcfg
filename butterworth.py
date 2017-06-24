"""Butterworth filter using Tustin method."""

from math import pi, sqrt
from scipy.signal import butter, lfilter

def bw_tustin(signal, order = 2, cutoff = 5.0, fs = 30.0):
  
  T = 2.0*pi*cutoff/fs;

  if order == 1:
    normalizeOutput = T + 2.0;
    A = [1.0, (T - 2.0)/normalizeOutput]
    B = [T/normalizeOutput, T/normalizeOutput]
  elif order == 2:
    normalizeOutput = T*T + 2.0*sqrt(2.0)*T + 4.0;
    A = [ 1.0, (2.0*T*T                   - 8.0)/normalizeOutput, (    T*T - 2.0*sqrt(2.0)*T + 4.0)/normalizeOutput ]
    B = [T*T/normalizeOutput, 2.0*T*T/normalizeOutput, T*T/normalizeOutput]
  elif order == 3:
    normalizeOutput = T*T*T + 4.0*T*T + 8.0*T + 8.0;
    A = [ 1.0, (3.0*T*T*T + 4.0*T*T - 8.0*T - 24.0)/normalizeOutput, (3.0*T*T*T - 4.0*T*T - 8.0*T + 24.0)/normalizeOutput, (    T*T*T - 4.0*T*T + 8.0*T -  8.0)/normalizeOutput ]
    B = [T*T*T/normalizeOutput, 3*T*T*T/normalizeOutput, 3*T*T*T/normalizeOutput, T*T*T/normalizeOutput]

  filtered_signal = lfilter(B, A, signal, axis=0)
  return filtered_signal

if __name__ == "__main__":
    main()


