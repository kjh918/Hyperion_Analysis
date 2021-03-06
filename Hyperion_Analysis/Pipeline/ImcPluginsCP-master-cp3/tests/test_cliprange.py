'''test_stackimages.py - test the stackimages module
'''

import StringIO
import base64
import unittest
import zlib

import numpy as np
from scipy.ndimage import gaussian_filter

from cellprofiler.preferences import set_headless

set_headless()

import cellprofiler.workspace as cpw
import cellprofiler.image as cpi
import cellprofiler.module as cpm
import cellprofiler.modules as modules
import cellprofiler.object as cpo
import cellprofiler.pipeline as cpp
import cellprofiler.measurement as cpmeas

import plugins.cliprange as C

INPUT_IMAGE_NAME = 'myimage'

OUTPUT_IMAGE_NAME = 'myclippedimage'


class TestStackImages(unittest.TestCase):
    def make_workspace(self, image, outlier_percentile):
        '''Make a workspace '''
        module = C.ClipRange()
        pipeline = cpp.Pipeline()
        object_set = cpo.ObjectSet()
        image_set_list = cpi.ImageSetList()
        image_set = image_set_list.get_image_set(0)
        workspace = cpw.Workspace(pipeline,
                                  module,
                                  image_set,
                                  object_set,
                                  cpmeas.Measurements(),
                                  image_set_list)

        # setup the input images
        image_set.add(INPUT_IMAGE_NAME, cpi.Image(image))

        # setup the input images settings
        module.x_name.value = INPUT_IMAGE_NAME
        module.y_name.value = OUTPUT_IMAGE_NAME
        module.outlier_percentile.value = outlier_percentile

        return workspace, module

    def test_clip_gray(self):
        """
        The test is to create an image with pixel values 0:100. After 
        using a 95 percentile, the image max should be 95. 
        all values < 95 should be not touched.
        """
        perc = 0.95
        maxval = 0.95
        img = np.reshape(np.arange(1,101.)/100, (10,10))
        workspace, module = self.make_workspace(img, perc)
        module.run(workspace)
        result = workspace.image_set.get_image(OUTPUT_IMAGE_NAME).pixel_data
        np.testing.assert_almost_equal(result.max(), maxval)
        fil = img == maxval
        np.testing.assert_almost_equal(img[fil], result[fil])

    def test_clip_multichan(self):
        """
        Image channel 1 will be values from 0.005 to 0.5,
        Plane 2 from 0.505 to 1
        After clipping the 95th the max values should be:
            0.95/2
            and 0.95/2+0.5
        """
        perc = 0.95
        maxvals = (0.95/2, 0.95/2+0.5)
        img = np.reshape(np.arange(1,201.)/200, (10,10, 2),order='F')
        workspace, module = self.make_workspace(img, perc)
        module.run(workspace)
        result = workspace.image_set.get_image(OUTPUT_IMAGE_NAME).pixel_data
        np.testing.assert_almost_equal(result.max(axis=(0,1)), maxvals)
