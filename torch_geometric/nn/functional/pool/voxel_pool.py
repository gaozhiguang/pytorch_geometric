from torch_cluster import sparse_grid_cluster, dense_grid_cluster
import torch
from torch.autograd import Variable
from .pool import max_pool
from .pool import avg_pool
from ....datasets.dataset import Data
from ...modules.spline_conv import repeat_to
from torch_scatter import scatter_add
import torch.nn.functional as F


def sparse_voxel_max_pool(data, size, start=None, transform=None, weight=None):
    pos_tensor = data.pos if torch.is_tensor(data.pos) else data.pos.data
    size = pos_tensor.new(repeat_to(size, data.pos.size(1)))

    if start is not None:
        start = pos_tensor.new(repeat_to(start, data.pos.size(1)))

    output = sparse_grid_cluster(pos_tensor, size, data.batch, start)
    cluster = output[0] if isinstance(output, tuple) else output
    batch = output[1] if isinstance(output, tuple) else None

    if weight is not None:
        weight = F.relu(weight).unsqueeze(1) + 0.0001  # avoid all zero
        norm = scatter_add(Variable(cluster), weight.squeeze(), dim=0)
        norm = torch.gather(norm, 0, Variable(cluster))
        weight = weight / norm.unsqueeze(1)

    input, index, pos = max_pool(data.input, data.index, data.pos, cluster,
                                 weight=weight)

    data = Data(input, pos, index, None, data.target, batch)

    if transform is not None:
        data = transform(data)

    return data, cluster


def dense_voxel_max_pool(data, size, start=None, end=None, transform=None,
                         weight=None):
    pos_tensor = data.pos if torch.is_tensor(data.pos) else data.pos.data
    size = pos_tensor.new(repeat_to(size, data.pos.size(1)))

    if start is not None:
        start = pos_tensor.new(repeat_to(start, data.pos.size(1)))

    if end is not None:
        end = pos_tensor.new(repeat_to(end, data.pos.size(1)))

    cluster, C = dense_grid_cluster(pos_tensor, size, data.batch, start, end)

    input, index, pos = max_pool(data.input, data.index, data.pos, cluster, C,
                                 weight=weight)

    data = Data(input, pos, index, None, data.target)

    if transform is not None:
        data = transform(data)

    return data, cluster


def sparse_voxel_avg_pool(data, size, start=None, transform=None, weight=None,
                          weight_values=False, weight_pos=False):
    pos_tensor = data.pos if torch.is_tensor(data.pos) else data.pos.data
    size = pos_tensor.new(repeat_to(size, data.pos.size(1)))

    if start is not None:
        start = pos_tensor.new(repeat_to(start, data.pos.size(1)))

    output = sparse_grid_cluster(pos_tensor, size, data.batch, start)
    cluster = output[0] if isinstance(output, tuple) else output
    batch = output[1] if isinstance(output, tuple) else None

    if weight is not None:
        weight = F.relu(weight).unsqueeze(1) + 0.0001  # avoid all zero
        norm = scatter_add(Variable(cluster), weight.squeeze(), dim=0)
        norm = torch.gather(norm, 0, Variable(cluster))
        weight = weight / norm.unsqueeze(1)

    input, index, pos = avg_pool(data.input, data.index, data.pos, cluster,
                                 weight=weight, weight_values=False,
                                 weight_pos=False)

    data = Data(input, pos, index, None, data.target, batch)

    if transform is not None:
        data = transform(data)

    return data, cluster


def dense_voxel_avg_pool(data, size, start=None, end=None, transform=None,
                         weight=None, weight_values=False, weight_pos=False):
    pos_tensor = data.pos if torch.is_tensor(data.pos) else data.pos.data
    size = pos_tensor.new(repeat_to(size, data.pos.size(1)))

    if start is not None:
        start = pos_tensor.new(repeat_to(start, data.pos.size(1)))

    if end is not None:
        end = pos_tensor.new(repeat_to(end, data.pos.size(1)))

    cluster, C = dense_grid_cluster(pos_tensor, size, data.batch, start, end)

    input, index, pos = avg_pool(data.input, data.index, data.pos, cluster, C,
                                 weight=weight)

    data = Data(input, pos, index, None, data.target)

    if transform is not None:
        data = transform(data)

    return data, cluster