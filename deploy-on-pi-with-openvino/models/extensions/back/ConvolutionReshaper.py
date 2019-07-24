"""
 Copyright (c) 2018 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import networkx as nx
import numpy as np

from mo.back.replacement import BackReplacementPattern
from mo.ops.reshape import Reshape


class ConvolutionReshaper(BackReplacementPattern):
    """
        Workarounds absence of 1D Convolution support in Inference Engine by converting it to 2D Convolution
            - updating shape dependent Convolution parameters with fake H: dilation, kernel, pad, stride
            - reshape weights from [OIX] -> [OIYX] = [OI1X]
            - inserting fake H dimension by adding reshapes before and after Convolution: [NCW] -> [NCHW] = [NC1W]
    """
    enabled = True

    @staticmethod
    def pattern():
        return dict(
            nodes=[
                ('conv', dict(type='Convolution'))
            ],
            edges=[]
        )

    def replace_pattern(self, graph: nx.MultiDiGraph, match: dict):
        conv = match['conv']

        assert len(conv.out_nodes()) == 1, "Convolution operation {} should have 1 output data node".format(conv.id)
        out_data = conv.out_node()

        assert out_data.has_valid('shape'), 'Output shape is undefined for {} in back phase'.format(conv.id)
        out_shape = out_data.shape

        if out_shape.size != 3:
            return

        assert len(conv.in_nodes()) >= 1, "Convolution operation {} should have more than 1 input data node".format(conv.id)
        inp_data = conv.in_node()

        assert inp_data.has_valid('shape'), 'Input shape is undefined for {} in back phase'.format(conv.id)
        inp_shape = inp_data.shape
        new_inp_shape = np.insert(inp_shape, 2, 1)

        # setting to None to be overwritten by infer function
        conv.kernel_spatial_idx = None
        conv.spatial_dims = None

        # inserting fake H dimension
        conv.dilation = np.insert(conv.dilation, 2, 1)
        conv.kernel_spatial = np.append([1], conv.kernel_spatial)
        conv.pad = np.insert(conv.pad, 2, [0, 0], axis=0)
        conv.stride = np.insert(conv.stride, 2, 1)

        weights_index = len(conv.in_nodes()) - 2
        weights_node = conv.in_node(weights_index)
        weights_node.value = np.reshape(weights_node.value, np.insert(weights_node.value.shape, 2, 1))
        weights_node.shape = np.array(weights_node.value.shape, dtype=np.int64)

        conv.bracket_op_with_another_op(inp=inp_data, out=out_data, new_op_class=Reshape,
                                        op_before_params={'dim': new_inp_shape},
                                        op_after_params={'dim': out_shape})
