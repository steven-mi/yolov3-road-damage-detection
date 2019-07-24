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

from mo.front.extractor import FrontExtractorOp
from extensions.ops.TensorArrayGather import TensorArrayGather
from mo.front.tf.extractors.utils import tf_int_list, tf_tensor_shape
from mo.graph.graph import Node


class TensorArrayGatherV3Exteractor(FrontExtractorOp):
    op = "TensorArrayGatherV3"
    enabled = True

    @staticmethod
    def extract(node: Node):
        attrs = {
            'op': __class__.op,
            'element_shape': tf_tensor_shape(node.pb.attr["element_shape"].shape),
        }
        TensorArrayGather.update_node_stat(node, attrs)
        return __class__.enabled

