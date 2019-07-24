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
from mo.graph.graph import Node
from mo.ops.op import Op
from mo.utils.error import Error


class Enter(Op):
    op = "Enter"

    def __init__(self, graph: nx.MultiDiGraph, attrs: dict):
        mandatory_props = {
            'type': __class__.op,
            'op': __class__.op,
            'infer': Enter.enter_infer,
        }
        super().__init__(graph, mandatory_props, attrs)

    @staticmethod
    def enter_infer(node: Node):
        output_shape = node.in_node(0).shape
        output_value = node.in_node(0).value

        for _, out_node in node.graph.out_edges(node.id):
            node.graph.node[out_node]['shape'] = np.array(output_shape)
            node.graph.node[out_node]['value'] = None if output_value is None else np.array(output_value)
