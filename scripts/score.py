#!/usr/bin/env python3
"""
山寨币/Meme SOP 极速排雷与动能评分系统
参考：小龙虾执行手册 v1.0
"""

import sys
from datetime import datetime

# ─────────────────────────────────────────────
#  步骤一：排雷（Kill Switch）
# ─────────────────────────────────────────────

KILL_SWITCH_REASONS = []


def check_rug_history(has_rug, bundle_ratio=None, dev_reputation="unknown"):
    """
    红线1：老鼠仓与发币者声誉
    """
    if has_rug or dev_reputation == "rug":
        KILL_SWITCH_REASONS.append("🚨 红线1：开发者有Rug历史")
        return True
    if bundle_ratio is not None and bundle_ratio > 0.3:
        KILL_SWITCH_REASONS.append(f"🚨 红线1：Bundle Detection异常（{bundle_ratio:.1%}），疑似老鼠仓")
        return True
    return False


def check_liquidity(liquidity_usd=None, slippage_pct=None, min_liquidity=50000, max_slippage=3.0):
    """
    红线2：流动性枯竭
    """
    if liquidity_usd is not None and liquidity_usd < min_liquidity:
        KILL_SWITCH_REASONS.append(f"🚨 红线2：流动性极浅（${liquidity_usd:,.0f} < ${min_liquidity:,}）")
        return True
    if slippage_pct is not None and slippage_pct > max_slippage:
        KILL_SWITCH_REASONS.append(f"🚨 红线2：滑点过高（{slippage_pct:.2f}% > {max_slippage}%）")
        return True
    return False


def check_honeypot(
    is_open_source=True,
    has_hidden_mint=False,
    has_blacklist=False,
    can_sell=True
):
    """
    红线3：蜜罐貔貅
    """
    reasons = []
    if not is_open_source:
        reasons.append("合约未开源")
    if has_hidden_mint:
        reasons.append("含隐藏Mint权限")
    if has_blacklist:
        reasons.append("含黑名单功能")
    if not can_sell:
        reasons.append("无法卖出（疑似蜜罐）")
    if reasons:
        KILL_SWITCH_REASONS.append("🚨 红线3：" + "、".join(reasons))
        return True
    return False


def check_macro_crash(btc_dxy_trend="neutral", vix=None, btc_in_downtrend=False):
    """
    红线4：宏观环境熔断
    """
    if btc_in_downtrend:
        KILL_SWITCH_REASONS.append("🚨 红线4：BTC处于明确日线级别下跌通道")
        return True
    if vix is not None and vix > 25:
        KILL_SWITCH_REASONS.append(f"🚨 红线4：VIX={vix}>25，市场恐慌，山寨无独立行情")
        return True
    return False


def run_kill_switch(
    # 红线1
    has_rug=False,
    bundle_ratio=None,
    dev_reputation="unknown",
    # 红线2
    liquidity_usd=None,
    slippage_pct=None,
    # 红线3
    is_open_source=True,
    has_hidden_mint=False,
    has_blacklist=False,
    can_sell=True,
    # 红线4
    btc_in_downtrend=False,
    vix=None,
):
    """
    执行全部排雷检查。
    返回：(是否通过, 触发原因列表)
    """
    KILL_SWITCH_REASONS.clear()
    kills = []

    if check_rug_history(has_rug, bundle_ratio, dev_reputation):
        kills.append("老鼠仓/Rug")
    if check_liquidity(liquidity_usd, slippage_pct):
        kills.append("流动性枯竭")
    if check_honeypot(is_open_source, has_hidden_mint, has_blacklist, can_sell):
        kills.append("蜜罐貔貅")
    if check_macro_crash(None, vix, btc_in_downtrend):
        kills.append("宏观熔断")

    passed = len(kills) == 0
    return passed, list(KILL_SWITCH_REASONS)


# ─────────────────────────────────────────────
#  步骤二：模型路由
# ─────────────────────────────────────────────

def get_model(mc=None, fdv=None):
    """
    根据流通率路由模型。
    流通率 = MC / FDV
    模型A：15%-80%（常规模型）
    模型B：>90%（高流通/Meme）
    """
    if mc is not None and fdv is not None and fdv > 0:
        circ_rate = mc / fdv
        if circ_rate > 0.90:
            return "B", circ_rate
        elif circ_rate >= 0.15:
            return "A", circ_rate
        else:
            return "C", circ_rate  # <15%，数据可靠性低
    return None, None


# ─────────────────────────────────────────────
#  步骤三：模块一评分（20分，A/B通用）
# ─────────────────────────────────────────────

def score_module1(btc_d_signal="neutral", total3_signal="neutral"):
    """
    BTC.D（10分）+ TOTAL3（10分）
    """
    btc_score = {"down": 10, "neutral": 0, "up": -10}.get(btc_d_signal, 0)
    total3_score = {"breakout": 10, "neutral": 0, "down": 0}.get(total3_signal, 0)
    return btc_score + total3_score, btc_score, total3_score


# ─────────────────────────────────────────────
#  步骤三：模块二A - 常规模型（80分）
# ─────────────────────────────────────────────

def score_model_a(
    unlock_status="normal",      # safe(15) / normal(5) / cliff(-15)
    cex_flow="neutral",          # outflow(15) / neutral(0) / huge_inflow(-10)
    micro_structure="neutral",   # healthy(10) / normal(0) / overheated(-10)
    event_driver=0,              # 20 / 10 / 0
    sector_hot=False,            # True(+10) / False(0)
    fundamentals=False,          # True(+10) / False(0)
):
    s = 0
    detail = []

    # 解锁抛压
    if unlock_status == "safe":
        s += 15; detail.append("无大额解锁+15")
    elif unlock_status == "cliff":
        s -= 15; detail.append("大额悬崖解锁-15")
    else:
        s += 5; detail.append("常规线性解锁+5")

    # CEX资金流
    if cex_flow == "outflow":
        s += 15; detail.append("CEX净流出+15")
    elif cex_flow == "huge_inflow":
        s -= 10; detail.append("CEX巨额流入-10")
    else:
        detail.append("CEX进出平衡0")

    # 微观结构
    if micro_structure == "healthy":
        s += 10; detail.append("OI上升+费率健康+10")
    elif micro_structure == "overheated":
        s -= 10; detail.append("费率过热-10")
    else:
        detail.append("微观结构正常0")

    # 事件驱动
    s += event_driver
    if event_driver == 20: detail.append("重大利好+20")
    elif event_driver == 10: detail.append("次级利好+10")

    # 赛道资金
    if sector_hot:
        s += 10; detail.append("热门赛道+10")

    # 基本面
    if fundamentals:
        s += 10; detail.append("TVL/交互量异动+10")

    return s, detail


# ─────────────────────────────────────────────
#  步骤三：模块二B - 高流通/Meme模型（80分）
# ─────────────────────────────────────────────

def score_model_b(
    holder_ratio=None,            # <15%(15) / 15-30%(0) / >30%(-15)
    smart_money="neutral",       # buy(20) / neutral(0) / dump(-20)
    volume_burst=False,           # True(+15) / False(0)
    social_heat=0,               # 20/10/0
    micro_structure="neutral",    # healthy(10) / normal(0) / overheated(-10)
):
    s = 0
    detail = []

    # 大户控盘度
    if holder_ratio is not None:
        if holder_ratio < 0.15:
            s += 15; detail.append(f"前10大占比{holder_ratio:.1%}<15%控盘低+15")
        elif holder_ratio > 0.30:
            s -= 15; detail.append(f"前10大占比{holder_ratio:.1%}>30%高度控盘-15")
        else:
            detail.append(f"前10大占比{holder_ratio:.1%}中等0")

    # 聪明钱动向
    if smart_money == "buy":
        s += 20; detail.append("Smart Money净买入+20")
    elif smart_money == "dump":
        s -= 20; detail.append("低成本钱包砸盘-20")
    else:
        detail.append("Smart Money无异动0")

    # 链上量价
    if volume_burst:
        s += 15; detail.append("交易量二次爆发+15")

    # 情绪热度
    s += social_heat
    if social_heat == 20: detail.append("社交热度爆发+20")
    elif social_heat == 10: detail.append("社区有热度+10")

    # 微观结构
    if micro_structure == "healthy":
        s += 10; detail.append("OI稳升+费率健康+10")
    elif micro_structure == "overheated":
        s -= 10; detail.append("费率过热-10")

    return s, detail


# ─────────────────────────────────────────────
#  步骤四：汇总信号
# ─────────────────────────────────────────────

def get_signal(total, model, core_penalty_triggered=False):
    if total >= 75 and not core_penalty_triggered:
        return "🟢 强烈建议买入/建仓", "筹码结构极佳，聪明钱流入+叙事爆发，高胜率做多标准"
    elif total >= 55:
        return "⚪ 底仓观望/等待突破", "有一定叙事亮点但结构存在瑕疵，可建观察仓跟踪"
    else:
        return "🔴 规避/减仓/潜在做空", "动能衰竭抛压沉重，建议清仓或转合约做空观察池"


# ─────────────────────────────────────────────
#  主评分函数
# ─────────────────────────────────────────────

def score_altcoin(
    # ── 必要信息 ──
    ticker=None,
    chain=None,
    contract_address=None,
    mc=None,        # 流通市值
    fdv=None,        # 全流通市值

    # ── 排雷参数 ──
    has_rug=False,
    bundle_ratio=None,
    dev_reputation="unknown",
    liquidity_usd=None,
    slippage_pct=None,
    is_open_source=True,
    has_hidden_mint=False,
    has_blacklist=False,
    can_sell=True,
    btc_in_downtrend=False,
    vix=None,

    # ── 模块一（大盘Beta，20分）──
    btc_d_signal="neutral",   # down / neutral / up
    total3_signal="neutral",   # breakout / neutral / down

    # ── 模块二A（常规模型，80分）──
    unlock_status="normal",   # safe / normal / cliff
    cex_flow="neutral",       # outflow / neutral / huge_inflow
    micro_structure_a="neutral",
    event_driver=0,           # 20 / 10 / 0
    sector_hot=False,
    fundamentals=False,

    # ── 模块二B（Meme模型，80分）──
    holder_ratio=None,
    smart_money="neutral",
    volume_burst=False,
    social_heat=0,
    micro_structure_b="neutral",
):
    """
    山寨币/Meme 综合评分

    示例用法：
    score_altcoin(
        ticker="PEPE",
        chain="Ethereum",
        contract_address="0x6982508145454Ce325dDbE47a25d4ec3d2311933",
        mc=3.5e9, fdv=3.8e9,  # 流通率 ~92%，用模型B

        # 排雷
        is_open_source=True,
        can_sell=True,
        vix=18,

        # 模块一
        btc_d_signal="down",
        total3_signal="breakout",

        # 模块二B
        holder_ratio=0.12,
        smart_money="buy",
        volume_burst=True,
        social_heat=20,
    )
    """

    # ── 步骤一：排雷 ──
    kill_passed, kill_reasons = run_kill_switch(
        has_rug=has_rug,
        bundle_ratio=bundle_ratio,
        dev_reputation=dev_reputation,
        liquidity_usd=liquidity_usd,
        slippage_pct=slippage_pct,
        is_open_source=is_open_source,
        has_hidden_mint=has_hidden_mint,
        has_blacklist=has_blacklist,
        can_sell=can_sell,
        btc_in_downtrend=btc_in_downtrend,
        vix=vix,
    )

    # ── 步骤二：模型路由 ──
    model, circ_rate = get_model(mc, fdv)

    # ── 步骤三：打分 ──
    m1_total, btc_d_score, total3_score = score_module1(btc_d_signal, total3_signal)

    if model == "A":
        m2_total, m2_detail = score_model_a(
            unlock_status=unlock_status,
            cex_flow=cex_flow,
            micro_structure=micro_structure_a,
            event_driver=event_driver,
            sector_hot=sector_hot,
            fundamentals=fundamentals,
        )
        model_label = "A（常规模型）"
    elif model == "B":
        m2_total, m2_detail = score_model_b(
            holder_ratio=holder_ratio,
            smart_money=smart_money,
            volume_burst=volume_burst,
            social_heat=social_heat,
            micro_structure=micro_structure_b,
        )
        model_label = "B（Meme/高流通）"
    else:
        m2_total = 0
        m2_detail = ["数据不足，无法评分"]
        model_label = f"未知（流通率{circ_rate:.1%}）" if circ_rate else "未知"

    total = m1_total + m2_total

    # ── 核心扣分项检测 ──
    core_penalty = (
        (model == "A" and unlock_status == "cliff") or
        (model == "A" and cex_flow == "huge_inflow") or
        (model == "B" and holder_ratio is not None and holder_ratio > 0.30) or
        (model == "B" and smart_money == "dump")
    )

    signal, signal_desc = get_signal(total, model, core_penalty)

    # ── 构建结果 ──
    result = {
        "代币信息": {
            "ticker": ticker,
            "chain": chain,
            "合约地址": contract_address,
            "流通市值MC": f"${mc/1e9:.2f}B" if mc else "N/A",
            "全流通FDV": f"${fdv/1e9:.2f}B" if fdv else "N/A",
            "流通率": f"{circ_rate:.1%}" if circ_rate else "N/A",
            "使用模型": model_label,
        },
        "排雷结果": {
            "通过": kill_passed,
            "触发红线": kill_reasons if not kill_passed else [],
        },
        "模块一_大盘Beta（20分）": {
            "小计": m1_total,
            "BTC.D": {"得分": btc_d_score, "说明": f"BTC.D信号={btc_d_signal}"},
            "TOTAL3": {"得分": total3_score, "说明": f"TOTAL3信号={total3_signal}"},
        },
        "模块二_专属因子": {
            "小计": m2_total,
            "详情": m2_detail,
        },
        "总分": total,
        "信号": signal,
        "信号说明": signal_desc,
        "核心扣分项": core_penalty,
    }

    return total, result


def print_report(result):
    info = result["代币信息"]
    print(f"【山寨币/Meme SOP评分】{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 55)
    print(f"代币：{info.get('ticker','N/A')} | {info.get('chain','N/A')}")
    ca = info.get('合约地址')
    print(f"合约：{ca[:20]}..." if ca else "合约：N/A")
    print(f"MC：{info.get('流通市值MC','N/A')} | FDV：{info.get('全流通FDV','N/A')} | 流通率：{info.get('流通率','N/A')}")
    print(f"模型：{info['使用模型']}")
    print()

    # 排雷
    kill = result["排雷结果"]
    if not kill["通过"]:
        print("🛑 排雷结果：❌ 未通过，触发红线！")
        for r in kill["触发红线"]:
            print(f"   {r}")
        print()
        print("=" * 55)
        print("🔴 极度高危 / 拒绝买入 — 终止评估")
        return
    else:
        print("✅ 排雷结果：全部通过，进入打分流程")
        print()

    m1 = result["模块一_大盘Beta（20分）"]
    m2 = result["模块二_专属因子"]

    print(f"【总分：{result['总分']}分】→ {result['信号']}")
    print(f"说明：{result['信号说明']}")
    if result["核心扣分项"]:
        print("⚠️ 核心扣分项触发：存在大额解锁/大户砸盘等致命瑕疵")
    print()

    print(f"模块一（大盘Beta）：{m1['小计']}分")
    print(f"  BTC.D： {m1['BTC.D']['得分']:+d}分  {m1['BTC.D']['说明']}")
    print(f"  TOTAL3：{m1['TOTAL3']['得分']:+d}分  {m1['TOTAL3']['说明']}")
    print()

    print(f"模块二（专属因子，{info['使用模型']}）：{m2['小计']}分")
    for d in m2["详情"]:
        print(f"  • {d}")
    print()

    print("─── 评分阈值参考 ───")
    print(f"  🟢 ≥75分：强烈买入/建仓  （当前{result['总分']}分 {'✅' if result['总分']>=75 else '❌'}）")
    print(f"  ⚪ 55-74：观望/等待突破  {'✅' if 55<=result['总分']<=74 else ''}")
    print(f"  🔴 ≤40分：规避/减仓     {'✅' if result['总分']<=40 else ''}")


def main():
    args = sys.argv[1:]

    if len(args) >= 1 and args[0] == "--help":
        print("""
山寨币/Meme SOP 评分工具

用法：
  python3 score.py [ticker] [chain] [model] [选项...]

参数：
  ticker        代币名称（如 PEPE）
  chain         公链（如 Ethereum）
  model         模型 A 或 B

示例：
  # Meme币（模型B）
  python3 score.py PEPE Ethereum B \\
    --btc_down --total3_breakout \\
    --holder_ratio 0.12 \\
    --smart_money buy \\
    --volume_burst \\
    --social_heat 20

  # 常叙事币（模型A）
  python3 score.py ARB Ethereum A \\
    --btc_down --total3_neutral \\
    --unlock safe \\
    --cex_flow outflow \\
    --event_driver 20 \\
    --sector_hot \\
    --vix 18
""")
        return

    print("⚠️  请使用 Python API 调用 score_altcoin() 函数进行评分")
    print("    完整参数列表请查看 score.py 源码或 SOP 参考文档")


if __name__ == "__main__":
    main()
