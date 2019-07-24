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

from mo.front.common.partial_infer.inner_product import caffe_inner_product
from mo.ops.op import Op


class InnerProduct(Op):
    op = 'FullyConnected'
    enabled = True

    def __init__(self, graph: nx.MultiDiGraph, attrs: dict):
        super().__init__(graph, {
            'type': 'FullyConnected',
            'op': 'FullyConnected',
            'out-size': None,
            'layout': 'NCHW',
            'infer': caffe_inner_product
        }, attrs)

    def supported_attrs(self):
        return ['out-size']
