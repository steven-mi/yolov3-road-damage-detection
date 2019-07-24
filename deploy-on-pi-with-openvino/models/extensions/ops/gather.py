"""
 Copyright (c) 2017-2018 Intel Corporation

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

from mo.graph.graph import Node
from mo.ops.op import Op


class Gather(Op):
    op = 'Gather'

    def __init__(self, graph: nx.MultiDiGraph, attrs: dict):
        mandatory_props = {
            'type': __class__.op,
            'op': __class__.op,
            'axis': 0,
            'infer': __class__.infer
        }
        super().__init__(graph, mandatory_props, attrs)

    def supported_attrs(self):
        return [
            'axis',
        ]

    @staticmethod
    def infer(node: Node):
        assert len(node.in_nodes()) == 2 or len(node.in_nodes()) == 3

        # There may be three inputs in TensorFlow. The third input is axis
        if len(node.in_nodes()) == 3:
            if node.in_node(2).value is None:
                log.error("Gather is supported only with constant axis value")
                return
            node.axis = node.in_node(2).value.item()
            node.graph.remove_edge(node.in_node(2).id, node.id)

        axis = node.axis
        data = node.in_node(0)
        indices = node.in_node(1)

        # both inputs are constant
        if data.value is not None and indices.value is not None:
            node.out_node(0).value = np.take(data.value, indices.value, axis)
            node.out_node(0).shape = np.array(node.out_node(0).value.shape, dtype=np.int64)
            return

        shape = np.concatenate((data.shape[:axis], indices.shape))
        if axis < len(data.shape) - 1:
            shape = np.concatenate((shape, data.shape[axis+1:]))

        node.out_node(0).shape = np.array(shape, dtype=np.int64)
