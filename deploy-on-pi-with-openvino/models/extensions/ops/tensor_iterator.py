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

import logging as log

import networkx as nx
import numpy as np

from mo.utils.error import Error
from mo.graph.graph import Node, dict_includes
from mo.ops.op import Op
from mo.utils.utils import refer_to_faq_msg


class TensorIterator(Op):
    ''' Loop layer that iterates over tensors and execute embedded sub-graph.
    '''

    op = 'TensorIterator'


    def __init__(self, graph: nx.MultiDiGraph, attrs: dict):
        mandatory_props = {
            'type': __class__.op,
            'op': __class__.op,
            'input_port_map': [],  # a list of dicts with such attrs as external_port_id, etc.
            'output_port_map': [],  # a list of dicts with such attrs as external_port_id, etc.
            'back_edges': [], # a list of dicts with such attrs as from_layer, from_port, etc.
            'body': None,   # an nx.MultiDiGraph object with a body sub-graph
            'sub_graphs': ['body'],  # built-in attribute with all sub-graphg
            'infer': __class__.infer
        }
        super().__init__(graph, mandatory_props, attrs)


    def substitute_ie_attrs(self, new_attrs: dict):
        """
        Replace standard list of attribute in layer/data by attributes
        delivered by backend_attrs
        """

        port_map_attrs = [
            'external_port_id',
            'internal_layer_id',
            'internal_port_id',
            'axis',
            'start',
            'stride',
            'end',
            'part_size'
        ]

        back_edges_attrs = [
            ('from-layer', 'from_layer'),
            ('from-port', 'from_port'),
            ('to-layer', 'to_layer'),
            ('to-port', 'to_port'),
        ]

        new_attrs.update({
            'IE': [(
                'layer',
                [('id', lambda node: node.node), 'name', 'precision', 'type'],
                [
                    ('data', self.backend_attrs() + self.default_backend_attrs, []),
                    '@ports',
                    ('port_map', [], [
                        ('@list', lambda node: self.generate_port_map(node, node.input_port_map), ('input', port_map_attrs, [])),
                        ('@list', lambda node: self.generate_port_map(node, node.output_port_map), ('output', port_map_attrs, [])),
                    ]),
                    ('back_edges', [], [
                        ('@list', lambda node: self.generate_back_edges(node), ('edge', back_edges_attrs, [])),
                    ]),
                    ('body', [], [('@network', 'body')]),
                ])]
        })

    @staticmethod
    def find_port_id(node: Node, virtual_id, attr):
        attrs = node.edge({attr: virtual_id})[2]
        assert bool('in' in attrs) != bool('out' in attrs)
        return attrs['in' if 'in' in attrs else 'out']


    @staticmethod
    def find_internal_layer_id(graph: nx.MultiDiGraph, virtual_id):
        internal_nodes = list(filter(lambda d: dict_includes(d[1], {'internal_layer_id': virtual_id}), graph.nodes(data=True)))
        assert len(internal_nodes) == 1, 'Nodes: {}, virtual_id: {}'.format(internal_nodes, virtual_id)
        return  internal_nodes[0][0]


    @staticmethod
    def find_internal_layer_and_port(graph: nx.MultiDiGraph, virtual_layer_id, virtual_port_id):
        internal_layer_id = __class__.find_internal_layer_id(graph, virtual_layer_id)
        internal_port_id = __class__.find_port_id(Node(graph, internal_layer_id), virtual_port_id, 'internal_port_id')
        return internal_layer_id, internal_port_id


    @staticmethod
    def generate_port_map(node: Node, src_port_map):
        ''' Extract port_map attributes from node and node.body attributes.
        
            It iterates over src_port_map and substitude external_port_id, internal_port_id and
            internal_layer_id by real values queried from node ports and node.body attributes.
        '''
        result_list = []
        for map_item in src_port_map:
            result = dict(map_item)
            assert result is not map_item
            result['external_port_id'] = __class__.find_port_id(node, result['external_port_id'], 'external_port_id')
            result['internal_layer_id'], result['internal_port_id'] = __class__.find_internal_layer_and_port(
                node.body, result['internal_layer_id'], result['internal_port_id'])
            result_list.append(result)
        return result_list


    @staticmethod
    def generate_back_edges(node: Node):
        ''' Extract back_edges attributes from node and node.body attributes. '''
        result_list = []
        for back_edge in node.back_edges:
            result = dict(back_edge)
            assert result is not back_edge
            result['from_layer'], result['from_port'] = __class__.find_internal_layer_and_port(
                node.body, result['from_layer'], result['from_port'])
            result['to_layer'], result['to_port'] = __class__.find_internal_layer_and_port(
                node.body, result['to_layer'], result['to_port'])
            result_list.append(result)
        return result_list


    @staticmethod
    def infer(node: Node):
        return
        raise Error('TensorIterator.infer is not implemented. '
            'Do not insert TensorIterator before middle-end in Model Optimizer')
