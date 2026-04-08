# 山寨币/Meme SOP 极速排雷与动能评分

## 核心流程

```
步骤零：接收信息（Ticker + Chain + 合约地址）
    ↓
步骤一：一票否决排雷（Kill Switch）
    ↓ 通过 → 步骤二：识别资产属性 → 步骤三：打分
    ↓ 否决 → 输出🔴极度高危，终止
    ↓
步骤四：输出信号与投研建议
```

## 评分结构（满分100分）

| 模块 | 权重 | 说明 |
|------|------|------|
| 模块一：全局Beta | 20分 | BTC.D + TOTAL3大盘资金溢出 |
| 模块二A：常规模型 | 80分 | 适用流通率15-80%的叙事币/VC币 |
| 模块二B：高流通/Meme | 80分 | 适用流通率>90%的Meme/土狗 |

## 信号阈值（v1.1）

| 分数 | 信号 | 操作建议 |
|------|------|---------|
| **≥75分** | 🟢 强烈建议买入/建仓 | 筹码结构极佳，聪明钱流入+叙事爆发，执行现货或合约右侧建仓 |
| **55-74分** | ⚪ 底仓观望/等待突破 | 有一定亮点但结构存在瑕疵，可建观察仓跟踪 |
| **41-54分** | ⚠️ 谨慎观望 | 缺乏明确动能催化，等待突破确认后再操作 |
| **≤40分** | 🔴 规避/减仓/潜在做空 | 动能衰竭或结构破坏，建议清仓或转合约做空池 |

> 🚨 **排雷优先**：任何打分前必须先通过4条红线
> **核心扣分项触发**：无论分数，立即降级为🔴

## 4条红线（Kill Switch）

| 红线 | 触发条件 | 工具 |
|------|---------|------|
| 🔴 老鼠仓/Rug | Bundle>30%；历史Rug率>10%；或有Rug历史 | `okx-dex-trenches` |
| 🔴 流动性枯竭 | 流动性<$50K；或滑点>3% | `okx-dex-token` |
| 🔴 蜜罐貔貅 | 合约未开源/隐藏Mint/黑名单/无法卖出 | GoPlus / OKX Security |
| 🔴 宏观熔断 | BTC日线下跌通道；或VIX>25 | TradingView |

## 使用方法

```bash
# 直接运行（需通过Python API调用完整参数）
python3 scripts/score.py

# 示例：PEPE打分
python3 -c "
from scripts.score import score_altcoin, print_report
total, result = score_altcoin(
    ticker='PEPE', chain='Ethereum',
    contract_address='0x6982508145454Ce325dDbE47a25d4ec3d2311933',
    mc=3.5e9, fdv=3.8e9,
    btc_d_signal='down', total3_signal='breakout',
    holder_ratio=0.12, smart_money='buy',
    volume_burst=True, social_heat='爆发',
    is_open_source=True, can_sell=True, vix=18,
)
print_report(result)
"
```

## OKX工具速查

```bash
export OKX_API_KEY="your_key"
export OKX_SECRET_KEY="your_secret"
export OKX_PASSPHRASE="your_passphrase"

# 开发者Rug历史
onchainos memepump token-dev-info --chain bsc --address <CA>

# 持币分布
onchainos token holders --chain bsc --address <CA>

# 安全扫描（蜜罐/黑名单）
onchainos security token-scan --chain bsc --address <CA>

# Smart Money信号
onchainos signal list --chain bsc
```

## 目录结构

```
altcoin-meme-sop/
├── SKILL.md               ← Skill主文件
├── scripts/score.py       ← 评分脚本（含OKX实测数据）
└── references/sop.md     ← SOP完整参考手册
```

## License

MIT
