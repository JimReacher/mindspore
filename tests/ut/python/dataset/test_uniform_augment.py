# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from mindspore import log as logger
import mindspore.dataset.engine as de
import mindspore.dataset.transforms.vision.py_transforms as F

DATA_DIR = "../data/dataset/testImageNetData/train/"

def visualize(image_original, image_ua):
    """
    visualizes the image using DE op and Numpy op
    """
    num = len(image_ua)
    for i in range(num):
        plt.subplot(2, num, i + 1)
        plt.imshow(image_original[i])
        plt.title("Original image")

        plt.subplot(2, num, i + num + 1)
        plt.imshow(image_ua[i])
        plt.title("DE UniformAugment image")

    plt.show()
    

def test_uniform_augment(plot=False, num_ops=2):
    """
    Test UniformAugment
    """
    logger.info("Test UniformAugment")
    
    # Original Images
    ds = de.ImageFolderDatasetV2(dataset_dir=DATA_DIR, shuffle=False)    
    
    transforms_original = F.ComposeOp([F.Decode(),
                                       F.Resize((224,224)),
                                       F.ToTensor()])    
    
    ds_original = ds.map(input_columns="image",
                         operations=transforms_original())
    
    ds_original = ds_original.batch(512)
            
    for idx, (image,label) in enumerate(ds_original):
        if idx == 0:
            images_original = np.transpose(image, (0, 2,3,1))
        else:
            images_original = np.append(images_original,
                                        np.transpose(image, (0, 2,3,1)),
                                        axis=0)    

    # UniformAugment Images
    ds = de.ImageFolderDatasetV2(dataset_dir=DATA_DIR, shuffle=False)    
    
    transform_list = [F.RandomRotation(45),
                      F.RandomColor(),
                      F.RandomSharpness(),
                      F.Invert(),
                      F.AutoContrast(),
                      F.Equalize()]
    
    transforms_ua = F.ComposeOp([F.Decode(),
                                 F.Resize((224,224)),
                                 F.UniformAugment(transforms=transform_list, num_ops=num_ops),
                                 F.ToTensor()])    
    
    ds_ua = ds.map(input_columns="image",
                   operations=transforms_ua())
    
    ds_ua = ds_ua.batch(512)    
      
    for idx, (image,label) in enumerate(ds_ua):
        if idx == 0:
            images_ua = np.transpose(image, (0, 2,3,1))
        else:
            images_ua = np.append(images_ua,
                                  np.transpose(image, (0, 2,3,1)),
                                  axis=0)
    
    num_samples = images_original.shape[0]
    mse = np.zeros(num_samples)
    for i in range(num_samples):
        mse[i] = np.mean((images_ua[i]-images_original[i])**2)
    logger.info("MSE= {}".format(str(np.mean(mse))))
    
    if plot:
        visualize(images_original, images_ua)
        

if __name__ == "__main__":
    test_uniform_augment(num_ops=1)
    
