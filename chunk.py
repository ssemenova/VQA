import gc
import os
import sys
import tensorflow as tf
from PIL import Image
import logging

from feature_extractors import ChunkC3DExtractor, ChunkVGGExtractor, ChunkI3DExtractor


class Chunk(object):
  def __init__(
          self, id, chunk_size, 
          frames_per_clip, clip_num,
          i3d_extractor_model_path
    ):
    self.id = id

    self.i3d_extractor_model_path = i3d_extractor_model_path

    # Feature extraction constants
    self.chunk_size = chunk_size
    self.frames_per_clip = frames_per_clip
    self.clip_num = clip_num

    # Computed vgg and c3d features 
    self.vgg_features = list()
    self.c3d_features = list()
    self.i3d_features = list()

    # Image frames of all images in this video chunk
    self.image_frames = list()

  def add_frame(self, frame, frame_count):
    self.image_frames.append(Image.fromarray(frame))

  def generate_features(self):
    logging.debug("Creating chunk #" + str(self.id))

    sess_config = tf.ConfigProto()
    sess_config.gpu_options.allow_growth = True
    sess_config.gpu_options.visible_device_list = '0'
    
    logging.debug("C3D extractor...")
    with tf.Graph().as_default(), tf.Session(config=sess_config) as sess:
      c3d_extractor = ChunkC3DExtractor(
        self.clip_num, sess, self.frames_per_clip, self.chunk_size
      )
      self.c3d_features = c3d_extractor.extract(self.image_frames)
    
    logging.debug("VGG extractor...")
    with tf.Graph().as_default(), tf.Session(config=sess_config) as sess:
      vgg_extractor = ChunkVGGExtractor(
        self.clip_num, sess, self.chunk_size
      )
      self.vgg_features = vgg_extractor.extract(self.image_frames)

    #Not currently implemented.
    #print("I3D extractor...")
    #i3d_extractor = ChunkI3DExtractor(self.i3d_extractor_model_path)
    #self.i3d_features = i3d_extractor.extract(self.image_frames)

    del self.image_frames
    gc.collect()
