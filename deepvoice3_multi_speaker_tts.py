# -*- coding: utf-8 -*-
"""DeepVoice3 multi-speaker TTS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fmcd4fhQ5r_m1oEzEN_rxr_xWrIp92ch

# DeepVoice3: Multi-speaker text-to-speech demo

In this notebook, you can try DeepVoice3-based multi-speaker text-to-speech (en) using a model trained on [VCTK dataset](http://homepages.inf.ed.ac.uk/jyamagis/page3/page58/page58.html). The notebook is supposed to be executed on [Google colab](https://colab.research.google.com) so you don't have to setup your machines locally.

## Setup

### Install dependencies
"""



import torch
import numpy as np
import librosa
import librosa.display
import IPython
from IPython.display import Audio
# need this for English text processing frontend
import nltk


"""### Downloading a pre-trained model"""

# checkpoint_path = "20171222_deepvoice3_vctk108_checkpoint_step000300000.pth"

# """### git checkout to the working commit"""

# # Copy preset file (json) from master
# # The preset file describes hyper parameters
# ! git checkout master --quiet
# preset = "./presets/deepvoice3_vctk.json"
# ! cp -v $preset .
# preset = "./deepvoice3_vctk.json"

# # And then git checkout to the working commit
# # This is due to the model was trained a few months ago and it's not compatible
# # with the current master. 
# ! git checkout 0421749 --quiet
# ! pip install -q -e '.[train]'

"""## Synthesis

### Setup hyper parameters
"""

import hparams
import json

# Newly added params. Need to inject dummy values
for dummy, v in [("fmin", 0), ("fmax", 0), ("rescaling", False),
                 ("rescaling_max", 0.999), 
                 ("allow_clipping_in_normalization", False)]:
  if hparams.hparams.get(dummy) is None:
    hparams.hparams.add_hparam(dummy, v)
    
# Load parameters from preset
with open(preset) as f:
  hparams.hparams.parse_json(f.read())

# Tell we are using multi-speaker DeepVoice3
hparams.hparams.builder = "deepvoice3_multispeaker"
  
# Inject frontend text processor
import synthesis
import train
from deepvoice3_pytorch import frontend
synthesis._frontend = getattr(frontend, "en")
train._frontend =  getattr(frontend, "en")

# alises
fs = hparams.hparams.sample_rate
hop_length = hparams.hparams.hop_size

"""### Define utility functions"""

def tts(model, text, p=0, speaker_id=0, fast=True, figures=True):
  from synthesis import tts as _tts
  waveform, alignment, spectrogram, mel = _tts(model, text, p, speaker_id, fast)
  if figures:
      visualize(alignment, spectrogram)
  IPython.display.display(Audio(waveform, rate=fs))
  
  return mel
  
def visualize(alignment, spectrogram):
  label_fontsize = 16
  figure(figsize=(16,16))

  subplot(2,1,1)
  imshow(alignment.T, aspect="auto", origin="lower", interpolation=None)
  xlabel("Decoder timestamp", fontsize=label_fontsize)
  ylabel("Encoder timestamp", fontsize=label_fontsize)
  colorbar()

  subplot(2,1,2)
  librosa.display.specshow(spectrogram.T, sr=fs, 
                           hop_length=hop_length, x_axis="time", y_axis="linear")
  xlabel("Time", fontsize=label_fontsize)
  ylabel("Hz", fontsize=label_fontsize)
  tight_layout()
  colorbar()

def extract_features(audio,sample_rate):
    
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    mfccsscaled = np.mean(mfccs.T,axis=0)
     
    return mfccs

"""### Load the model checkpoint"""

from train import build_model
from train import restore_parts, load_checkpoint

model = build_model()
model = load_checkpoint(checkpoint_path, model, None, True)

"""### Generate speech"""

# Try your favorite sentences:)
text = "Some have accepted this as a miracle without any physical explanation"
N = 10
features = []
print("Synthesizing \"{}\" with {} different speakers".format(text, N))
for speaker_id in range(N):
  print(speaker_id)
  print(type(tts(model, text, speaker_id=speaker_id, figures=False)))

# With attention plot
tts(model, text, speaker_id=3, figures=True)