# Pytorch的训练过程  

2021/4/6  

摸了三整天的鱼，内心非常不安。看BMXNet的代码，在仔细研究网络实现之前看了看训练步骤，尝试弥补对pytorch训练认识的缺失。  

首先是来自[简书的注释代码](https://www.jianshu.com/p/e704a6f6e8d3)：  

```python  
# 训练网络
# 迭代epoch
for epoch in range(20):

    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the input
        inputs, labels = data

        # zeros the paramster gradients
        optimizer.zero_grad()       # 

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)  # 计算loss
        loss.backward()     # loss 求导
        optimizer.step()    # 更新参数

        # print statistics
        running_loss += loss.item()  # tensor.item()  获取tensor的数值
        if i % 2000 == 1999:
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 2000))  # 每2000次迭代，输出loss的平均值
            running_loss = 0.0

print('Finished Training')

```  

看起来**epoch和step都是用for循环实现的**。epoch循环下面的`running_loss`看起来是每2000 steps打印loss用的buffer。在epoch内部，首先获取当前的mini batch，需要将**parameter的gradient置为零**（`optimizer.zero_grad()`），forward计算当前网络的output，根据criterion计算loss，用`loss.backward()`求导，再`optimizer.step()`**更新参数**。  

之后是BMXNetv2的epoch循环体：  

```python  
    for epoch in range(opt.start_epoch, opt.epochs):
        global_step = epoch * num_examples
        track_lr(epoch, global_step)
        tic = time.time()
        if hasattr(train_data, "reset"):
            train_data.reset()
        metric.reset()
        btic = time.time()
        for i, batch in enumerate(train_data):
            data, label = batch_fn(batch, ctx)
            outputs = []
            Ls = []
            with autograd.record():
                for x, y in zip(data, label):
                    z = net(x)
                    L = loss(z, y)
                    # store the loss and do backward after we have done forward
                    # on all GPUs for better speed on multiple GPUs.
                    Ls.append(L)
                    outputs.append(z)
                autograd.backward(Ls)
            trainer.step(batch_size)
            metric.update(label, outputs)

            if opt.log_interval and not (i+1) % opt.log_interval:
                name, acc = metric.get()
                log_metrics("batch", name, acc, epoch, summary_writer, global_step,
                            sep=" [%d]\tSpeed: %f samples/sec\t" % (i, batch_size/(time.time()-btic)))
                log_progress(num_examples, opt, epoch, i, time.time()-tic, epoch_time)
                track_lr(epoch, global_step)

            btic = time.time()
            global_step += batch_size
            if opt.test_run:
                break

        epoch_time = time.time()-tic

        write_net_summaries(summary_writer, ctx[0], global_step=global_step)

        # First epoch will usually be much slower than the subsequent epics,
        # so don't factor into the average
        if num_epochs > 0:
            total_time = total_time + epoch_time
        num_epochs = num_epochs + 1

        logger.info('[Epoch %d] time cost: %f' % (epoch, epoch_time))
        if summary_writer:
            summary_writer.add_scalar("training/epoch", epoch, global_step=global_step)
            summary_writer.add_scalar("training/epoch-time", epoch_time, global_step=global_step)

        # train
        name, acc = metric.get()
        log_metrics("training", name, acc, epoch, summary_writer, global_step)

        # test
        name, val_acc = test(ctx, val_data, batch_fn, opt.test_run)
        log_metrics("validation", name, val_acc, epoch, summary_writer, global_step)

        if opt.interrupt_at is not None and epoch + 1 == opt.interrupt_at:
            logging.info("[Epoch %d] Interrupting run now because 'interrupt-at' was set to %d..." %
                         (epoch, opt.interrupt_at))
            save_checkpoint(trainer, epoch, val_acc[0], best_acc, force_save=True)
            sys.exit(3)

        # save model if meet requirements
        save_checkpoint(trainer, epoch, val_acc[0], best_acc)
        best_acc = max(best_acc, val_acc[0])
```  

epoch开始调整lr，重置dataset（合理，这里用的是自己压缩成二进制的数据，需要自行解码，可能不能直接用pytorch的dataset，所以需要自己reset dataset的指针到头部），**重置metric**（~~这个是干什么的？为什么要重置metric？~~ A：metric应该是accuracy，每个epoch开始重新计算accuracy应该也挺有道理，不知道**有没有参考价值**？）。  
在batch里，先获取当前的mini batch，使用`with autograd.record()`创建用于求导的计算图（这个用法是MXNet中独有的，辨析请见[社区issue](https://discuss.gluon.ai/t/topic/15381)，作用是“引入record在每次构建网络，或者计算BN之类的层，可以不用手动指定是train或test，默认是inference的情况下开箱即用还是挺方便的。需要计算梯度的时候把forward代码放在record作用的代码块里就好。”），forward一次求output，根据output和label求loss，再backward求导，`step`一次更新参数，计算metric（accuracy）。后面就是打印log存模型之类的操作。  

**简单总结**  
在epoch开始的时候需要：  
* 更改lr  

在epoch中（对于一个minibatch而言）：  
* 获取新batch  
* forward计算output，计算loss，计算metric，根据loss计算梯度，更新参数。  











