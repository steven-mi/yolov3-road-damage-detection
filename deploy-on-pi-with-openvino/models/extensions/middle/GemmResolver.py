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

from extensions.middle.NormalizeFullyConnected import NormalizeFullyConnected
from mo.front.common.partial_infer.utils import mark_input_bins, assign_dims_to_weights, int64_array
from mo.middle.replacement import MiddleReplacementPattern
from mo.ops.op import PermuteAttrs


class GemmResolver(MiddleReplacementPattern):
    enabled = True

    def run_before(self):
        return [NormalizeFullyConnected]

    def pattern(self):
        return dict(
            nodes=[
                   ('input_0', dict(kind='data')),
                   ('input_1', dict(kind='data')),
                   ('fc', dict(op='MatMul')),
                   ('fc_data', dict(kind='data'))],
            edges=[
                ('input_0', 'fc', {'in': 0}),
                ('input_1', 'fc', {'in': 1}),
                ('fc', 'fc_data')
            ]
        )

    def replace_pattern(self, graph: nx.MultiDiGraph, match: dict):
        if not match['input_0'].has_valid('value') and not match['input_1'].has_valid('value') or \
                not match['input_0'].has_valid('value') and match['input_1'].has_valid('value') and match['input_1'].shape.size > 2:
            match['fc']['type'] = 'GEMM'
        elif not match['input_0'].has_valid('value') and match['input_1'].has_valid('value'):
            match['fc']['type'] = 'FullyConnected'
            node = match['fc']
            mark_input_bins(node)
            weights_node = match['input_1']
            assign_dims_to_weights(weights_node, None, 0, 1, 2)
            PermuteAttrs.set_permutation(weights_node, node, PermuteAttrs.Permutation(perm=int64_array([1, 0]),
                                                                                      inv=int64_array([0, 1])))
            weights_shape = weights_node.shape

            node['out-size'] = weights_shape[1]



