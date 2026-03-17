# VeriGuard: Enhancing LLM Agent Safety via Verified Code Generation  

2026/3/17

很好，这一部分已经进入这篇  的核心方法了。我帮你**按“读论文 + 建立直觉”的方式继续导读**，重点讲清楚它到底在做什么，以及和你做具身智能/agent系统有什么关系。

---

# 🌟 一、这篇文章的核心思想（一句话版）

👉 **VeriGuard = 用“形式化验证”给LLM Agent加一个“可证明安全”的外壳**

不是：

* ❌ 事后拦截（guardrail / filter）

而是：

* ✅ **生成时就保证正确（correct-by-construction）**
* ✅ **执行前再严格检查（runtime enforcement）**

---

# 🧠 二、方法总览（论文 Figure 1）

论文第 **第4页 Figure 1** 给了一个非常关键的结构图（你一定要理解这个）：

## 整体分两阶段：

### 🔵 阶段1：Policy Generation（离线）

👉 生成一个“安全策略函数 + 数学约束”，并证明它是对的

流程是：

```
自然语言安全需求
        ↓
LLM生成：
   - policy code（代码）
   - constraints（逻辑约束）
        ↓
三步 refinement：
   1. Validation（语义对齐）
   2. Testing（单元测试）
   3. Formal Verification（形式化证明）
        ↓
✅ Verified Policy（经过证明的安全策略）
```

---

### 🟢 阶段2：Policy Enforcement（在线）

👉 在 agent 执行动作前进行检查

```
Agent要执行动作
        ↓
提取参数（LLM）
        ↓
执行 policy 函数
        ↓
✔ 合法 → 执行
❌ 不合法 → 阻止 / 重规划
```

---

# 🧩 三、核心建模（非常关键）

论文第 **4页 Task Definition** 这段非常重要：

---

## 1️⃣ Policy Generation 的形式化定义

给定：

* 自然语言请求：
  👉 ( r )（比如：不能泄露隐私数据）

* agent描述：
  👉 ( \mathcal{S} )（工具、输入输出、环境）

---

生成：

* policy函数：
  👉 ( p )

* 约束集合：
  👉 ( C = {c_1, c_2, ..., c_n} )

---

目标：

[
p \models C
]

👉 含义是：

> policy代码必须满足所有约束（每一条安全规则都成立）

---

## ⚠️ 这一步的本质

👉 把“自然语言安全要求”变成：

* 可执行代码（policy）
* 可验证逻辑（constraints）

这是**论文最核心创新之一**

---

## 2️⃣ Policy Enforcement

目标：

> 在运行时，让 agent 的行为始终符合 policy

优化目标：

* ↓ 减少违规（attack surface）
* ↑ 保持任务完成率（utility）

---

# 🔁 四、Refinement Loop（论文最精华部分）

论文第 **5–6页**

这是整个方法的灵魂👇

---

## 三阶段循环：

### ① Validation（语义对齐）

👉 解决问题：

* 用户说的不清楚
* 逻辑有歧义

输出：

* 明确的 requirements ( R )
* 假设 ( A )

---

👉 本质：

> NLP → 精确定义（像 requirement engineering）

---

### ② Testing（功能验证）

👉 自动生成 test cases：

* 正常情况
* 边界情况
* 错误输入

---

👉 本质：

> 软件工程里的 unit test

---

### ③ Formal Verification（形式化验证）

这是最关键的👇

---

使用 Hoare Logic：

[
{C_{pre}} \ p \ {C_{post}}
]

意思是：

> 如果前置条件成立
> 那执行 policy 后
> 后置条件一定成立

---

👉 如果不成立：

* verifier 给 counterexample
* LLM 再修代码

---

## 🔁 最终形成闭环：

```
生成 → 验证失败 → 修正 → 再验证
```

直到：

✅ 证明成立

---

# 🔥 五、和你研究方向的关系（非常重要）

你现在在做：

> 多智能体 + 具身智能 + 任务验证

这篇论文直接对应你提到的“缺失模块”👇

---

## 🧠 你之前的观察：

> agent系统没有“验证模块”

✔ 这篇论文就是在补这个：

| 模块 | 传统agent | VeriGuard |
| -- | ------- | --------- |
| 规划 | ✔       | ✔         |
| 执行 | ✔       | ✔         |
| 验证 | ❌（弱）    | ✅（形式化）    |

---

## 🔥 更深一层（关键 insight）

VeriGuard其实做了三件事：

---

### ① 把“安全”变成可验证逻辑

👉 从：

* “不要泄露隐私”（模糊）

变成：

* IF access_sensitive_data → DENY

---

### ② 把“agent行为”变成程序

👉 agent ≈ program

---

### ③ 引入 formal methods

👉 类似：

* 编译器验证
* 程序证明

---

# ⚖️ 六、实验结论（你要抓的重点）

## 📊 Table 1（第8页）

结果：

👉 VeriGuard：

* ASR（攻击成功率）≈ 0
* TSR（任务成功率）↑

---

👉 结论：

> 不只是安全，还保持性能

---

## 📊 Table 2（第9页）

👉 在 access control 场景：

* Accuracy = 100%
* Recall = 100%

---

👉 论文强调：

> Recall 比 Precision 更重要（安全系统）

---

# 🧪 七、策略设计（很有工程价值）

论文第6页讲了4种 enforcement：

| 方法  | 特点         |
| --- | ---------- |
| TT  | 直接终止       |
| AB  | 阻止动作       |
| TEH | 阻止工具调用     |
| CRP | 让agent重新规划 |

---

## 🧠 最优组合：

👉 **CRP + TEH**

（第10页结论）

---

# ⚠️ 八、局限性（你一定要看）

论文第11页：

---

## 1️⃣ 依赖 LLM 生成约束

👉 可能错

→ verification正确 ≠ 需求正确

---

## 2️⃣ verifier能力有限（Nagini）

👉 表达能力有限

---

## 3️⃣ policy是静态的

👉 对动态攻击不够强

---

# 🧭 九、给你的研究启发（重点）

结合你在做的方向，我给你几个非常有价值的研究点：

---

## 💡 1. 多智能体共享 memory + verification

👉 你可以做：

* memory consistency verification
* 多agent状态约束

---

## 💡 2. LTL + VeriGuard结合（非常契合你前面问的）

👉 用：

* LTL → 表达任务逻辑
* VeriGuard → 验证执行

👉 形成：

> **时序逻辑 + 程序验证 = 强安全 agent**

---

## 💡 3. 任务完成验证（你提到的痛点）

👉 可以做：

* post-condition verification
* goal satisfaction checking

---

## 💡 4. 在线验证 vs 离线验证

👉 VeriGuard：

* heavy offline
* light online

你可以研究：

👉 更动态的 verification

---

# ✅ 总结一句话

👉 VeriGuard 的本质是：

> **把 agent safety 从“经验规则”升级为“可证明正确”的程序验证问题**

---

如果你愿意，我可以下一步帮你做更深入的：

✅ 把 VeriGuard 和你做的“多智能体共享记忆”结合起来
✅ 或帮你设计一个“具身智能 + 验证模块”的完整架构（很适合写论文）
