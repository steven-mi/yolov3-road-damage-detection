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

from mo.front.common.layout import get_width_dim, get_height_dim
from mo.front.extractor import attr_getter
from mo.graph.graph import Node
from mo.ops.op import Op


class PriorBoxOp(Op):
    op = 'PriorBox'

    def __init__(self, graph: nx.MultiDiGraph, attrs: dict):
        mandatory_props = {
            'type': __class__.op,
            'op': __class__.op,
            'flip': 1,
            'max_size': np.array([]),
            'min_size': np.array([]),
            'aspect_ratio': np.array([]),
            'infer': PriorBoxOp.priorbox_infer
        }
        super().__init__(graph, mandatory_props, attrs)

    def supported_attrs(self):
        return [
            'min_size',
            'max_size',
            'aspect_ratio',
            'flip',
            'clip',
            'variance',
            'img_size',
            'img_h',
            'img_w',
            'step',
            'step_h',
            'step_w',
            'offset',
        ]

    def backend_attrs(self):
        return [
            'flip',
            'clip',
            'step',
            'offset',
            ('min_size', lambda node: attr_getter(node, 'min_size')),
            ('max_size', lambda node: attr_getter(node, 'max_size')),
            ('aspect_ratio', lambda node: attr_getter(node, 'aspect_ratio')),
            ('variance', lambda node: attr_getter(node, 'variance')),
        ]

    @staticmethod
    def priorbox_infer(node: Node):
        layout = node.graph.graph['layout']
        data_shape = node.in_node(0).shape

        # calculate all different aspect_ratios (the first one is always 1)
        # in aspect_ratio 1/x values will be added for all except 1 if flip is True
        ar_seen = [1.0]
        ar_seen.extend(node.aspect_ratio.copy())
        if node.flip:
            for s in node.aspect_ratio:
                ar_seen.append(1.0/s)

        ar_seen = np.unique(np.array(ar_seen).round(decimals=6))
        
        num_ratios = 0
        if len(node.min_size) > 0:
            num_ratios = len(ar_seen) * len(node.min_size)

        num_ratios = num_ratios + len(node.max_size)

        res_prod = data_shape[get_height_dim(layout, 4)] * data_shape[get_width_dim(layout, 4)] * num_ratios * 4
        node.out_node(0).shape = np.array([1, 2, res_prod], dtype=np.int64)
