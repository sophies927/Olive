# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
# Tensor Parallel layers. 
# This layers could replace corresponding PyTorch layers.
# --------------------------------------------------------------------------

import torch
import torch.distributed as dist
from torch.distributed.distributed_c10d import _get_default_group
import torch.nn.functional as F
from torch import nn
import math


class AllReduce(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x) -> torch.Tensor:
        if torch.onnx.is_in_onnx_export():
            return x
        dist.all_reduce(x, op=dist.ReduceOp.SUM)
        return x

    @staticmethod
    def symbolic(g: torch.Graph, x) -> torch.Value:
        return g.op("com.microsoft::AllReduce", x)


def get_process_group():
    return _get_default_group()


def get_world_size():
    return dist.get_world_size(get_process_group())


class TensorParallelColumnLinear(nn.Module):
    def __init__(
        self,
        in_features,
        out_features,
        bias=True,
        device=None,
        dtype=None,
        process_group: torch.distributed.ProcessGroup = None,
    ):
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.use_bias = bias
        self.in_features = in_features
        self.out_features = out_features
        self.rank_weights = []
        self.rank_biases = []
        # We change from traditional `nn.Linear` and remove unecessary `torch.Tensor.transpose` operation
        self.weight = nn.Parameter(torch.empty((self.out_features, self.in_features), **factory_kwargs))
        if bias:
            self.bias = nn.Parameter(torch.empty(self.out_features, **factory_kwargs))
        else:
            self.register_parameter("bias", None)

        self.reset_parameters()

    def parallel_split(self, world_size):
        if world_size == 1:
            return
        
        assert self.out_features % world_size == 0
        # Split weights in multiple chunks.
        # This could be optimized
        for r in world_size:
            self.rank_weights.append(self.weight.chunk(self.world_size)[r])
            if self.use_bias:
                self.rank_biases.append(self.bias.chunk(self.tp_world_size)[r])

    def load_rank_weights(self, rank):
        self.weight = nn.Parameter(self.rank_weights[rank])
        if self.use_bias:
            self.bias = nn.Parameter(self.rank_biases[rank])

    def reset_parameters(self) -> None:
        """From `torch.nn.Linear`"""
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(in_features), 1/sqrt(in_features)). For details, see
        # https://github.com/pytorch/pytorch/issues/57109
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
            nn.init.uniform_(self.bias, -bound, bound)

    def extra_repr(self) -> str:
        """From `torch.nn.Linear`"""
        return "in_features={}, out_features={}, bias={}".format(
            self.in_features, self.out_features, self.bias is not None
        )

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        out = F.linear(input, weight=self.weight, bias=self.bias)
        return out


class TensorParallelRowLinear(nn.Module):
    def __init__(
        self,
        in_features,
        out_features,
        bias=True,
        device=None,
        dtype=None,
        process_group: torch.distributed.ProcessGroup = None,
    ):
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.use_bias = bias
        self.in_features = in_features
        self.out_features = out_features
        self.rank_weights = []
        # We change from traditional `nn.Linear` and remove unecessary `torch.Tensor.transpose` operation
        self.weight = nn.Parameter(torch.empty((self.out_features, self.in_features), **factory_kwargs))
        if bias:
            self.bias = nn.Parameter(torch.empty(self.out_features, **factory_kwargs))
        else:
            self.register_parameter("bias", None)

        self.reset_parameters()

    def parallel_split(self, world_size):
        if world_size == 1:
            return

        assert self.in_features % world_size == 0
        # Split weights in multiple chunks.
        # This could be optimized
        for r in world_size:
            self.rank_weights.append(self.weight.chunk(world_size, dim=1)[r])

    def load_rank_weights(self, rank):
        self.weight = nn.Parameter(self.rank_weights[rank])

    def reset_parameters(self) -> None:
        """From `torch.nn.Linear`"""
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(in_features), 1/sqrt(in_features)). For details, see
        # https://github.com/pytorch/pytorch/issues/57109
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
            nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        out = F.linear(input, weight=self.weight, bias=self.bias)
        out = AllReduce.apply(out)

        return out

    def extra_repr(self) -> str:
        """From `torch.nn.Linear`"""
        return "in_features={}, out_features={}, bias={}".format(
            self.in_features, self.out_features, self.bias is not None
        )
