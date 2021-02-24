# torch.nn.functional.pad

2021/2/24  

因为有[官方文档](https://pytorch.org/docs/stable/nn.functional.html#torch.nn.functional.pad)，所以这种东西都写得简单些。（不会真有人查自己的blog而不是查官方doc吧，不会吧不会吧不会吧）  

## torch.nn.functional.pad(input, pad, mode='constant', value=0)  
## Parameters  
* **input** (Tensor) – N维 tensor
* **pad** (tuple，数组) – m个元素的数组, 其中$$ \frac{m}{2}<input dim $$ ，m是偶数。
* **mode** – 'constant', 'reflect', 'replicate' or 'circular'. 默认值: 'constant'。
* **value** – 'constant'模式下的填充值。默认值: 0
