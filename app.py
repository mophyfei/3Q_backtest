import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
import time  # 引入 time 模組用於模擬進度

# 設定頁面配置
st.set_page_config(page_title="3Q全球贏家 - 專業回測分析", layout="wide", initial_sidebar_state="collapsed")

# 顏色定義（符合台股慣例）
COLOR_PROFIT = "#EF4444"  # 紅色
COLOR_LOSS = "#10B981"  # 綠色
COLOR_PRIMARY = "#4A9EFF"  # 藍色

# 初始化 session state
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'params_confirmed' not in st.session_state:
    st.session_state.params_confirmed = False
if 'mc_triggered' not in st.session_state:
    st.session_state.mc_triggered = False
if 'mc_simulations' not in st.session_state:
    st.session_state.mc_simulations = 100

# 自訂CSS - TradingView風格
st.markdown(f"""
<style>
    .main {{{{
        background: #0B0E14;
    }}}}
    .stApp {{{{
        background: #0B0E14;
    }}}}

    #MainMenu {{{{visibility: hidden;}}}}
    footer {{{{visibility: hidden;}}}}
    header {{{{visibility: hidden;}}}}

    h1 {{{{
        color: {COLOR_PRIMARY} !important;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: 600;
        font-size: 2.8em !important;
        text-align: center;
        margin-bottom: 0 !important;
        text-shadow: 0 0 30px rgba(74, 158, 255, 0.5);
    }}}}

    h2 {{{{
        color: #E8EAED !important;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: 500;
        font-size: 1.4em !important;
        border-left: 4px solid {COLOR_PRIMARY};
        padding-left: 15px;
        margin-top: 40px !important;
        margin-bottom: 20px !important;
    }}}}

    /* 確保所有文字顏色正確 */
    p, span, div, label {{{{
        color: #E8EAED;
    }}}}

    .stFileUploader label {{{{
        color: #9CA3AF !important;
    }}}}

    .metric-card {{{{
        background: linear-gradient(145deg, #1A1D24 0%, #252930 100%);
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 30px rgba(74, 158, 255, 0.15);
        transition: all 0.3s ease;
        height: 100%; /* 確保高度一致 */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}}}

    .metric-card:hover {{{{
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(74, 158, 255, 0.25);
        border-color: rgba(74, 158, 255, 0.5);
    }}}}

    .stMetric label {{{{
        color: #9CA3AF !important;
        font-size: 0.95em !important;
        font-weight: 500 !important;
    }}}}

    .stMetric > div {{{{
        color: #E8EAED !important;
        font-size: 2em !important;
        font-weight: 700 !important;
    }}}}

    /* 確保台股顏色應用在 Metric Card */
    .metric-profit {{{{ color: {COLOR_PROFIT} !important; }}}} /* 賺錢用紅色 */
    .metric-loss {{{{ color: {COLOR_LOSS} !important; }}}}     /* 虧錢用綠色 */


    .stNumberInput > div > div > input {{{{
        background: #1A1D24 !important;
        color: #E8EAED !important;
        border: 1px solid #3A3F4B !important;
        border-radius: 8px !important;
        font-size: 1.05em !important;
    }}}}

    /* 針對 st.radio (計算模式) 調整樣式 */
    div[data-baseweb="radio"] {{{{
        background: #1A1D24; /* 調整背景色 */
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #3A3F4B;
        color: #E8EAED; /* 確保文字顏色可見 */
    }}}}
    .stRadio > label {{{{
        color: #E8EAED !important; /* 確保 Radio 標籤文字顏色可見 */
    }}}}

    .stButton > button {{{{
        background: linear-gradient(145deg, {COLOR_PRIMARY} 0%, #357ABD 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 36px;
        font-weight: 600;
        font-size: 1.05em;
        box-shadow: 0 6px 20px rgba(74, 158, 255, 0.4);
        transition: all 0.3s ease;
    }}}}

    .stButton > button:hover {{{{
        background: linear-gradient(145deg, #6BB6FF 0%, {COLOR_PRIMARY} 100%);
        box-shadow: 0 8px 30px rgba(74, 158, 255, 0.5);
        transform: translateY(-3px);
    }}}}

    .stTabs [data-baseweb="tab-list"] {{{{
        gap: 10px;
        background: #1A1D24;
        border-radius: 10px;
        padding: 6px;
    }}}}

    .stTabs [data-baseweb="tab"] {{{{
        background: transparent;
        color: #9CA3AF;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 1.05em;
    }}}}

    .stTabs [aria-selected="true"] {{{{
        background: {COLOR_PRIMARY};
        color: white;
    }}}}

    hr {{{{
        border-color: #3A3F4B;
        margin: 40px 0;
    }}}}

    /* 進度條顏色 */
    .stProgress > div > div > div {{{{
        background-color: {COLOR_PRIMARY};
    }}}}
    .stProgress > div > div {{{{
        background-color: #3A3F4B;
    }}}}

</style>
""".format(
    COLOR_PRIMARY=COLOR_PRIMARY,
    COLOR_PROFIT=COLOR_PROFIT,
    COLOR_LOSS=COLOR_LOSS
), unsafe_allow_html=True)


# 計算函數
def parse_csv(file):
    """解析CSV檔案"""
    encodings = ['big5', 'utf-8', 'gb2312', 'cp950']

    # 模擬解析進度
    progress_bar = st.empty()
    progress_bar.progress(0, text="載入檔案中...")

    for i, encoding in enumerate(encodings):
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)

            # 模擬計算時間
            time.sleep(0.5)
            progress_bar.progress(int((i + 1) / len(encodings) * 50), text=f"嘗試編碼: {encoding}...")

            required_cols = ['商品名稱', '商品代碼', '序號', '進場時間', '進場方向',
                             '進場價格', '出場時間', '出場方向', '出場價格']
            df = df[required_cols]

            df['進場時間'] = pd.to_datetime(df['進場時間'])
            df['出場時間'] = pd.to_datetime(df['出場時間'])
            df['進場價格'] = pd.to_numeric(df['進場價格'])
            df['出場價格'] = pd.to_numeric(df['出場價格'])

            progress_bar.progress(100, text="✅ 檔案解析完成!")
            time.sleep(0.5)
            progress_bar.empty()

            return df, None
        except Exception as e:
            # 錯誤不需要中斷，繼續嘗試下一個編碼
            continue

    progress_bar.empty()
    return None, "無法解析CSV檔案，請確認檔案格式是否正確"


def calculate_trades(df, investment, mode):
    # ... (計算函數保持不變) ...
    """計算每筆交易的損益 (未考慮交易成本)"""
    trades = []

    # 這裡可以加入一個 progress bar 來追蹤計算進度
    # 但因為計算很快，這裡先省略，保持原本的計算邏輯

    for idx, row in df.iterrows():
        entry_price = row['進場價格']
        exit_price = row['出場價格']

        if entry_price == 0:
            continue

        if mode == "整張計算":
            shares = int(investment / (entry_price * 1000)) * 1000
            if shares < 1000:
                continue
            actual_investment = (shares / 1000) * entry_price * 1000
        else:
            shares = investment / entry_price
            actual_investment = shares * entry_price

        # 簡單計算，未考慮費用
        pnl = shares * (exit_price - entry_price)
        pnl_pct = (exit_price - entry_price) / entry_price

        trades.append({
            '商品名稱': row['商品名稱'],
            '商品代碼': row['商品代碼'],
            '進場時間': row['進場時間'],
            '出場時間': row['出場時間'],
            '進場價格': entry_price,
            '出場價格': exit_price,
            '股數': shares,
            '投入金額': actual_investment,
            '損益': pnl,
            '報酬率': pnl_pct,
            '持有天數': (row['出場時間'] - row['進場時間']).days
        })

    return pd.DataFrame(trades)


# ... (其餘計算函數保持不變) ...

def calculate_equity_curve(trades_df):
    """計算權益曲線，標記創新高點"""
    if len(trades_df) == 0:
        return pd.DataFrame()

    trades_df = trades_df.sort_values('出場時間').reset_index(drop=True)
    trades_df['累積損益'] = trades_df['損益'].cumsum()

    # 標記創新高點
    cumulative = trades_df['累積損益'].values
    running_max = np.maximum.accumulate(cumulative)
    trades_df['New_High'] = (cumulative == running_max) & (
                cumulative > trades_df['累積損益'].shift(1).fillna(-np.inf).values)
    trades_df.loc[0, 'New_High'] = True  # 第一筆交易一定是新高 (相對初始資金0)

    return trades_df


def calculate_concurrent_holdings(trades_df):
    """計算同時持有金額的時間序列"""
    if len(trades_df) == 0:
        return pd.DataFrame()

    # 收集所有時間點
    all_dates = pd.date_range(
        start=trades_df['進場時間'].min(),
        end=trades_df['出場時間'].max(),
        freq='D'
    )

    holdings = []
    for date in all_dates:
        # 找出在這個日期持有的倉位
        holding_positions = trades_df[
            (trades_df['進場時間'].dt.date <= date.date()) &
            (trades_df['出場時間'].dt.date >= date.date())
            ]
        total_amount = holding_positions['投入金額'].sum()
        holdings.append({'日期': date, '持有金額': total_amount})

    return pd.DataFrame(holdings)


def calculate_max_concurrent_positions(trades_df):
    """計算最大同時持有金額"""
    if len(trades_df) == 0:
        return 0

    events = []
    for idx, row in trades_df.iterrows():
        events.append((row['進場時間'], row['投入金額'], 'enter'))
        events.append((row['出場時間'], row['投入金額'], 'exit'))

    events.sort(key=lambda x: (x[0], 0 if x[2] == 'enter' else 1))

    current_amount = 0
    max_amount = 0

    for time, amount, action in events:
        if action == 'enter':
            current_amount += amount
            max_amount = max(max_amount, current_amount)
        else:
            current_amount -= amount

    return max_amount


def calculate_drawdown(equity_curve):
    """計算MDD並標記創新低點"""
    if len(equity_curve) == 0:
        return pd.DataFrame(), 0, 0

    cumulative = equity_curve['累積損益'].values
    running_max = np.maximum.accumulate(cumulative)
    drawdown = cumulative - running_max

    # 標記回撤創新低點 (即最大回撤)
    running_min_dd = np.minimum.accumulate(drawdown)
    equity_curve['New_Drawdown'] = (drawdown == running_min_dd)

    max_dd = drawdown.min()

    # 計算百分比回撤 - 基於初始資金而非最高點 (暫時保留，但不使用)
    initial_capital = 0  # 從0開始
    drawdown_pct = drawdown / (running_max - initial_capital + 1e-10)

    max_dd_pct = drawdown_pct.min()  # 最大的百分比回撤

    dd_df = pd.DataFrame({
        '時間': equity_curve['出場時間'],
        '回撤金額': drawdown,
        '回撤%': drawdown_pct * 100,
        'New_Drawdown': equity_curve['New_Drawdown']
    })

    return dd_df, max_dd, max_dd_pct


def calculate_sharpe_ratio(trades_df):
    """計算夏普值 (年化，假設年交易日 252)"""
    if len(trades_df) == 0:
        return 0

    returns = trades_df['報酬率'].values
    if len(returns) < 2:
        return 0

    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)

    if std_return == 0:
        return 0

    # 假設策略是日頻率，或者報酬率是每筆交易的報酬率
    # 這裡使用每筆交易的報酬率進行年化 (sqrt(交易次數/年化因子), 簡化處理)
    sharpe = (mean_return / std_return) * np.sqrt(252)  # 簡化年化

    return sharpe


def calculate_profit_factor(trades_df):
    """計算獲利因子"""
    gross_profit = trades_df[trades_df['損益'] > 0]['損益'].sum()
    gross_loss = trades_df[trades_df['損益'] < 0]['損益'].sum()

    if gross_loss == 0 or gross_profit == 0:
        return np.inf if gross_loss == 0 else 0
    else:
        return gross_profit / abs(gross_loss)


def monte_carlo_simulation(trades_df, n_simulations):
    """蒙地卡羅模擬 - 返回多條權益曲線"""
    if len(trades_df) == 0:
        return []

    pnl_values = trades_df['損益'].values
    n_trades = len(pnl_values)

    simulation_curves = []

    # 步驟 3: 在開始模擬時顯示進度條
    progress_bar = st.empty()

    for i in range(n_simulations):
        # 隨機抽樣交易損益 (Bootstrap)
        sim_pnl = np.random.choice(pnl_values, size=n_trades, replace=True)
        sim_cumulative = np.cumsum(sim_pnl)
        simulation_curves.append(sim_cumulative)

        # 更新進度條 (因為計算速度很快，這裡可以加入 time.sleep(0.001) 讓進度條稍微可見)
        progress = int((i + 1) / n_simulations * 100)
        progress_bar.progress(progress, text=f"執行模擬中: {i + 1}/{n_simulations} ({progress}%)")

        # 由於 Streamlit 單線程的限制，這裡的百分比顯示僅為參考，並非實時進度。
        # time.sleep(0.001) # 可選: 稍微延遲讓用戶看到進度條

    progress_bar.progress(100, text="✅ 模擬完成!")
    time.sleep(0.5)
    progress_bar.empty()

    return simulation_curves


# 主標題
st.markdown("<h1>⚡ 3Q全球贏家</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 1.15em; margin-top: -10px;'>專業回測分析平台</p>",
            unsafe_allow_html=True)

# 主要內容
if not st.session_state.uploaded:
    # 未上傳狀態 - 僅保留標準的 st.file_uploader
    st.markdown("<h2>💾 上傳回測報表</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #9CA3AF; font-size: 1.05em; margin-bottom: 25px;'>請上傳 XQ 全球贏家匯出的 CSV 交易回測報表。</p>",
        unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "請選擇 CSV 檔案",
        type=['csv'],
        label_visibility="visible",
        key="file_uploader_key"
    )

    if uploaded_file is not None:
        # 這裡會觸發 parse_csv 內部的進度條
        df, error = parse_csv(uploaded_file)

        if error:
            st.error(f"❌ {error}")
        else:
            st.session_state.df = df
            st.session_state.uploaded = True
            st.rerun()

elif not st.session_state.params_confirmed:
    # 參數設定階段
    st.markdown("<h2>⚙️ 回測參數設定</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        investment_amount = st.number_input(
            "💰 每筆固定投入金額 (元)",
            min_value=1000,
            value=100000,
            step=10000,
            format="%d",
            help="每次進場時投入的固定金額"
        )

        # 修正: 使用 st.radio 替換下拉選單
        calc_mode = st.radio(
            "📊 計算模式",
            ["整張計算", "股數計算"],
            index=0,
            key="calc_mode_radio",
            help="整張計算: 以1000股為單位，高價股可能買不起\n股數計算: 可買零股，任何價位都能買"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            if st.button("✅ 確認開始分析", type="primary", use_container_width=True):
                # 這裡不需要進度條，因為主要計算在後面
                st.session_state.investment_amount = investment_amount
                st.session_state.calc_mode = calc_mode
                st.session_state.params_confirmed = True
                st.rerun()

else:
    # 已確認參數 - 顯示分析結果
    df = st.session_state.df
    investment_amount = st.session_state.investment_amount
    calc_mode = st.session_state.calc_mode

    # 側邊欄
    with st.sidebar:
        st.markdown("### ⚙️ 分析設定")
        st.markdown(f"**投入金額:** ${investment_amount:,}")
        st.markdown(f"**計算模式:** {calc_mode}")
        st.markdown("---")

        mc_simulations = st.number_input(
            "🎲 蒙地卡羅次數",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )

        st.markdown("---")

        if st.button("🔄 重新設定"):
            st.session_state.params_confirmed = False
            st.session_state.mc_triggered = False  # 重設時清空模擬結果
            st.rerun()

        if st.button("📤 重新上傳"):
            st.session_state.uploaded = False
            st.session_state.df = None
            st.session_state.params_confirmed = False
            st.session_state.mc_triggered = False  # 重設時清空模擬結果
            st.rerun()

    # 計算交易 (這裡的計算速度很快，不需要進度條)
    trades_df = calculate_trades(df, investment_amount, calc_mode)

    if len(trades_df) == 0:
        st.error(f"❌ 沒有可執行的交易。請檢查您的回測報表或調整投入金額 ${investment_amount:,} 及計算模式: {calc_mode}")
    else:
        # 計算指標
        equity_curve = calculate_equity_curve(trades_df)
        total_pnl = trades_df['損益'].sum()
        total_investment = trades_df['投入金額'].sum()
        total_return = (total_pnl / total_investment) * 100
        max_concurrent = calculate_max_concurrent_positions(trades_df)
        dd_df, max_dd, max_dd_pct = calculate_drawdown(equity_curve)
        sharpe = calculate_sharpe_ratio(trades_df)
        profit_factor = calculate_profit_factor(trades_df)
        win_rate = (trades_df['損益'] > 0).sum() / len(trades_df) * 100
        concurrent_df = calculate_concurrent_holdings(trades_df)

        # 關鍵指標
        st.markdown("<h2>📊 績效總覽</h2>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">📈</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">夏普值</div>
                <div style="color: #E8EAED; font-size: 1.8em; font-weight: 700;">{:.2f}</div>
            </div>
            """.format(sharpe), unsafe_allow_html=True)

        with col2:
            pf_color = COLOR_PROFIT if profit_factor >= 1 else COLOR_LOSS
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">⚖️</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">獲利因子</div>
                <div style="color: {pf_color}; font-size: 1.8em; font-weight: 700;">{profit_factor:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">💼</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">最大持倉</div>
                <div style="color: #E8EAED; font-size: 1.8em; font-weight: 700;">${:,.0f}</div>
            </div>
            """.format(max_concurrent), unsafe_allow_html=True)

        with col4:
            # 修正: 虧損為綠色 (COLOR_LOSS)，最大回撤是負數
            mdd_color = COLOR_LOSS if max_dd < 0 else COLOR_PROFIT
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">📉</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">最大回撤 (MDD)</div>
                <div style="color: {mdd_color}; font-size: 1.8em; font-weight: 700;">${max_dd:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            # 修正: 賺錢為紅色 (COLOR_PROFIT)
            return_color = COLOR_PROFIT if total_return > 0 else COLOR_LOSS
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">💹</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">總回報率</div>
                <div style="color: {return_color}; font-size: 1.8em; font-weight: 700;">{total_return:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col6:
            # 修正: 賺錢為紅色 (COLOR_PROFIT)
            pnl_color = COLOR_PROFIT if total_pnl > 0 else COLOR_LOSS
            # 修正: 補上說明 (圖一問題 1)
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">💰</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">總損益</div>
                <div style="color: {pnl_color}; font-size: 1.8em; font-weight: 700;">${total_pnl:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 勝率", f"{win_rate:.1f}%")
        with col2:
            st.metric("📝 交易次數", f"{len(trades_df)}")
        with col3:
            avg_pnl = trades_df['損益'].mean()
            st.metric("📊 平均損益", f"${avg_pnl:,.0f}")

        # 權益曲線 + 同時持有金額
        st.markdown("<h2>📈 權益曲線 & 資金使用</h2>", unsafe_allow_html=True)

        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=('累積損益曲線', '績效回檔', '同時持有金額')
        )

        # 權益曲線
        fig.add_trace(
            go.Scatter(
                x=equity_curve['出場時間'],
                y=equity_curve['累積損益'],
                mode='lines',
                name='累積損益',
                line=dict(color=COLOR_PROFIT, width=3),  # 修正: 權益曲線用紅色
                fill='tozeroy',
                fillcolor=f'rgba({int(COLOR_PROFIT[1:3], 16)}, {int(COLOR_PROFIT[3:5], 16)}, {int(COLOR_PROFIT[5:7], 16)}, 0.15)',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>累積損益: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )

        # 權益曲線 - 創新高標記
        new_highs = equity_curve[equity_curve['New_High'] == True]
        fig.add_trace(
            go.Scatter(
                x=new_highs['出場時間'],
                y=new_highs['累積損益'],
                mode='markers',
                name='權益新高點',
                marker=dict(color='white', size=8, line=dict(width=1, color=COLOR_PROFIT)),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>權益新高: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_hline(y=0, line_dash="dot", line_color="#6B7280", line_width=1.5, row=1, col=1)

        # 績效回檔 (MDD)
        fig.add_trace(
            go.Scatter(
                x=dd_df['時間'],
                y=dd_df['回撤金額'],
                fill='tozeroy',
                mode='lines',
                name='回撤',
                line=dict(color=COLOR_LOSS, width=2),  # 修正: 回撤用綠色
                fillcolor=f'rgba({int(COLOR_LOSS[1:3], 16)}, {int(COLOR_LOSS[3:5], 16)}, {int(COLOR_LOSS[5:7], 16)}, 0.25)',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>回檔金額: $%{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )

        # 績效回檔 - 創新低標記 (即 MDD)
        new_drawdowns = dd_df[dd_df['New_Drawdown'] == True]
        fig.add_trace(
            go.Scatter(
                x=new_drawdowns['時間'],
                y=new_drawdowns['回撤金額'],
                mode='markers',
                name='最大回撤點',
                marker=dict(color='white', size=8, line=dict(width=1, color=COLOR_LOSS)),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>回檔新低: $%{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )

        # 同時持有金額
        fig.add_trace(
            go.Scatter(
                x=concurrent_df['日期'],
                y=concurrent_df['持有金額'],
                mode='lines',
                name='持有金額',
                line=dict(color='#F59E0B', width=2),
                fill='tozeroy',
                fillcolor='rgba(245, 158, 11, 0.2)',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>持有金額: $%{y:,.0f}<extra></extra>'
            ),
            row=3, col=1
        )

        fig.update_layout(
            height=800,
            template='plotly_dark',
            paper_bgcolor='#0B0E14',
            plot_bgcolor='#1A1D24',
            font=dict(color='#E8EAED', family='Trebuchet MS', size=12),
            hovermode='x unified',
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#3A3F4B',
            showline=True,
            linecolor='#3A3F4B'
        )

        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#3A3F4B',
            showline=True,
            linecolor='#3A3F4B'
        )

        st.plotly_chart(fig, use_container_width=True)

        # 報酬分佈分析
        st.markdown("<h2>📊 報酬分佈分析</h2>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["💰 損益分佈", "💲 價格分析", "📅 時間分析"])

        with tab1:
            # 損益分佈直方圖
            fig_dist = go.Figure()

            # 根據損益正負賦予顏色 (紅色賺，綠色賠)
            pnl_data = trades_df['損益'].values
            colors_hist = [COLOR_PROFIT if p > 0 else COLOR_LOSS for p in pnl_data]

            # 這裡使用 Plotly 內建的 Histogarm
            fig_dist.add_trace(go.Histogram(
                x=pnl_data,
                nbinsx=50,
                # 由於 Plotly Histogram 難以對單一條形圖上色，這裡使用 `marker.color` 保持單一顏色，但在其他圖中使用條件顏色。
                # 為了視覺效果，這裡使用 Primary Color，並在 Bar 圖中使用條件顏色。
                marker=dict(
                    color=COLOR_PRIMARY,
                    line=dict(color='#3A3F4B', width=0.5)
                ),
                hovertemplate='損益: $%{x:,.0f}<br>次數: %{y}<extra></extra>'
            ))

            fig_dist.add_vline(x=0, line_dash="dash", line_color="#E8EAED", line_width=2.5)

            fig_dist.update_layout(
                height=450,
                template='plotly_dark',
                paper_bgcolor='#0B0E14',
                plot_bgcolor='#1A1D24',
                font=dict(color='#E8EAED', size=12),
                xaxis_title="損益 (元)",
                yaxis_title="交易次數",
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )

            fig_dist.update_xaxes(showgrid=True, gridcolor='#3A3F4B')
            fig_dist.update_yaxes(showgrid=True, gridcolor='#3A3F4B')

            st.plotly_chart(fig_dist, use_container_width=True)

        with tab2:
            # 價格區間與損益的關係
            price_bins = [0, 10, 20, 30, 50, 100, 200, float('inf')]
            price_labels = ['0-10', '10-20', '20-30', '30-50', '50-100', '100-200', '200+']

            trades_df['價格區間'] = pd.cut(trades_df['進場價格'], bins=price_bins, labels=price_labels)

            # 計算每個價格區間的總損益和交易次數
            price_analysis = trades_df.groupby('價格區間', observed=True).agg({
                '損益': ['sum', 'mean', 'count']
            }).reset_index()

            price_analysis.columns = ['價格區間', '總損益', '平均損益', '交易次數']

            # 繪製價格分析圖
            fig_price = make_subplots(
                rows=1, cols=2,
                subplot_titles=('各價格區間總損益', '各價格區間平均損益'),
                horizontal_spacing=0.12
            )

            # 修正: 根據損益正負賦予顏色 (紅色賺，綠色賠)
            colors_sum = [COLOR_PROFIT if x > 0 else COLOR_LOSS for x in price_analysis['總損益']]
            colors_avg = [COLOR_PROFIT if x > 0 else COLOR_LOSS for x in price_analysis['平均損益']]

            fig_price.add_trace(
                go.Bar(
                    x=price_analysis['價格區間'],
                    y=price_analysis['總損益'],
                    marker=dict(color=colors_sum, line=dict(color='#3A3F4B', width=0.5)),
                    text=price_analysis['交易次數'],
                    texttemplate='%{text}筆',
                    textposition='outside',
                    hovertemplate='<b>%{x}元</b><br>總損益: $%{y:,.0f}<br>交易次數: %{text}筆<extra></extra>'
                ),
                row=1, col=1
            )

            fig_price.add_trace(
                go.Bar(
                    x=price_analysis['價格區間'],
                    y=price_analysis['平均損益'],
                    marker=dict(color=colors_avg, line=dict(color='#3A3F4B', width=0.5)),
                    hovertemplate='<b>%{x}元</b><br>平均損益: $%{y:,.0f}<extra></extra>'
                ),
                row=1, col=2
            )

            fig_price.add_hline(y=0, line_dash="dash", line_color="#6B7280", line_width=1.5, row=1, col=1)
            fig_price.add_hline(y=0, line_dash="dash", line_color="#6B7280", line_width=1.5, row=1, col=2)

            fig_price.update_layout(
                height=450,
                template='plotly_dark',
                paper_bgcolor='#0B0E14',
                plot_bgcolor='#1A1D24',
                font=dict(color='#E8EAED', size=12),
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            fig_price.update_xaxes(title_text="進場價格區間", showgrid=True, gridcolor='#3A3F4B')
            fig_price.update_yaxes(title_text="損益 (元)", showgrid=True, gridcolor='#3A3F4B')

            st.plotly_chart(fig_price, use_container_width=True)

            # 顯示詳細數據
            st.dataframe(
                price_analysis.style.format({
                    '總損益': '${:,.0f}',
                    '平均損益': '${:,.0f}',
                    '交易次數': '{:.0f}'
                }),
                use_container_width=True
            )

        with tab3:
            # 時間分析 - 依開倉時間
            time_tab1, time_tab2 = st.tabs(["📅 依開倉時間", "📅 依關倉時間"])

            with time_tab1:
                # 按月份分組 - 開倉
                trades_df['進場月份'] = trades_df['進場時間'].dt.to_period('M')
                entry_analysis = trades_df.groupby('進場月份').agg({
                    '損益': ['sum', 'count']
                }).reset_index()
                entry_analysis.columns = ['月份', '總損益', '交易次數']
                entry_analysis['月份'] = entry_analysis['月份'].astype(str)

                fig_entry = go.Figure()

                # 修正: 根據損益正負賦予顏色 (紅色賺，綠色賠)
                colors_entry = [COLOR_PROFIT if x > 0 else COLOR_LOSS for x in entry_analysis['總損益']]

                fig_entry.add_trace(
                    go.Bar(
                        x=entry_analysis['月份'],
                        y=entry_analysis['總損益'],
                        marker=dict(color=colors_entry, line=dict(color='#3A3F4B', width=0.5)),
                        text=entry_analysis['交易次數'],
                        texttemplate='%{text}筆',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>總損益: $%{y:,.0f}<br>交易次數: %{text}筆<extra></extra>',
                        name='總損益'
                    )
                )

                fig_entry.add_hline(y=0, line_dash="dash", line_color="#6B7280", line_width=1.5)

                fig_entry.update_layout(
                    title='開倉月份 - 總損益',
                    height=500,
                    template='plotly_dark',
                    paper_bgcolor='#0B0E14',
                    plot_bgcolor='#1A1D24',
                    font=dict(color='#E8EAED', size=12),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=60, b=20),
                    xaxis_title='月份',
                    yaxis_title='總損益 (元)'
                )

                fig_entry.update_xaxes(showgrid=True, gridcolor='#3A3F4B')
                fig_entry.update_yaxes(showgrid=True, gridcolor='#3A3F4B')

                st.plotly_chart(fig_entry, use_container_width=True)

                st.dataframe(entry_analysis.style.format({'總損益': '${:,.0f}', '交易次數': '{:.0f}'}),
                             use_container_width=True)

            with time_tab2:
                # 按月份分組 - 關倉
                trades_df['出場月份'] = trades_df['出場時間'].dt.to_period('M')
                exit_analysis = trades_df.groupby('出場月份').agg({
                    '損益': ['sum', 'count']
                }).reset_index()
                exit_analysis.columns = ['月份', '總損益', '交易次數']
                exit_analysis['月份'] = exit_analysis['月份'].astype(str)

                fig_exit = go.Figure()

                # 修正: 根據損益正負賦予顏色 (紅色賺，綠色賠)
                colors_exit = [COLOR_PROFIT if x > 0 else COLOR_LOSS for x in exit_analysis['總損益']]

                fig_exit.add_trace(
                    go.Bar(
                        x=exit_analysis['月份'],
                        y=exit_analysis['總損益'],
                        marker=dict(color=colors_exit, line=dict(color='#3A3F4B', width=0.5)),
                        text=exit_analysis['交易次數'],
                        texttemplate='%{text}筆',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>總損益: $%{y:,.0f}<br>交易次數: %{text}筆<extra></extra>',
                        name='總損益'
                    )
                )

                fig_exit.add_hline(y=0, line_dash="dash", line_color="#6B7280", line_width=1.5)

                fig_exit.update_layout(
                    title='關倉月份 - 總損益',
                    height=500,
                    template='plotly_dark',
                    paper_bgcolor='#0B0E14',
                    plot_bgcolor='#1A1D24',
                    font=dict(color='#E8EAED', size=12),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=60, b=20),
                    xaxis_title='月份',
                    yaxis_title='總損益 (元)'
                )

                fig_exit.update_xaxes(showgrid=True, gridcolor='#3A3F4B')
                fig_exit.update_yaxes(showgrid=True, gridcolor='#3A3F4B')

                st.plotly_chart(fig_exit, use_container_width=True)

                st.dataframe(exit_analysis.style.format({'總損益': '${:,.0f}', '交易次數': '{:.0f}'}),
                             use_container_width=True)

        # 蒙地卡羅模擬
        st.markdown("<h2>🎲 蒙地卡羅模擬</h2>", unsafe_allow_html=True)

        # 修正: 將按鈕獨立出來
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("🚀 開始模擬", type="primary", use_container_width=True, key="mc_start_button"):
                # 按鈕被點擊，設置 session state 標記，並儲存模擬次數
                st.session_state.mc_triggered = True
                st.session_state.mc_simulations = mc_simulations
                # 重新執行以觸發下一階段的圖表顯示
                # 這裡不需要 rerun，因為計算會直接在這裡發生
                pass  # 讓程式碼繼續向下執行，進入模擬繪圖區塊

        if st.session_state.mc_triggered:
            # 確保有交易數據才能模擬
            if len(trades_df) > 0:
                mc_simulations_count = st.session_state.mc_simulations

                # 模擬計算會在這裡執行，並顯示內部進度條
                simulation_curves = monte_carlo_simulation(trades_df, mc_simulations_count)

                # 繪製模擬曲線
                fig_mc = go.Figure()

                # 添加所有模擬曲線
                for i, curve in enumerate(simulation_curves):
                    # 降低透明度，讓實際曲線更突出
                    fig_mc.add_trace(go.Scatter(
                        x=list(range(len(curve))),
                        y=curve,
                        mode='lines',
                        line=dict(
                            color=f'rgba({int(COLOR_PRIMARY[1:3], 16)}, {int(COLOR_PRIMARY[3:5], 16)}, {int(COLOR_PRIMARY[5:7], 16)}, 0.08)',
                            width=1),  # 模擬曲線使用 Primary Blue
                        showlegend=False,
                        hoverinfo='skip'
                    ))

                # 添加實際曲線
                fig_mc.add_trace(go.Scatter(
                    x=list(range(len(equity_curve))),
                    y=equity_curve['累積損益'].values,
                    mode='lines',
                    name='實際曲線',
                    line=dict(color=COLOR_PROFIT, width=3),  # 修正: 實際曲線用紅色
                    hovertemplate='<b>第%{x}筆交易</b><br>累積損益: $%{y:,.0f}<extra></extra>'
                ))

                # 添加零軸
                fig_mc.add_hline(y=0, line_dash="dash", line_color="#6B7280", line_width=2)

                # 計算統計數據
                final_values = [curve[-1] for curve in simulation_curves]
                loss_prob = (np.array(final_values) < 0).sum() / len(final_values) * 100
                percentile_5 = np.percentile(final_values, 5)
                percentile_95 = np.percentile(final_values, 95)
                median = np.median(final_values)

                fig_mc.update_layout(
                    title=f'蒙地卡羅模擬 (n={mc_simulations_count}) - 權益曲線',
                    height=550,
                    template='plotly_dark',
                    paper_bgcolor='#0B0E14',
                    plot_bgcolor='#1A1D24',
                    font=dict(color='#E8EAED', size=12),
                    xaxis_title="交易次數",
                    yaxis_title="累積損益 (元)",
                    hovermode='closest',
                    showlegend=True,
                    margin=dict(l=20, r=20, t=60, b=20)
                )

                fig_mc.update_xaxes(showgrid=True, gridcolor='#3A3F4B')
                fig_mc.update_yaxes(showgrid=True, gridcolor='#3A3F4B')

                st.plotly_chart(fig_mc, use_container_width=True)

                # 顯示統計數據
                st.markdown("### 📊 模擬統計")
                col_mc1, col_mc2, col_mc3, col_mc4 = st.columns(4)

                with col_mc1:
                    # 修正: 虧損機率顏色（機率越低越好，但這裡的顏色用於突顯數據）
                    loss_color = COLOR_LOSS if loss_prob < 10 else COLOR_PROFIT
                    st.markdown(
                        f"<p style='color: {loss_color}; font-size: 1.5em; font-weight: 700;'>{loss_prob:.1f}%</p>",
                        unsafe_allow_html=True)
                    st.markdown("<p style='color: #9CA3AF; font-size: 0.9em;'>⚠️ 虧損機率</p>", unsafe_allow_html=True)

                with col_mc2:
                    # 修正: 樂觀情境顏色 (賺錢用紅色)
                    p95_color = COLOR_PROFIT if percentile_95 > 0 else COLOR_LOSS
                    st.markdown(
                        f"<p style='color: {p95_color}; font-size: 1.5em; font-weight: 700;'>${percentile_95:,.0f}</p>",
                        unsafe_allow_html=True)
                    st.markdown("<p style='color: #9CA3AF; font-size: 0.9em;'>📈 95% 樂觀情境</p>",
                                unsafe_allow_html=True)

                with col_mc3:
                    # 修正: 中位數顏色 (賺錢用紅色)
                    median_color = COLOR_PROFIT if median > 0 else COLOR_LOSS
                    st.markdown(
                        f"<p style='color: {median_color}; font-size: 1.5em; font-weight: 700;'>${median:,.0f}</p>",
                        unsafe_allow_html=True)
                    st.markdown("<p style='color: #9CA3AF; font-size: 0.9em;'>⚖️ 模擬中位數</p>",
                                unsafe_allow_html=True)

                with col_mc4:
                    # 修正: 最差情境顏色 (賺錢用紅色)
                    p5_color = COLOR_PROFIT if percentile_5 > 0 else COLOR_LOSS
                    st.markdown(
                        f"<p style='color: {p5_color}; font-size: 1.5em; font-weight: 700;'>${percentile_5:,.0f}</p>",
                        unsafe_allow_html=True)
                    st.markdown("<p style='color: #9CA3AF; font-size: 0.9em;'>📉 5% 最差情境</p>",
                                unsafe_allow_html=True)

                    ## RUN 的方法：streamlit run app.py