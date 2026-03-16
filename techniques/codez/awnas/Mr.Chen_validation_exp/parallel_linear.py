import itertools
from timeit import default_timer

import argparse

import torch
from torch import Tensor, nn
from torch.nn import functional as F


class MLP(nn.Module):
    def __init__(self, num_features):
        super().__init__()
        self.num_features = num_features
        self.layers = nn.Sequential(
            nn.Linear(num_features, num_features, bias=False),
            nn.Linear(num_features, num_features, bias=False),
            nn.Linear(num_features, num_features, bias=False),
            nn.Linear(num_features, num_features, bias=False),
            nn.Linear(num_features, 1, bias=False),
        )

    def forward(self, x):
        return self.layers(x)


def parallel_linear(weight, x):
    return torch.matmul(weight, x.t()).transpose(1, 2)


def get_all_indices(num_parallel, in_features, out_features):
    # Get all indices where the weights will be changed in a parallelized linear layer
    # Output is a tensor of shape [3, D_out \times D_in]
    return torch.tensor(
        [
            (k, j, i)
            for k, (j, i) in zip(
                itertools.cycle(range(num_parallel)),
                itertools.product(
                    range(out_features),
                    range(in_features),
                ),
            )
        ]
    ).t()


@torch.no_grad()
def parallel_cdg(
    num_parallel: int,
    target_model: nn.Module,
    test_model: nn.Module,
    x: Tensor,
    epsilon: float,
    learning_rates: Tensor,
    normalize=True,
    device="cuda",
):
    grad = {
        n: torch.zeros(p.shape, device=device) for n, p in test_model.named_parameters()
    }

    y_target = target_model(x)

    for i_layer in range(len(test_model.layers)):
        # save intermediate result of previous layers
        new_x = test_model.layers[:i_layer](x)

        current_layer = test_model.layers[i_layer]
        latter_layers = test_model.layers[i_layer + 1 :]
        assert isinstance(current_layer, nn.Linear)

        # iterable trickery to get all indices where the weights will be changed
        indices = get_all_indices(
            num_parallel, current_layer.in_features, current_layer.out_features
        )

        for kji in indices.split(num_parallel, dim=1):
            # k, j, i are vectors each used to index a dimension
            k, j, i = kji.unbind()
            # split_size is num_parallel or smaller (at the last split)
            split_size = len(k)

            new_weight = current_layer.weight.repeat(split_size, 1, 1)
            y_target_ex = y_target.expand(split_size, -1, -1)

            # calculation of current_layer is replaced with parallel_linear
            new_weight[k, j, i] += epsilon
            y_test = latter_layers(parallel_linear(new_weight, new_x))
            L_a = F.mse_loss(y_test, y_target_ex, reduction="none").mean(dim=(1, 2))

            new_weight[k, j, i] -= epsilon * 2
            y_test = latter_layers(parallel_linear(new_weight, new_x))
            L_m = F.mse_loss(y_test, y_target_ex, reduction="none").mean(dim=(1, 2))

            grad[f"layers.{i_layer}.weight"][j, i] = (L_a - L_m) / (epsilon * 2)

    if normalize:
        grad = {n: v / (torch.norm(v) + 1e-8) for n, v in grad.items()}

    backup_weights = {n: v.clone() for n, v in test_model.state_dict().items()}
    best_loss = 9999
    best_lr = 0
    for lr in learning_rates:
        test_model.load_state_dict(
            {n: v - lr * grad[n] for n, v in backup_weights.items()}
        )

        y_test = test_model(x)
        loss = F.mse_loss(y_test, y_target)
        if loss < best_loss:
            best_loss = loss
            best_lr = lr

    # the function makes no modification to the models
    test_model.load_state_dict(backup_weights)

    return best_loss, best_lr


device = 0
num_parallel = 128
seed = 0
timeit = True

if seed is not None:
    torch.manual_seed(seed)

device = f"cuda:{device}" if torch.cuda.is_available() else "cpu"

batch_size = 1024
num_features = 32

target_model = MLP(num_features).to(device)
test_model = MLP(num_features).to(device)

learning_rates = torch.arange(1e-4, 1e-1, 2e-4)

num_batches = 10

if timeit:
    start = default_timer()

for i_batch in range(num_batches):
    x = torch.randn((batch_size, num_features), device=device)

    best_loss, best_lr = parallel_cdg(
        num_parallel,
        target_model,
        test_model,
        x,
        0.1,
        learning_rates,
        device=device,
    )

    print(f"i_batch={i_batch}, best_loss={best_loss:.4f}, best_lr={best_lr:.4f}")

if timeit:
    print(f"total_time={default_timer() - start}")
