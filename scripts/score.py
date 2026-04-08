#!/usr/bin/env python3
"""
山寨币/Meme SOP 极速排雷与动能评分系统
参考：小龙虾执行手册 v1.0（完整版）
"""

import sys
from datetime import datetime

# ─────────────────────────────────────────────
#  步骤一：排雷（Kill Switch）
# ─────────────────────────────────────────────

KILL_SWITCH_REASONS = []


def check_rug_history(
    has_rug=False,
    bundle_ratio=None,
    dev_reputation="unknown",
    rug_count=None,       # OKX trenches: 开发者历史Rug次数
    total_tokens=None,    # OKX trenches: 开发者历史总代币数
):
    """
    红线1：老鼠仓与发币者声誉
    触发条件（满足任一）：
    - has_rug = True
    - dev_reputation = "rug"
    - bundle_ratio > 30%
    - dev_reputation = "low" 且 bundle_ratio > 15%
    - 开发者历史 Rug率 > 10%（Rug数/总代币数）
    """
    kills = []

    if has_rug or dev_reputation == "rug":
        kills.append("开发者有Rug历史（直接标记）")
        KILL_SWITCH_REASONS.append("🚨 红线1：开发者有Rug历史（直接标记）")
        return True

    if bundle_ratio is not None and bundle_ratio > 0.30:
        kills.append(f"Bundle Detection异常（{bundle_ratio:.1%}）")
        KILL_SWITCH_REASONS.append(f"🚨 红线1：Bundle Detection异常（{bundle_ratio:.1%}），疑似老鼠仓")
        return True

    # OKX trenches 深度检查
    if rug_count is not None and total_tokens is not None and total_tokens > 10:
        rug_rate = rug_count / total_tokens
        if rug_rate > 0.10:  # Rug率>10%
            kills.append(f"Rug率{rug_rate:.1%}（{rug_count}次/{total_tokens}个代币）")
            KILL_SWITCH_REASONS.append(f"🚨 红线1：开发者历史Rug率{rug_rate:.1%}（{rug_count}次Rug/{total_tokens}个代币），惯犯")
            return True

    if dev_reputation == "low" and bundle_ratio is not None and bundle_ratio > 0.15:
        kills.append(f"开发者声誉差+Bundle偏高{bundle_ratio:.1%}")
        KILL_SWITCH_REASONS.append(f"🚨 红线1：开发者声誉差+Bundle Detection {bundle_ratio:.1%}")
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
    can_sell=True,
    transfer_pausable=False,
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
    if transfer_pausable:
        reasons.append("转账可被暂停（风险）")
    if reasons:
        KILL_SWITCH_REASONS.append("🚨 红线3：" + "、".join(reasons))
        return True
    return False


def check_macro_crash(vix=None, btc_in_downtrend=False):
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
    rug_count=None,
    total_tokens=None,
    # 红线2
    liquidity_usd=None,
    slippage_pct=None,
    # 红线3
    is_open_source=True,
    has_hidden_mint=False,
    has_blacklist=False,
    can_sell=True,
    transfer_pausable=False,
    # 红线4
    btc_in_downtrend=False,
    vix=None,
):
    """
    执行全部排雷检查。
    返回：(是否通过, 触发原因列表)
    """
    KILL_SWITCH_REASONS.clear()

    killed = (
        check_rug_history(has_rug, bundle_ratio, dev_reputation, rug_count, total_tokens) or
        check_liquidity(liquidity_usd, slippage_pct) or
        check_honeypot(is_open_source, has_hidden_mint, has_blacklist, can_sell, transfer_pausable) or
        check_macro_crash(vix, btc_in_downtrend)
    )

    return not killed, list(KILL_SWITCH_REASONS)


# ─────────────────────────────────────────────
#  步骤二：模型路由
# ─────────────────────────────────────────────

def get_model(mc=None, fdv=None):
    """
    流通率 = MC / FDV
    模型A：15%-80%（强叙事币/VC币）
    模型B：>90%（纯土狗/Meme）
    <15%：数据可靠性低，谨慎评分
    """
    if mc is not None and fdv is not None and fdv > 0:
        circ_rate = mc / fdv
        if circ_rate > 0.90:
            return "B", circ_rate
        elif circ_rate >= 0.15:
            return "A", circ_rate
        else:
            return "C", circ_rate
    return None, None


# ─────────────────────────────────────────────
#  步骤三：模块一评分（20分，A/B通用）
# ─────────────────────────────────────────────

def score_module1(btc_d_signal="neutral", total3_signal="neutral"):
    """
    BTC.D（10分）+ TOTAL3（10分）
    BTC.D下跌=+10（资金分流山寨）；TOTAL3突破=+10（山寨行情）
    """
    btc_score = {"down": 10, "neutral": 0, "up": -10}.get(btc_d_signal, 0)
    total3_labels = {
        "breakout": ("突破阻力位/上升通道", 10),
        "neutral": ("震荡", 0),
        "down": ("震荡下跌", 0),
    }
    total3_label, total3_score = total3_labels.get(total3_signal, ("未知", 0))
    return btc_score + total3_score, btc_score, total3_score, total3_label


# ─────────────────────────────────────────────
#  步骤三：模块二A - 常规模型（80分）
# ─────────────────────────────────────────────

def score_model_a(
    # 解锁抛压（+15 / +5 / -15）
    # +15: 未来30天无大额解锁；+5: 常规线性；-15: 未来14天大额悬崖解锁
    unlock_ahead_days=None,   # 距离下次大额解锁天数
    unlock_amount_usd=None,  # 解锁金额（美元）
    # CEX资金流（+15 / 0 / -10）
    cex_flow="neutral",       # outflow / neutral / huge_inflow
    # 微观结构（+10 / 0 / -10）
    oi_trend="neutral",       # rising / neutral / falling
    funding_rate=None,        # 资金费率（小数，如 0.001 = 0.1%）
    # 事件驱动（+20 / +10 / 0）
    event_impact="none",     # major / minor / none
    # 赛道资金（+10 / 0）
    sector_hot=False,
    # 基本面（+10 / 0）
    tvl_growth_7d=None,     # TVL 7天增长率（小数，如 0.20 = 20%）
    # CEX上市状态（辅助参考）
    on_binance=False,
    on_okx=False,
):
    """
    模型A：常规模型（流通率15-80%）
    评估：解锁/CEX/微观结构/事件/赛道/基本面
    """
    s = 0
    detail = []

    # ① 解锁抛压
    if unlock_ahead_days is not None:
        if unlock_ahead_days > 30:
            s += 15
            detail.append(f"未来{unlock_ahead_days}天无大额解锁+15")
        elif unlock_ahead_days <= 14:
            s -= 15
            detail.append(f"⚠️未来{unlock_ahead_days}天大额悬崖解锁-15（砸盘预警）")
        else:
            s += 5
            detail.append(f"{unlock_ahead_days}天后解锁，常规线性+5")
    else:
        detail.append("解锁数据：未提供（默认+5）")
        s += 5

    # ② CEX资金流（Binance/Nansen）
    if cex_flow == "outflow":
        s += 15
        detail.append("CEX净流出（提币建仓）+15")
    elif cex_flow == "huge_inflow":
        s -= 10
        detail.append("⚠️CEX巨额净流入（疑似项目方砸盘）-10")
    else:
        detail.append("CEX进出平衡0")

    # ③ 微观结构（OI + 资金费率）
    if oi_trend == "rising" and funding_rate is not None and funding_rate <= 0.001:
        s += 10
        detail.append("OI稳升+费率健康(≤0.1%)+10")
    elif funding_rate is not None and funding_rate > 0.001:
        s -= 10
        detail.append(f"⚠️费率过热({funding_rate:.3%})>-10")
    else:
        detail.append("微观结构正常0")

    # ④ 事件驱动
    if event_impact == "major":
        s += 20
        detail.append("未来1-4周重大主网/合作利好+20")
    elif event_impact == "minor":
        s += 10
        detail.append("次级利好+10")
    else:
        detail.append("无明确事件0")

    # ⑤ 赛道资金（okx-dex-market热点榜）
    if sector_hot:
        s += 10
        detail.append("所属赛道近3天资金净流入前三+10")
    else:
        detail.append("非热门赛道0")

    # ⑥ 基本面（DefiLlama TVL）
    if tvl_growth_7d is not None and tvl_growth_7d > 0.15:
        s += 10
        detail.append(f"TVL 7天异动+{tvl_growth_7d:.0%}+10")
    else:
        detail.append("TVL无异动0")

    return s, detail


# ─────────────────────────────────────────────
#  步骤三：模块二B - 高流通/Meme模型（80分）
# ─────────────────────────────────────────────

def score_model_b(
    # 大户控盘度（+15 / 0 / -15）
    holder_ratio=None,        # 前10大真实个人地址占比
    lp_ratio=None,           # LP池占比（从holder中排除）
    # 聪明钱动向（+20 / 0 / -20）
    smart_money="neutral",   # buy / neutral / dump
    # 链上量价（+15 / 0）
    volume_burst=False,      # 24-48h量价二次爆发
    volume_change_24h=None,   # 24h成交量变化（小数）
    # 情绪热度（+20 / +10 / 0）
    social_heat="none",      #爆发 / 有热度 / 无
    # 微观结构（+10 / +5 / -10）
    oi_trend="neutral",
    funding_rate=None,
    on_cex=False,            # 是否上了大所合约
):
    """
    模型B：高流通/Meme专属（流通率>90%）
    评估：大户控盘/Smart Money/量价/情绪/微观结构
    """
    s = 0
    detail = []

    # ① 大户控盘度
    if holder_ratio is not None:
        if holder_ratio < 0.15:
            s += 15
            detail.append(f"前10大个人占比{holder_ratio:.1%}<15%且换手充分+15")
        elif holder_ratio > 0.30:
            s -= 15
            detail.append(f"⚠️前10大占比{holder_ratio:.1%}>30%高度控盘-15（极危）")
        else:
            detail.append(f"前10大占比{holder_ratio:.1%}中等0")
    else:
        detail.append("大户数据未提供")

    # ② 聪明钱动向（okx-dex-signal）
    if smart_money == "buy":
        s += 20
        detail.append("Smart Money净买入+20")
    elif smart_money == "dump":
        s -= 20
        detail.append("⚠️低成本早期钱包向LP池砸盘-20（致命）")
    else:
        detail.append("Smart Money无异动0")

    # ③ 链上量价
    if volume_burst:
        s += 15
        detail.append("24-48h量价二次爆发+15")
    elif volume_change_24h is not None and volume_change_24h > 0.50:
        s += 15
        detail.append(f"成交量24h暴涨+{volume_change_24h:.0%}+15")
    elif volume_change_24h is not None and volume_change_24h < -0.30:
        detail.append(f"成交量萎缩{abs(volume_change_24h):.0%}0")
    else:
        detail.append("链上量能无明显变化0")

    # ④ 情绪热度（推特/社交）
    if social_heat == "爆发":
        s += 20
        detail.append("社交提及量爆发（非单一KOL）+20")
    elif social_heat == "有热度":
        s += 10
        detail.append("社区有一定热度+10")
    else:
        detail.append("无人讨论0")

    # ⑤ 微观结构（仅大所合约适用，否则默认+5）
    if on_cex:
        if oi_trend == "rising" and funding_rate is not None and funding_rate <= 0.001:
            s += 10
            detail.append("大所合约OI稳升+费率健康+10")
        elif funding_rate is not None and funding_rate > 0.001:
            s -= 10
            detail.append(f"大所合约费率过热{funding_rate:.3%}-10")
        else:
            detail.append("大所合约微观结构正常0")
    else:
        s += 5
        detail.append("未上大所合约，默认+5分")

    return s, detail


# ─────────────────────────────────────────────
#  步骤四：汇总信号
# ─────────────────────────────────────────────

def get_signal(total, model, core_penalty_triggered=False):
    """
    信号阈值（严格遵循原SOP文档）：
    ≥75分 → 🟢 强烈建议买入
    55-74分 → ⚪ 底仓观望/等待突破
    41-54分 → ⚠️ 谨慎观望（宏观无力/事件未验证）
    ≤40分 → 🔴 规避/减仓/潜在做空

    核心扣分项触发（-15/-20）→ 无论分数，立即降级处理
    """
    if core_penalty_triggered:
        return "🔴 规避/减仓/潜在做空", "触发核心扣分项（大额悬崖解锁/大户砸盘等），结构已破坏，建议立即退出"

    if total >= 75:
        return "🟢 强烈建议买入/建仓", "筹码结构极佳，聪明钱流入+叙事爆发，符合高胜率做多标准"
    elif total >= 55:
        return "⚪ 底仓观望/等待突破", "有一定叙事亮点但结构存在瑕疵，可建观察仓跟踪，不符合重仓标准"
    elif total >= 41:
        return "⚠️ 谨慎观望", "缺乏明确动能催化，建议等待突破确认后再操作"
    else:
        return "🔴 规避/减仓/潜在做空", "总分≤40，动能衰竭或结构破坏，建议清仓或转合约做空观察池"


# ─────────────────────────────────────────────
#  主评分函数
# ─────────────────────────────────────────────

def score_altcoin(
    # ── 必要信息 ──
    ticker=None,
    chain=None,
    contract_address=None,
    mc=None,
    fdv=None,

    # ═══════════════════════════════════════
    #  排雷参数（Kill Switch 4条红线）
    # ═══════════════════════════════════════

    # 红线1：老鼠仓/Rug
    has_rug=False,
    bundle_ratio=None,         # Bundle Detection捆绑占比（>30%触发）
    dev_reputation="unknown",  # unknown / high / low / rug
    rug_count=None,            # OKX trenches: 历史Rug次数
    total_tokens=None,         # OKX trenches: 历史总代币数

    # 红线2：流动性枯竭
    liquidity_usd=None,         # 核心池子美元深度
    slippage_pct=None,         # 模拟大额交易滑点（>3%触发）

    # 红线3：蜜罐貔貅
    is_open_source=True,
    has_hidden_mint=False,
    has_blacklist=False,
    can_sell=True,
    transfer_pausable=False,   # 转账可暂停（额外风险）

    # 红线4：宏观熔断
    btc_in_downtrend=False,
    vix=None,

    # ═══════════════════════════════════════
    #  模块一：大盘Beta（20分，A/B通用）
    # ═══════════════════════════════════════
    btc_d_signal="neutral",    # down / neutral / up
    total3_signal="neutral",   # breakout / neutral / down

    # ═══════════════════════════════════════
    #  模块二A：常规模型（80分）
    #  适用：流通率 15-80%（强叙事币/VC币）
    # ═══════════════════════════════════════
    unlock_ahead_days=None,    # 距离下次大额解锁天数
    unlock_amount_usd=None,    # 解锁金额（美元）
    cex_flow="neutral",        # outflow / neutral / huge_inflow
    oi_trend="neutral",        # rising / neutral / falling
    funding_rate=None,          # 资金费率（小数）
    event_impact="none",       # major / minor / none
    sector_hot=False,          # 赛道热点前三
    tvl_growth_7d=None,       # TVL 7天增长率

    # ═══════════════════════════════════════
    #  模块二B：高流通/Meme（80分）
    #  适用：流通率 >90%
    # ═══════════════════════════════════════
    holder_ratio=None,          # 前10大个人地址占比
    smart_money="neutral",     # buy / neutral / dump
    volume_burst=False,        # 24-48h量价二次爆发
    volume_change_24h=None,    # 24h成交量变化率
    social_heat="none",        # 爆发 / 有热度 / 无
    on_cex=False,              # 是否上大所合约
):
    """
    山寨币/Meme SOP 综合评分

    示例用法（完整参数）：
    score_altcoin(
        ticker="PEPE",
        chain="Ethereum",
        contract_address="0x6982508145454Ce325dDbE47a25d4ec3d2311933",
        mc=3.5e9, fdv=3.8e9,  # 流通率92% → 模型B

        # 排雷
        is_open_source=True, can_sell=True, vix=18,
        liquidity_usd=100e6, slippage_pct=1.5,
        bundle_ratio=0.05, dev_reputation="low",
        rug_count=0, total_tokens=5,

        # 模块一
        btc_d_signal="down",
        total3_signal="breakout",

        # 模块二B
        holder_ratio=0.12,
        smart_money="buy",
        volume_burst=True,
        social_heat="爆发",
        on_cex=True,
    )
    """

    # ── 步骤一：排雷 ──
    kill_passed, kill_reasons = run_kill_switch(
        has_rug=has_rug,
        bundle_ratio=bundle_ratio,
        dev_reputation=dev_reputation,
        rug_count=rug_count,
        total_tokens=total_tokens,
        liquidity_usd=liquidity_usd,
        slippage_pct=slippage_pct,
        is_open_source=is_open_source,
        has_hidden_mint=has_hidden_mint,
        has_blacklist=has_blacklist,
        can_sell=can_sell,
        transfer_pausable=transfer_pausable,
        btc_in_downtrend=btc_in_downtrend,
        vix=vix,
    )

    # ── 步骤二：模型路由 ──
    model, circ_rate = get_model(mc, fdv)

    # ── 步骤三：打分 ──
    m1_total, btc_d_score, total3_score, total3_label = score_module1(btc_d_signal, total3_signal)

    if model == "A":
        m2_total, m2_detail = score_model_a(
            unlock_ahead_days=unlock_ahead_days,
            unlock_amount_usd=unlock_amount_usd,
            cex_flow=cex_flow,
            oi_trend=oi_trend,
            funding_rate=funding_rate,
            event_impact=event_impact,
            sector_hot=sector_hot,
            tvl_growth_7d=tvl_growth_7d,
        )
        model_label = "A（常规模型）"
    elif model == "B":
        m2_total, m2_detail = score_model_b(
            holder_ratio=holder_ratio,
            smart_money=smart_money,
            volume_burst=volume_burst,
            volume_change_24h=volume_change_24h,
            social_heat=social_heat,
            oi_trend=oi_trend,
            funding_rate=funding_rate,
            on_cex=on_cex,
        )
        model_label = "B（Meme/高流通）"
    else:
        m2_total = 0
        m2_detail = ["流通率<15%，数据可靠性低，建议手动评估"]
        model_label = f"未知（流通率{circ_rate:.1%}）" if circ_rate else "未知"

    total = m1_total + m2_total

    # ── 核心扣分项检测 ──
    core_penalty = (
        (model == "A" and unlock_ahead_days is not None and unlock_ahead_days <= 14) or
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
            "BTC.D": {"得分": btc_d_score, "说明": f"BTC.D={btc_d_signal}"},
            "TOTAL3": {"得分": total3_score, "说明": f"TOTAL3={total3_signal}（{total3_label}）"},
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

    kill = result["排雷结果"]
    if not kill["通过"]:
        print("🛑 排雷结果：❌ 未通过，触发红线！")
        for r in kill["触发红线"]:
            print(f"   {r}")
        print()
        print("=" * 55)
        print("🔴 极度高危 / 拒绝买入 — 终止评估")
        return

    print("✅ 排雷结果：全部通过，进入打分流程")
    print()

    m1 = result["模块一_大盘Beta（20分）"]
    m2 = result["模块二_专属因子"]

    print(f"【总分：{result['总分']}分】→ {result['信号']}")
    print(f"说明：{result['信号说明']}")
    if result["核心扣分项"]:
        print("⚠️ 核心扣分项触发：大额悬崖解锁/大户砸盘等致命瑕疵")
    print()

    print(f"模块一（大盘Beta）：{m1['小计']}分")
    print(f"  BTC.D：  {m1['BTC.D']['得分']:+d}分  {m1['BTC.D']['说明']}")
    print(f"  TOTAL3： {m1['TOTAL3']['得分']:+d}分  {m1['TOTAL3']['说明']}")
    print()

    print(f"模块二（专属因子，{info['使用模型']}）：{m2['小计']}分")
    for d in m2["详情"]:
        print(f"  • {d}")
    print()

    print("─── 评分阈值参考 ───")
    total = result['总分']
    cp = result['核心扣分项']
    print(f"  🟢 ≥75分：强烈买入/建仓  （当前{total}分 {'✅' if total>=75 else '❌'}）")
    print(f"  ⚪ 55-74：观望/等待突破  {'✅' if 55<=total<=74 else ''}")
    print(f"  ⚠️ 41-54：谨慎观望       {'✅' if 41<=total<=54 else ''}")
    print(f"  🔴 ≤40分：规避/减仓/做空  {'✅' if total<=40 else ''}")
    if cp:
        print("  ⚠️ 核心扣分项触发：无论分数，立即降级处理")


def main():
    args = sys.argv[1:]
    if len(args) >= 1 and args[0] == "--help":
        print("""
山寨币/Meme SOP 评分工具 v1.1

用法：python3 score.py [ticker] [chain] [model] [参数...]

重要新增参数：
  --unlock_days N    距离下次大额解锁天数（>30:+15；15-30:+5；≤14:-15）
  --cex_flow FLOW    CEX资金流：outflow/neutral/huge_inflow
  --event MAJOR/MINOR/NONE  事件驱动
  --sector_hot       赛道热点前三
  --smart_money BUY/DUMP/NEUTRAL  Smart Money动向
  --social HEAT/BURST/NONE  社交情绪热度
  --holder_ratio N   前10大个人地址占比（小数）

完整参数列表请查看 score.py 源码
""")
        return
    print("⚠️  请使用 Python API 调用 score_altcoin() 函数进行评分")


if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────
#  GoPlus API 安全扫描（红线3辅助）
# ─────────────────────────────────────────────

def check_goplus_security(chain_id, contract_address):
    """
    调用 GoPlus API 获取代币安全信息。
    chain_id: 1=ETH, 56=BSC, 等
    返回: dict 或 None（失败时）
    """
    import urllib.request
    import json
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={contract_address}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            result = data.get("result", {})
            if contract_address.lower() in result:
                return result[contract_address.lower()]
    except Exception:
        pass
    return None


def goplus_to_kill_flags(goplus_data):
    """
    将 GoPlus 数据转换为红线3触发标志。
    返回: (is_honeypot, has_hidden_mint, has_blacklist, can_sell, transfer_pausable)
    """
    if not goplus_data:
        return False, False, False, True, False

    is_honeypot = goplus_data.get("is_honeypot") == "1"
    has_hidden_mint = goplus_data.get("owner_can_mint") == "1"
    has_blacklist = goplus_data.get("is_blacklisted") == "1"
    # sell_tax=0 means sell is possible
    sell_tax = float(goplus_data.get("sell_tax", "0") or "0")
    can_sell = sell_tax < 99  # 超过99%税 = 无法卖出
    transfer_pausable = goplus_data.get("transfer_pausable") == "1"

    return is_honeypot, has_hidden_mint, has_blacklist, can_sell, transfer_pausable

