import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go
import pandas as pd



# dfs에는 HTML 테이블을 포함하는 데이터프레임 리스트가 담겨 있을 것입니다.

# caching
# 인자가 바뀌지 않는 함수 실행 결과를 저장 후 크롬의 임시 저장 폴더에 저장 후 재사용
@st.cache_data
def get_stock_info():
    base_url = "http://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"
    url = f"{base_url}?method={method}"   
    df = pd.read_html(url, header=0, encoding='euc-kr')[0]
    df['종목코드'] = df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

# Function to get ticker symbol
def get_ticker_symbol(company_name):
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values
    if len(code) > 0:
        ticker_symbol = code[0]
    else:
        ticker_symbol = None  # Handle case where company name is not found
        st.error(f"'{company_name}'에 대한 종목 코드를 찾을 수 없습니다.")
    return ticker_symbol

# Streamlit app
def main():
    st.sidebar.write('## 회사 이름과 기간을 입력하세요')
    stock_name = st.sidebar.text_input("회사 이름")

    date_range = st.sidebar.date_input("시작일 - 종료일", (datetime.date(2019, 1, 1), datetime.date(2021, 12, 31)))
    button_key = "주가 데이터 확인 버튼"

    if st.sidebar.button('주가 데이터 확인', key=button_key):
        ticker_symbol = get_ticker_symbol(stock_name)
        if ticker_symbol is not None:
            start_p = date_range[0]
            end_p = date_range[1] + datetime.timedelta(days=1) 
            df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
            df.index = df.index.date
            st.subheader(f"[{stock_name}] 주가 데이터")
            st.dataframe(df.tail(7))

            # Plotting interactive chart using Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='주가'))
            fig.update_layout(title=f"{stock_name} 주가 차트", xaxis_title='날짜', yaxis_title='주가')
            st.plotly_chart(fig, use_container_width=True)

            # Excel download button
            excel_data = BytesIO()
            df.to_excel(excel_data, index=False)
            st.download_button("엑셀 파일 다운로드", excel_data, file_name='stock_data.xlsx')

            # CSV download button
            csv_data = df.to_csv(index=False).encode()
            st.download_button("CSV 파일 다운로드", csv_data, file_name='stock_data.csv')
        else:
            st.error("주가 데이터를 확인할 수 없습니다. 다시 시도해 주세요.")

if __name__ == "__main__":
    main()