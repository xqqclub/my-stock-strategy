import streamlit as st
from finlab import data
from finlab.backtest import sim
import matplotlib.pyplot as plt

# 設定頁面標題
st.title("🚀 台股深度價值動能策略")

if 'FINLAB_TOKEN' in st.secrets:
    data.login(st.secrets['FINLAB_TOKEN'])
else:
    st.error("請先設定 Secrets 才能執行！")

if st.button('執行策略回測與選股'):
    with st.spinner('正在下載資料與運算中...'):
        # 1. 獲取數據
        close = data.get('price:收盤價')
        pe = data.get('price_earning_ratio:本益比')
        pb = data.get('price_book_ratio:股價淨值比')
        rev_yoy = data.get('monthly_revenue:去年同月增減(%)')

        # 2. 計算指標
        sma60 = close.average(60)

        # 3. 篩選條件
        cond_growth = rev_yoy > 0
        cond_value = (pe < 10) & (pb < 1.5)
        cond_trend = close > sma60
        all_conditions = cond_growth & cond_value & cond_trend

        # 4. 選股
        position = (pe * all_conditions).is_smallest(20)
        
        # 顯示最新選股名單 (取出最後一天的持股)
        latest_date = position.index[-1]
        current_stocks = position.iloc[-1]
        selected_tickers = current_stocks[current_stocks > 0].index.tolist()
        
        st.subheader(f"📅 最新選股日期: {latest_date.strftime('%Y-%m-%d')}")
        st.write(f"共選出 {len(selected_tickers)} 檔股票：")
        st.dataframe(selected_tickers)

        # 5. 回測圖表
        report = sim(position, resample='M', fee_ratio=1.425/1000, upload=False)
        
        # 繪製回測曲線
        st.subheader("📈 資產走勢圖")
        fig = report.plot() # 取得 matplotlib 圖表

        st.pyplot(fig) # 在網頁上顯示
