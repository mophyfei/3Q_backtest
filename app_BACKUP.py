import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

# 設定頁面配置
st.set_page_config(page_title="3Q全球贏家", layout="wide", initial_sidebar_state="collapsed")

# 自訂CSS - TradingView風格
st.markdown("""
<style>
    .main {
        background: #0B0E14;
    }
    .stApp {
        background: #0B0E14;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    h1 {
        color: #4A9EFF !important;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: 600;
        font-size: 2.8em !important;
        text-align: center;
        margin-bottom: 0 !important;
        text-shadow: 0 0 30px rgba(74, 158, 255, 0.5);
    }

    h2 {
        color: #E8EAED !important;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: 500;
        font-size: 1.4em !important;
        border-left: 4px solid #4A9EFF;
        padding-left: 15px;
        margin-top: 40px !important;
        margin-bottom: 20px !important;
    }

    .upload-zone {
        background: linear-gradient(145deg, #1A1D24 0%, #252930 100%);
        border: 3px dashed #4A9EFF;
        border-radius: 20px;
        padding: 80px 40px;
        text-align: center;
        margin: 50px auto;
        max-width: 900px;
        cursor: pointer;
        transition: all 0.4s ease;
        box-shadow: 0 10px 40px rgba(74, 158, 255, 0.2);
    }

    .upload-zone:hover {
        border-color: #6BB6FF;
        box-shadow: 0 15px 60px rgba(74, 158, 255, 0.35);
        transform: translateY(-5px);
        background: linear-gradient(145deg, #1F2229 0%, #2A2F38 100%);
    }

    .metric-card {
        background: linear-gradient(145deg, #1A1D24 0%, #252930 100%);
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 30px rgba(74, 158, 255, 0.15);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(74, 158, 255, 0.25);
        border-color: rgba(74, 158, 255, 0.5);
    }

    .stMetric label {
        color: #9CA3AF !important;
        font-size: 0.95em !important;
        font-weight: 500 !important;
    }

    .stMetric > div {
        color: #E8EAED !important;
        font-size: 2em !important;
        font-weight: 700 !important;
    }

    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: #1A1D24 !important;
        color: #E8EAED !important;
        border: 1px solid #3A3F4B !important;
        border-radius: 8px !important;
        font-size: 1.05em !important;
    }

    .stButton > button {
        background: linear-gradient(145deg, #4A9EFF 0%, #357ABD 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 36px;
        font-weight: 600;
        font-size: 1.05em;
        box-shadow: 0 6px 20px rgba(74, 158, 255, 0.4);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(145deg, #6BB6FF 0%, #4A9EFF 100%);
        box-shadow: 0 8px 30px rgba(74, 158, 255, 0.5);
        transform: translateY(-3px);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #1A1D24;
        border-radius: 10px;
        padding: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #9CA3AF;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 1.05em;
    }

    .stTabs [aria-selected="true"] {
        background: #4A9EFF;
        color: white;
    }

    .profit {
        color: #EF4444 !important;
    }

    .loss {
        color: #10B981 !important;
    }

    .streamlit-expanderHeader {
        background: #1A1D24;
        border: 1px solid #3A3F4B;
        border-radius: 10px;
        color: #E8EAED !important;
        font-size: 1.05em !important;
    }

    hr {
        border-color: #3A3F4B;
        margin: 40px 0;
    }

    .stSpinner > div {
        border-top-color: #4A9EFF !important;
    }

    /* 修復數字可讀性 */
    p, span, div {
        color: #E8EAED;
    }

    .stMarkdown {
        color: #E8EAED;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'params_confirmed' not in st.session_state:
    st.session_state.params_confirmed = False


# 計算函數
def parse_csv(file):
    """解析CSV檔案"""
    encodings = ['big5', 'utf-8', 'gb2312', 'cp950']

    for encoding in encodings:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)

            required_cols = ['商品名稱', '商品代碼', '序號', '進場時間', '進場方向',
                             '進場價格', '出場時間', '出場方向', '出場價格']
            df = df[required_cols]

            df['進場時間'] = pd.to_datetime(df['進場時間'])
            df['出場時間'] = pd.to_datetime(df['出場時間'])
            df['進場價格'] = pd.to_numeric(df['進場價格'])
            df['出場價格'] = pd.to_numeric(df['出場價格'])

            return df, None
        except Exception as e:
            continue

    return None, "無法解析CSV檔案，請確認檔案格式是否正確"


def calculate_trades(df, investment, mode):
    """計算每筆交易的損益"""
    trades = []

    for idx, row in df.iterrows():
        entry_price = row['進場價格']
        exit_price = row['出場價格']

        if mode == "整張計算":
            shares = int(investment / (entry_price * 1000)) * 1000
            if shares < 1000:
                continue
            actual_investment = (shares / 1000) * entry_price * 1000
        else:
            shares = investment / entry_price
            actual_investment = shares * entry_price

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


def calculate_equity_curve(trades_df):
    """計算權益曲線"""
    if len(trades_df) == 0:
        return pd.DataFrame()

    trades_df = trades_df.sort_values('出場時間').reset_index(drop=True)
    trades_df['累積損益'] = trades_df['損益'].cumsum()

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
            (trades_df['進場時間'] <= date) &
            (trades_df['出場時間'] >= date)
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
    """計算MDD"""
    if len(equity_curve) == 0:
        return pd.DataFrame(), 0, 0

    cumulative = equity_curve['累積損益'].values
    running_max = np.maximum.accumulate(cumulative)
    drawdown = cumulative - running_max

    # 計算百分比回撤 - 基於初始資金而非最高點
    initial_capital = 0  # 從0開始
    drawdown_pct = drawdown / (running_max - initial_capital + 1e-10)

    max_dd = drawdown.min()
    max_dd_pct = drawdown_pct.min()

    dd_df = pd.DataFrame({
        '時間': equity_curve['出場時間'],
        '回撤金額': drawdown,
        '回撤%': drawdown_pct * 100
    })

    return dd_df, max_dd, max_dd_pct


def calculate_sharpe_ratio(trades_df):
    """計算夏普值"""
    if len(trades_df) == 0:
        return 0

    returns = trades_df['報酬率'].values
    if len(returns) < 2:
        return 0

    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)

    if std_return == 0:
        return 0

    sharpe = (mean_return / std_return) * np.sqrt(252)

    return sharpe


def monte_carlo_simulation(trades_df, n_simulations, investment):
    """蒙地卡羅模擬 - 返回多條權益曲線"""
    if len(trades_df) == 0:
        return []

    returns = trades_df['報酬率'].values
    pnl_values = trades_df['損益'].values
    n_trades = len(returns)

    simulation_curves = []

    for _ in range(n_simulations):
        # 隨機抽樣交易損益
        sim_pnl = np.random.choice(pnl_values, size=n_trades, replace=True)
        sim_cumulative = np.cumsum(sim_pnl)
        simulation_curves.append(sim_cumulative)

    return simulation_curves


# 主標題
st.markdown("<h1>⚡ 3Q全球贏家</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 1.15em; margin-top: -10px;'>專業回測分析平台</p>",
            unsafe_allow_html=True)

# 主要內容
if not st.session_state.uploaded:
    # 未上傳狀態
    st.markdown("<br><br>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "",
        type=['csv'],
        label_visibility="collapsed",
        help="拖曳CSV檔案到此處或點擊上傳"
    )

    # 使用HTML/CSS創建大的上傳區域提示
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size: 5em; margin-bottom: 25px;">📊</div>
        <h2 style="color: #E8EAED; margin: 0; border: none; padding: 0; font-size: 2em;">上傳回測報表</h2>
        <p style="color: #9CA3AF; margin-top: 15px; font-size: 1.2em;">支援 XQ 全球贏家 CSV 格式</p>
        <p style="color: #6B7280; margin-top: 10px; font-size: 1em;">請使用上方的按鈕選擇檔案</p>
    </div>
    """, unsafe_allow_html=True)

    if uploaded_file is not None:
        with st.spinner('🔄 正在解析檔案...'):
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
        st.markdown("""
        <div style="background: linear-gradient(145deg, #1A1D24 0%, #252930 100%); 
                    padding: 40px; border-radius: 15px; border: 1px solid rgba(74, 158, 255, 0.3);">
        """, unsafe_allow_html=True)

        investment_amount = st.number_input(
            "💰 每筆固定投入金額 (元)",
            min_value=1000,
            value=100000,
            step=10000,
            format="%d",
            help="每次進場時投入的固定金額"
        )

        calc_mode = st.selectbox(
            "📊 計算模式",
            ["整張計算", "股數計算"],
            help="整張計算: 以1000股為單位，高價股可能買不起\n股數計算: 可買零股，任何價位都能買"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            if st.button("✅ 確認開始分析", type="primary", use_container_width=True):
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
            st.rerun()

        if st.button("📤 重新上傳"):
            st.session_state.uploaded = False
            st.session_state.df = None
            st.session_state.params_confirmed = False
            st.rerun()

    # 計算交易
    trades_df = calculate_trades(df, investment_amount, calc_mode)

    if len(trades_df) == 0:
        st.error("❌ 沒有可執行的交易，請調整投入金額或計算模式")
    else:
        # 計算指標
        equity_curve = calculate_equity_curve(trades_df)
        total_pnl = trades_df['損益'].sum()
        total_investment = trades_df['投入金額'].sum()
        total_return = (total_pnl / total_investment) * 100
        max_concurrent = calculate_max_concurrent_positions(trades_df)
        dd_df, max_dd, max_dd_pct = calculate_drawdown(equity_curve)
        sharpe = calculate_sharpe_ratio(trades_df)
        win_rate = (trades_df['損益'] > 0).sum() / len(trades_df) * 100
        concurrent_df = calculate_concurrent_holdings(trades_df)

        # 關鍵指標
        st.markdown("<h2>📊 績效總覽</h2>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">📈</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">夏普值</div>
                <div style="color: #E8EAED; font-size: 1.8em; font-weight: 700;">{:.2f}</div>
            </div>
            """.format(sharpe), unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">💼</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">最大持倉</div>
                <div style="color: #E8EAED; font-size: 1.8em; font-weight: 700;">${:,.0f}</div>
            </div>
            """.format(max_concurrent), unsafe_allow_html=True)

        with col3:
            mdd_color = "#10B981" if max_dd < 0 else "#EF4444"
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">📉</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">最大回撤 (MDD)</div>
                <div style="color: {}; font-size: 1.8em; font-weight: 700;">${:,.0f}</div>
                <div style="color: {}; font-size: 1.2em; margin-top: 5px;">({:.2f}%)</div>
            </div>
            """.format(mdd_color, max_dd, mdd_color, max_dd_pct * 100), unsafe_allow_html=True)

        with col4:
            return_color = "#EF4444" if total_return > 0 else "#10B981"
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">💹</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">總回報率</div>
                <div style="color: {}; font-size: 1.8em; font-weight: 700;">{:.2f}%</div>
            </div>
            """.format(return_color, total_return), unsafe_allow_html=True)

        with col5:
            pnl_color = "#EF4444" if total_pnl > 0 else "#10B981"
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5em; margin-bottom: 10px;">💰</div>
                <div style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 5px;">總損益</div>
                <div style="color: {}; font-size: 1.8em; font-weight: 700;">${:,.0f}</div>
            </div>
            """.format(pnl_color, total_pnl), unsafe_allow_html=True)

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
            subplot_titles=('權益曲線', '回撤 (MDD)', '同時持有金額')
        )

        # 權益曲線
        fig.add_trace(
            go.Scatter(
                x=equity_curve['出場時間'],
                y=equity_curve['累積損益'],
                mode='lines',
                name='累積損益',
                line=dict(color='#4A9EFF', width=3),
                fill='tozeroy',
                fillcolor='rgba(74, 158, 255, 0.15)',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>累積損益: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_hline(y=0, line_dash="dot", line_color="#6B7280", line_width=1.5, row=1, col=1)

        # MDD
        fig.add_trace(
            go.Scatter(
                x=dd_df['時間'],
                y=dd_df['回撤金額'],
                fill='tozeroy',
                mode='lines',
                name='回撤',
                line=dict(color='#EF4444', width=2),
                fillcolor='rgba(239, 68, 68, 0.25)',
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>回撤: $%{y:,.0f}<extra></extra>'
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

            colors = ['#EF4444' if x > 0 else '#10B981' for x in trades_df['損益']]

            fig_dist.add_trace(go.Histogram(
                x=trades_df['損益'],
                nbinsx=50,
                marker=dict(
                    color=colors,
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

            # 計算每個價格區間的平均損益和交易次數
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

            colors_sum = ['#EF4444' if x > 0 else '#10B981' for x in price_analysis['總損益']]
            colors_avg = ['#EF4444' if x > 0 else '#10B981' for x in price_analysis['平均損益']]

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
            # 時間分析
            time_tab1, time_tab2 = st.tabs(["📅 依開倉時間", "📅 依關倉時間"])

            with time_tab1:
                # 按月份分組 - 開倉
                trades_df['進場月份'] = trades_df['進場時間'].dt.to_period('M')
                entry_analysis = trades_df.groupby('進場月份').agg({
                    '損益': ['sum', 'mean', 'count']
                }).reset_index()
                entry_analysis.columns = ['月份', '總損益', '平均損益', '交易次數']
                entry_analysis['月份'] = entry_analysis['月份'].astype(str)

                fig_entry = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('開倉月份 - 總損益', '開倉月份 - 平均損益'),
                    vertical_spacing=0.15,
                    row_heights=[0.5, 0.5]
                )

                colors_entry = ['#EF4444' if x > 0 else '#10B981' for x in entry_analysis['總損益']]

                fig_entry.add_trace(
                    go.Bar(
                        x=entry_analysis['月份'],
                        y=entry_analysis['總損益'],
                        marker=dict(color=colors_entry, line=dict(color='#3A3F4B', width=0.5)),
                        text=entry_analysis['交易次數'],
                        texttemplate='%{text}筆',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>總損益: $%{y:,.0f}<br>交易次數: %{text}筆<extra></extra>'
                    ),
                    row=1, col=1
                )

                colors_avg = ['#EF4444' if x > 0 else '#10B981' for x in entry_analysis['平均損益']]

                fig_entry.add_trace(
                    go.Bar(
                        x=entry_analysis['月份'],
                        y=entry_analysis['平均損益'],
                        marker=dict(color=colors_avg, line=dict(color='#3A3F4B', width=0.5)),
                        hovertemplate='<b>%{x}</b><br>平均損益: $%{y:,.0f}<extra></extra>'
                    ),
                    row=2, col=1
                )

                fig_entry.add_hline(y=0, line_dash="dash", line_color="#6B7280", line_width=1.5)

                fig_entry.update_layout(
                    height=700,
                    template='plotly_dark',
                    paper_bgcolor='#0B0E14',
                    plot_bgcolor='#1A1D24',
                    font=dict(color='#E8EAED', size=12),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                fig_entry.update_xaxes(showgrid=True, gridcolor='#3A3F4B')
                fig_entry.update_yaxes(title_text="損益 (元)", showgrid=True, gridcolor='#3A3F4B')

                st.plotly_chart(fig_entry, use_container_width=True)

            with time_tab2:
                # 按月份分組 - 關倉
                trades_df['出場月份'] = trades_df['出場時間'].dt.to_period('M')
                exit_analysis = trades_df.groupby('出場月份').agg({
                    '損益': ['sum', 'mean', 'count']
                }).reset_index()
                exit_analysis.columns = ['月份', '總損益', '平均損益', '交易次數']
                exit_analysis['月份'] = exit_analysis['月份'].astype(str)

                fig_exit = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('關倉月份 - 總損益', '關倉月份 - 平均損益'),
                    vertical_spacing=0.15,
                    row_heights=[0.5, 0.5]
                )

                colors_exit = ['#EF4444' if x > 0 else '#10B981' for x in exit_analysis['總損益']]

                fig_exit.add_trace(
                    go.Bar(
                        x=exit_analysis['月份'],
                        y=exit_analysis['總損益'],
                        marker=dict(color=colors_exit, line=dict(color='#3A3F4B', width=0.5)),
                        text=exit_analysis['交易次數'],
                        texttemplate='%{text}筆',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>總損益: $%{y:,.0f}<br>交易次數: %{text}筆<extra></extra>'
                    ),
                    row=1, col=1
                )

                colors_avg_exit = ['#EF4444' if x > 0 else '#10B981' for x in exit_analysis['平均損益']]

                fig_exit.add_trace(
                    go.Bar(
                        x=exit_analysis['月份'],
                        y=exit_analysis['平均損益'],
                        marker=dict(color=colors_avg_exit, line=dict(color='#3A3F4B', width=0.5)),
                        hovertemplate='<b>%{x}</b><br>平均損益: $%{y:,.0f}<extra></extra>'
                    ),
                    row=2, col=1
                )

                fig_exit.add_hline(y=0, line_dash="dash", line_color="#6B7280", line_width=1.5)

                fig_exit.update_layout(
                    height=700,
                    template='plotly_dark',
                    paper_bgcolor='#0B0E14',
                    plot_bgcolor='#1A1D24',
                    font=dict(color='#E8EAED', size=12),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                fig_exit.update_xaxes(showgrid=True, gridcolor='#3A3F4B')
                fig_exit.update_yaxes(title_text="損益 (元)", showgrid=True, gridcolor='#3A3F4B')

                st.plotly_chart(fig_exit, use_container_width=True)

        # 蒙地卡羅模擬
        st.markdown("<h2>🎲 蒙地卡羅模擬</h2>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🚀 開始模擬", type="primary", use_container_width=True):
                with st.spinner(f'⚡ 執行 {mc_simulations} 次模擬中...'):
                    simulation_curves = monte_carlo_simulation(trades_df, mc_simulations, investment_amount)

                    # 繪製模擬曲線
                    fig_mc = go.Figure()

                    # 添加所有模擬曲線
                    for i, curve in enumerate(simulation_curves):
                        color = 'rgba(74, 158, 255, 0.05)' if i < len(
                            simulation_curves) - 1 else 'rgba(74, 158, 255, 0.05)'
                        fig_mc.add_trace(go.Scatter(
                            x=list(range(len(curve))),
                            y=curve,
                            mode='lines',
                            line=dict(color=color, width=1),
                            showlegend=False,
                            hoverinfo='skip'
                        ))

                    # 添加實際曲線
                    fig_mc.add_trace(go.Scatter(
                        x=list(range(len(equity_curve))),
                        y=equity_curve['累積損益'].values,
                        mode='lines',
                        name='實際曲線',
                        line=dict(color='#EF4444', width=3),
                        hovertemplate='<b>第%{x}筆交易</b><br>累積損益: $%{y:,.0f}<extra></extra>'
                    ))

                    # 添加零軸
                    fig_mc.add_hline(y=0, line_dash="dash", line_color="#E8EAED", line_width=2)

                    # 計算統計數據
                    final_values = [curve[-1] for curve in simulation_curves]
                    loss_prob = (np.array(final_values) < 0).sum() / len(final_values) * 100
                    percentile_5 = np.percentile(final_values, 5)
                    percentile_95 = np.percentile(final_values, 95)
                    median = np.median(final_values)

                    fig_mc.update_layout(
                        title=f'蒙地卡羅模擬 (n={mc_simulations}) - 權益曲線',
                        height=550,
                        template='plotly_dark',
                        paper_bgcolor='#0B0E14',
                        plot_bgcolor='#1A1D24',
                        font=dict(color='#E8EAED', size=12),
                        xaxis_title="交易次數",
                        yaxis_title="累積損益 (元)",
                        hovermode='closest',
                        margin=dict(l=20, r=20, t=60, b=20)
                    )

                    fig_mc.update_xaxes(showgrid=True, gridcolor='#3A3F4B')
                    fig_mc.update_yaxes(showgrid=True, gridcolor='#3A3F4B')

                    st.plotly_chart(fig_mc, use_container_width=True)

                    # 顯示統計數據
                    st.markdown("### 📊 模擬統計")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("⚠️ 虧損機率", f"{loss_prob:.1f}%")
                    with col2:
                        st.metric("📉 5% 最差", f"${percentile_5:,.0f}")
                    with col3:
                        st.metric("📊 中位數", f"${median:,.0f}")
                    with col4:
                        st.metric("📈 95% 最佳", f"${percentile_95:,.0f}")

        # 交易明細
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 查看完整交易明細"):
            st.dataframe(
                trades_df[['商品名稱', '商品代碼', '進場時間', '出場時間', '進場價格',
                           '出場價格', '股數', '投入金額', '損益', '報酬率', '持有天數']].style.format({
                    '進場價格': '${:.2f}',
                    '出場價格': '${:.2f}',
                    '股數': '{:.0f}',
                    '投入金額': '${:,.0f}',
                    '損益': '${:,.0f}',
                    '報酬率': '{:.2%}',
                    '持有天數': '{:.0f}天'
                }),
                use_container_width=True,
                height=400
            )

# 頁尾
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 30px;'>
    <p style='font-size: 1.1em; color: #9CA3AF;'>⚡ 3Q全球贏家 - 專業回測分析系統</p>
    <p style='font-size: 0.9em; color: #6B7280; margin-top: 10px;'>Powered by Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)