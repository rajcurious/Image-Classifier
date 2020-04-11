from sklearn.metrics.pairwise import cosine_similarity #very useful metrics to find the cosone distance between thr two vectors
#%tensorflow_version 2.x
import tensorflow as tf
from tensorflow.keras.applications.inception_v3 import InceptionV3
import numpy as np
from tensorflow.keras.preprocessing.image import array_to_img,load_img,img_to_array
import imghdr

def vgg_layers(layer_names):
    """ Creates a vgg model that returns a list of intermediate output values."""
    # Load our model. Load pretrained VGG, trained on imagenet data
    vgg = tf.keras.applications.VGG19(include_top=False, weights='imagenet')
    vgg.trainable = False

    outputs = [vgg.get_layer(name).output for name in layer_names]

    model = tf.keras.Model([vgg.input], outputs)
    return model

#for painting identification
# Content layer where will pull our feature maps
content_layers = ['block5_conv2']

# Style layer of interest
style_layers = ['block2_conv1',
                'block3_conv1']
#'block3_conv1',
#'block4_conv1',
#'block5_conv1']

num_content_layers = len(content_layers)
num_style_layers = len(style_layers)


def gram_matrix(input_tensor):
  result = tf.linalg.einsum('bijc,bijd->bcd', input_tensor, input_tensor)
  input_shape = tf.shape(input_tensor)
  num_locations = tf.cast(input_shape[1]*input_shape[2], tf.float32)
  return result/(num_locations)


class StyleContentModel(tf.keras.models.Model):
    def __init__(self, style_layers, content_layers):
        super(StyleContentModel, self).__init__()
        self.vgg = vgg_layers(style_layers + content_layers)
        self.style_layers = style_layers
        self.content_layers = content_layers
        self.num_style_layers = len(style_layers)
        self.vgg.trainable = False

    def call(self, inputs):
        "Expects float input in [0,1]"
        inputs = inputs * 255.0
        preprocessed_input = tf.keras.applications.vgg19.preprocess_input(inputs)
        outputs = self.vgg(preprocessed_input)
        style_outputs, content_outputs = (outputs[:self.num_style_layers],
                                          outputs[self.num_style_layers:])

        style_outputs = [gram_matrix(style_output)
                         for style_output in style_outputs]

        return {'content': content_outputs, 'style': style_outputs}


painting_extractor=StyleContentModel(style_layers=style_layers,content_layers=content_layers)


def painting_similarity_matric(search_tensor, target_tensor):
    n = 0
    for i in range(num_style_layers):
        n += np.sum(flatten(np.square(target_tensor['style'][i] - search_tensor['style'][i])), axis=1)

    n /= num_style_layers

    sml = cosine_similarity(flatten(search_tensor['content'][0]), flatten(target_tensor['content'][0]))

    cs = sum(sml) / num_content_layers

    return cs, n


inception_net_index=[310,307,300,293]

TOTAL_FEATURE_MAPS=len(inception_net_index)


def InceptionNet(layer_index=inception_net_index):
  """ Creates a inception  model that returns a list of intermediate output values."""
  # Load our model. Load pretrained VGG, trained on imagenet data
  net=InceptionV3(include_top=False,input_shape=(256,256,3))

  net.trainable = False
  total_layers=net.layers
  outputs = [total_layers[i].output for i  in layer_index ]

  model = tf.keras.Model([net.input], outputs)
  return model

inception_classifier=InceptionNet()

import os


def getListOfFiles(dirname):
    os.listdir(path='.')
    listoffile = os.listdir(dirname)
    allfiles = []
    for f in listoffile:
        fullpath = os.path.join(dirname, f)
        if os.path.isdir(fullpath):
            allfiles += getListOfFiles(fullpath)
        else:
            if (imghdr.what(fullpath) in ['jpg', 'jpeg', 'png']):
                allfiles.append(fullpath)

    return allfiles


def process_img(SEARCH_DIR=None,from_file=None, shape=(256, 256)):
    if SEARCH_DIR:
        out = []
        li=getListOfFiles(SEARCH_DIR)
        print(li)
        #li = os.listdir(SEARCH_DIR)
        #print(li)
        for i in li:
            p = os.path.join(SEARCH_DIR, i)
            #print('p = ',p)
            img = load_img(p, target_size=shape)
            img=img_to_array(img)
            img = tf.cast(img, dtype=tf.float32)
            out.append(img)
        #print(out)
    else:
        img=load_img(from_file,target_size=shape)
        img=img_to_array(img)
        img=tf.cast(img,dtype=tf.float32)
        return img[tf.newaxis,...]

    return tf.convert_to_tensor(out), li

flatten=tf.keras.layers.Flatten()  # layer to flatten the input tensor

def similarity_matric(sim,target_img,TOTAL_FEATURE_MAPS):
  cs=0
  for i in range(TOTAL_FEATURE_MAPS):
    b=flatten(target_img[i])
    a=flatten(sim[i])
    cs+=cosine_similarity(a,b)

  return sum(cs)/TOTAL_FEATURE_MAPS


import pickle as pkl
def extract_image_from_pickle(PATH):
  with open(PATH,"rb") as watch_images:
    w_images=pkl.load(watch_images)

  li=[]
  for i in w_images:
    img=i.resize((256,256))
    img=img_to_array(img)
    img=tf.cast(img,dtype=tf.float32)
    li.append(img)


  target_input=tf.convert_to_tensor(li)


  return target_input,list(range(len(w_images)))


def sorted_result_Json(SEARCH_PATH=None, DIR_PATH=None, pickle_file_path=None, search_index=0, resize_shape=(256, 256)):
    if SEARCH_PATH:
        search_input = process_img(None,SEARCH_PATH,resize_shape)
    if DIR_PATH:
        target_input, index_list = process_img(DIR_PATH,None,resize_shape)

    li = []

    if pickle_file_path is not None and DIR_PATH is None:
        target_input, index_list = extract_image_from_pickle(pickle_file_path)
        if (SEARCH_PATH is None):
            search_input = target_input[search_index][tf.newaxis, ...]

    search_tensor = inception_classifier(search_input)
    target_tensor = inception_classifier(target_input)

    sml = similarity_matric(search_tensor, target_tensor, TOTAL_FEATURE_MAPS)
    for i, j in zip(sml, index_list):
        li.append({'path': j, 'value': i})

    dic = sorted(li, key=lambda i: i['value'], reverse=True)

    return dic


def sorted_paint_result_Json(SEARCH_PATH=None, DIR_PATH=None, pickle_file_path=None, search_index=0,
                             resize_shape=(256, 256),progress_func=None):
    if SEARCH_PATH:
        search_input = process_img(from_file=SEARCH_PATH, shape=resize_shape)
    if DIR_PATH:
        target_input, index_list = process_img(DIR_PATH, shape=resize_shape)

    li = []

    if pickle_file_path is not None and DIR_PATH is None:
        target_input, index_list = extract_image_from_pickle(pickle_file_path)
        if (SEARCH_PATH is None):
            search_input = target_input[search_index][tf.newaxis, ...]
    #print('result = ',len(target_input),len(index_list))
    for x in range(0,len(index_list),10):
        search_tensor = painting_extractor(search_input)
        target_tensor = painting_extractor(target_input[x:x+10])
        progress_func.emit((x/len(index_list))*100)
        cs, ss = painting_similarity_matric(search_tensor, target_tensor)
        for i, j, k in zip(index_list[x:x+10], ss, cs):
            li.append({'path': i, 'style': j, 'content': k})


    dic = sorted(li, key=lambda i: i['style'], reverse=False)

    return dic

def main():
    if search_image_path:

        if pickle_file_path:

            if search_image_path is None:
                if (search_index in None):
                    raise Exception("search_index is necessary")
                else:
                    if from_painting==True:
                        return sorted_result_Json(pickle_file_path=pickle_file_path, search_index=search_index)
            else:
                return sorted_result_Json(SEARCH_PATH=search_image_path, pickle_file_path=pickle_file_path)

    if target_dir_path:
        return sorted_result_Json(SEARCH_PATH=search_image_path, DIR_PATH=target_dir_path)

#print(sorted_result_Json(SEARCH_PATH='D:/AAA_BOOKS/PSC/Project/New folder/test1.jpg',DIR_PATH='D:/AAA_BOOKS/PSC/Project/New folder'))

#print(sorted_paint_result_Json(SEARCH_PATH='D:/AAA_BOOKS/PSC/Project/New folder/TEST/20170215_110928.jpg',DIR_PATH='D:/AAA_BOOKS/PSC/Project/New folder/TEST'))
