import torch

import triton
import triton.language as tl
import triton_viz
import argparse


@triton_viz.trace
@triton.jit
def dot_kernel(x_ptr, y_ptr, z_ptr, BLOCK_SIZE: tl.constexpr):
    x_val = tl.load(
        x_ptr
        + tl.arange(0, BLOCK_SIZE)[:, None] * BLOCK_SIZE
        + tl.arange(0, BLOCK_SIZE)[None, :]
    )
    y_val = tl.load(
        y_ptr
        + tl.arange(0, BLOCK_SIZE)[:, None] * BLOCK_SIZE
        + tl.arange(0, BLOCK_SIZE)[None, :]
    )
    z = tl.dot(x_val, y_val)
    tl.store(
        z_ptr
        + tl.arange(0, BLOCK_SIZE)[:, None] * BLOCK_SIZE
        + tl.arange(0, BLOCK_SIZE)[None, :],
        z,
    )


argparser = argparse.ArgumentParser()
argparser.add_argument("--device", type=str, default="cpu")
device = argparser.parse_args().device

triton_viz.sample((0,))
BLOCK_SIZE = 64
x = torch.randn((BLOCK_SIZE, BLOCK_SIZE), device=device)
y = torch.randn((BLOCK_SIZE, BLOCK_SIZE), device=device)
z = torch.zeros((BLOCK_SIZE, BLOCK_SIZE), device=device)

dot_kernel[(1,)](x, y, z, BLOCK_SIZE)

triton_viz.dump("./dot.json")
