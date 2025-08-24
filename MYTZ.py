from futu_data import *

import numpy as np
import talib
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['simhei']


def calculate_dual_ma(stock, high, low, close):
    # 确保数据格式正确
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)

    # 计算短期和长期 EMA
    A = talib.EMA(high, timeperiod=25)
    B = talib.EMA(low, timeperiod=24)
    A1 = talib.EMA(high, timeperiod=89)
    B1 = talib.EMA(low, timeperiod=90)

    # 计算昨日的 A 和 B（用于判断均线趋势）
    prev_A = np.roll(A, 1)
    prev_B = np.roll(B, 1)
    prev_A[0] = np.nan  # 避免首个数据点异常
    prev_B[0] = np.nan

    prev_A1 = np.roll(A1, 1)
    prev_B1 = np.roll(B1, 1)
    prev_A1[0] = np.nan
    prev_B1[0] = np.nan

    # 条件计算
    F1 = A > B
    F2 = (close < A) & (close > B)
    COND1 = (A > prev_A) & (B > prev_B)
    COND2 = (A < prev_A) & (B < prev_B)
    COND3 = ~(COND1 | COND2)

    F3 = A1 > B1
    F4 = (close < A1) & (close > B1)
    COND4 = (A1 > prev_A1) & (B1 > prev_B1)
    COND5 = (A1 < prev_A1) & (B1 < prev_B1)
    COND6 = ~(COND4 | COND5)

    # 绘制均线
    plt.figure(figsize=(12, 6))
    plt.plot(A, label='EMA(H,25)', color='#87CEEB')
    plt.plot(B, label='EMA(L,24)', color='#87CEEB')
    plt.plot(A1, label='EMA(H,89)', color='#F0E68C')
    plt.plot(B1, label='EMA(L,90)', color='#F0E68C')

    # 使用 plt.vlines() 模拟 STICKLINE 画柱状线
    x = np.arange(len(A))  # 时间轴索引

    # 短期趋势柱状线
    plt.vlines(x[F1 & ~F2 & COND1], B[F1 & ~F2 & COND1], A[F1 & ~F2 & COND1], color='#2896FF', linewidth=2)
    plt.vlines(x[F1 & ~F2 & COND2], B[F1 & ~F2 & COND2], A[F1 & ~F2 & COND2], color='#0000FF', linewidth=2)
    plt.vlines(x[F1 & ~F2 & COND3], B[F1 & ~F2 & COND3], A[F1 & ~F2 & COND3], color='#87CEEB', linewidth=2)

    # 长期趋势柱状线
    plt.vlines(x[F3 & ~F4 & COND4], B1[F3 & ~F4 & COND4], A1[F3 & ~F4 & COND4], color='#FFFF00', linewidth=2)
    plt.vlines(x[F3 & ~F4 & COND5], B1[F3 & ~F4 & COND5], A1[F3 & ~F4 & COND5], color='#FFA500', linewidth=2)
    plt.vlines(x[F3 & ~F4 & COND6], B1[F3 & ~F4 & COND6], A1[F3 & ~F4 & COND6], color='#F0E68C', linewidth=2)

    plt.legend()
    plt.title(stock)
    save_path = os.path.join("./stock_img", f"{stock}.png")
    plt.savefig(save_path)  # 保存图像到本地
    plt.close()

    return A, B, A1, B1


def get_stock_dict():
    stock_file = "stocks/stocks_HK.txt"  # 你的股票文件路径
    df = pd.read_csv(stock_file)
    stock_dict = {}
    for index, row in df.iterrows():
        if index == 0:
            continue
        stock_code = row["代码"]  # 读取股票代码
        stock_name = row["名称"]  # 读取股票名称（可选）
        stock_dict[stock_code] = stock_name
    return stock_dict


if __name__ == '__main__':
    FUTUOPEND_ADDRESS = '127.0.0.1'  # OpenD 监听地址
    FUTUOPEND_PORT = 11111  # OpenD 监听端口
    TRADING_PERIOD = KLType.K_DAY  # 信号 K 线周期
    stock_dict = get_stock_dict()
    stock_codes = list(stock_dict.keys())
    quote_context = OpenQuoteContext(host=FUTUOPEND_ADDRESS, port=FUTUOPEND_PORT)  # 行情对象
    quote_context.subscribe(code_list=stock_codes, subtype_list=[TRADING_PERIOD])
    for stock_code in stock_codes:
        # quote_context.subscribe(code_list=[stock_code], subtype_list=[TRADING_PERIOD])
        ret, data = quote_context.get_cur_kline(code=stock_code, num=365, ktype=TRADING_PERIOD)
        if ret != RET_OK:
            print('获取K线失败：', data)
        else:
            stock_name = stock_dict[stock_code]
            close_list = data['close'].values.tolist()
            high_list = data['high'].values.tolist()
            low_list = data['low'].values.tolist()
            calculate_dual_ma(f"{stock_name}_{stock_code}", high_list, low_list, close_list)
