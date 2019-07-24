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

from mo.front.common.replacement import FrontReplacementPattern
from mo.middle.passes.eliminate import remove_op_node_with_data_node


class FuseRepeatedReshapes(FrontReplacementPattern):
    enabled = False

    @staticmethod
    def pattern():
        return dict(
            nodes=[
                ('reshape_1', dict(kind='op', op='Reshape')),
                ('data_node', dict(kind='data')),
                ('reshape_2', dict(kind='op', op='Reshape'))
            ],
            edges=[
                ('reshape_1', 'data_node', {'out': 0}),
                ('data_node', 'reshape_2', {'in': 0})
            ]
        )

    @staticmethod
    def replace_pattern(graph: nx.MultiDiGraph, match: dict):
        node = match['reshape_1']
        if (node.has_valid('type') and node.type == 'Reshape' and
                len(node.out_nodes()) == 1 and node.out_node().has_valid('kind') and node.out_node().kind == 'data' and
                len(node.out_node().out_nodes()) == 1):
            remove_op_node_with_data_node(graph, node)
