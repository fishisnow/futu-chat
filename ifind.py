import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Union, Set
from datetime import date

# 获取今天的日期并格式化
formatted_date = date.today().strftime('%Y-%m-%d')


refreshToken ='eyJzaWduX3RpbWUiOiIyMDI1LTAzLTIwIDIzOjE2OjE1In0=.eyJ1aWQiOiI3NzI0OTk4MTYiLCJ1c2VyIjp7ImFjY291bnQiOiJ5b25naHUxMTUiLCJhdXRoVXNlckluZm8iOnt9LCJjb2RlQ1NJIjpbXSwiY29kZVp6QXV0aCI6W10sImhhc0FJUHJlZGljdCI6ZmFsc2UsImhhc0FJVGFsayI6ZmFsc2UsImhhc0NJQ0MiOmZhbHNlLCJoYXNDU0kiOmZhbHNlLCJoYXNFdmVudERyaXZlIjpmYWxzZSwiaGFzRlRTRSI6ZmFsc2UsImhhc0Zhc3QiOmZhbHNlLCJoYXNGdW5kVmFsdWF0aW9uIjpmYWxzZSwiaGFzSEsiOnRydWUsImhhc0xNRSI6ZmFsc2UsImhhc0xldmVsMiI6ZmFsc2UsImhhc1JlYWxDTUUiOmZhbHNlLCJoYXNUcmFuc2ZlciI6ZmFsc2UsImhhc1VTIjpmYWxzZSwiaGFzVVNBSW5kZXgiOmZhbHNlLCJoYXNVU0RFQlQiOmZhbHNlLCJtYXJrZXRBdXRoIjp7IkRDRSI6ZmFsc2V9LCJtYXhPbkxpbmUiOjUwMCwibm9EaXNrIjpmYWxzZSwicHJvZHVjdFR5cGUiOiJTVVBFUkNPTU1BTkRQUk9EVUNUIiwicmVmcmVzaFRva2VuRXhwaXJlZFRpbWUiOiIyMDI1LTA0LTA2IDE3OjEwOjQ4Iiwic2Vzc3Npb24iOiIzNDI5YzU4NTFmMDE2MDA3MWEyMmFjZWQ2YzlkNGZjZSIsInNpZEluZm8iOnt9LCJ0cmFuc0F1dGgiOmZhbHNlLCJ1aWQiOiI3NzI0OTk4MTYiLCJ1c2VyVHlwZSI6IkZSRUVJQUwiLCJ3aWZpbmRMaW1pdE1hcCI6e319fQ==.35375B4B2408EB792ED49CB4D72F7D310D76AC51B4C042DEEB3CE3537CBD2711'

# 全局变量用于存储 token 和最后获取时间
_cached_access_token = None
_last_token_time = None

def get_access_token():
    global _cached_access_token, _last_token_time
    
    # 检查是否需要重新获取 token
    current_time = datetime.now()
    if (_cached_access_token is None or 
        _last_token_time is None or 
        current_time - _last_token_time > timedelta(days=7)):
        
        getAccessTokenUrl = 'https://ft.10jqka.com.cn/api/v1/get_access_token'
        getAccessTokenHeader = {"Content-Type":"application/json","refresh_token":refreshToken}
        getAccessTokenResponse = requests.post(url=getAccessTokenUrl,headers=getAccessTokenHeader)
        _cached_access_token = json.loads(getAccessTokenResponse.content)['data']['access_token']
        _last_token_time = current_time
    
    return _cached_access_token

def get_real_time_quotation(codes, indicators=None):
    """
    获取实时行情数据
    :param codes: 股票代码列表，例如 ['300033.SZ', '600030.SH']
    :param indicators: 指标列表，默认为 ['changeRatio', 'volume']
    :return: 行情数据的字典
    """
    if indicators is None:
        indicators = ['changeRatio', 'volume']
    
    # 获取访问令牌
    access_token = get_access_token()
    
    # 准备请求URL和数据
    url = 'https://ft.10jqka.com.cn/api/v1/real_time_quotation'
    
    # 准备表单数据
    form_data = {
        'codes': ','.join(codes) if isinstance(codes, list) else codes,
        'indicators': ','.join(indicators) if isinstance(indicators, list) else indicators
    }
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'access_token': access_token
    }
    
    # 发送请求
    response = requests.post(url=url, data=form_data, headers=headers)
    
    # 返回解析后的JSON数据
    return json.loads(response.content)

def process_quotation_data(data: Dict) -> Dict[str, List[str]]:
    """
    处理实时行情数据，将结果转换为按指标分组并排序的字典
    :param data: API返回的原始数据
    :return: 按指标分组并排序的字典，格式为 {indicator: [sorted_codes]}
    """
    if data.get('errorcode') != 0:
        raise Exception(f"API返回错误: {data.get('errmsg')}")
    
    # 获取所有指标
    indicators = [item['itemid'] for item in data['datatype']]
    result = {indicator: [] for indicator in indicators}
    
    # 收集每个指标的数据
    for table in data['tables']:
        code = table['thscode']
        for indicator in indicators:
            try:
                # 获取该股票该指标的值，处理可能的空值情况
                value = table['table'].get(indicator, [None])[0]
                # 如果值为 None 或者不是数字，跳过这个股票
                if value is not None and isinstance(value, (int, float)):
                    result[indicator].append((code, value))
            except (KeyError, IndexError, TypeError):
                # 如果获取数据出错，跳过这个股票
                continue
    
    # 对每个指标的数据进行排序
    for indicator in indicators:
        # 按值降序排序，只保留股票代码
        result[indicator] = [item[0] for item in sorted(result[indicator], 
                                                      key=lambda x: x[1], 
                                                      reverse=True)]
    
    return result

def get_high_volume_and_change_stocks(A_codes: List[str], top_n: int = 50) -> Dict[str, List[Dict]]:
    """
    获取涨幅和成交量都较高的股票
    :param A_codes: A股股票代码列表
    :param top_n: 前多少名，默认50
    :return: 包含四个列表的字典：涨幅前N，成交量前N，成交额前10，以及涨幅和成交量的交集
    """
    try:
        # 获取行情数据
        raw_data = get_real_time_quotation(A_codes, ['changeRatio', 'volume', 'amount'])
        processed_data = process_quotation_data(raw_data)
        
        # 获取涨幅前N和成交量前N的股票代码
        top_change_codes = processed_data['changeRatio'][:top_n]
        top_volume_codes = processed_data['volume'][:top_n]
        top_amount_codes = processed_data['amount'][:top_n]  # 获取成交额前10
        
        # 计算交集
        intersection_codes = list(set(top_change_codes) & set(top_volume_codes))
        
        # 获取所有需要查询基本信息的股票代码
        all_codes = list(set(top_change_codes + top_volume_codes + top_amount_codes))
        
        # 获取基本信息
        basic_info = get_basic_info(all_codes)
        
        # 处理基本信息数据
        stock_info = {}
        if basic_info.get('tables'):
            for table in basic_info['tables']:
                code = table['thscode']
                name = table['table'].get('ths_stock_short_name_stock', [''])[0]
                pe = table['table'].get('ths_pe_mrq_stock', [''])[0]
                stock_info[code] = {
                    'code': code,
                    'name': name,
                    'pe': pe
                }
        
        # 获取行情数据
        quotation_data = get_real_time_quotation(all_codes, ['changeRatio', 'volume', 'amount'])
        if quotation_data.get('tables'):
            for table in quotation_data['tables']:
                code = table['thscode']
                if code in stock_info:
                    stock_info[code]['changeRatio'] = table['table'].get('changeRatio', [0])[0]
                    stock_info[code]['volume'] = table['table'].get('volume', [0])[0]
                    stock_info[code]['amount'] = table['table'].get('amount', [0])[0]
        
        # 构建结果
        def create_stock_list(codes):
            return [stock_info.get(code, {
                'code': code,
                'name': '未知',
                'pe': '未知',
                'changeRatio': 0,
                'volume': 0,
                'amount': 0
            }) for code in codes]
        
        return {
            'top_change': create_stock_list(top_change_codes),
            'top_volume': create_stock_list(top_volume_codes),
            'top_amount': create_stock_list(top_amount_codes),
            'intersection': create_stock_list(sorted(intersection_codes))
        }
        
    except Exception as e:
        print(f"获取数据时发生错误: {str(e)}")
        return {
            'top_change': [],
            'top_volume': [],
            'top_amount': [],
            'intersection': []
        }

def get_basic_info(codes: Union[str, List[str]]) -> Dict:
    """
    获取股票的基本信息数据
    :param codes: 股票代码或股票代码列表，例如 '300033.SZ' 或 ['300033.SZ', '600030.SH']
    :param indicators: 指标列表，例如 ['name', 'industry', 'market_value']，默认为None获取所有指标
    :return: 基本信息数据的字典
    """
    # 获取访问令牌
    access_token = get_access_token()
    
    # 准备请求URL
    url = 'https://ft.10jqka.com.cn/api/v1/basic_data_service'
    
    # 准备请求数据
    form_data = {
        'codes': ','.join(codes) if isinstance(codes, list) else codes,
        "indipara":[{"indicator":"ths_stock_short_name_stock","indiparams":[]},{"indicator":"ths_pe_mrq_stock","indiparams":[f"{formatted_date}"]},{"indicator":"ths_the_concept_stock","indiparams":[f"{formatted_date}"]}]
    }
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/json',
        'access_token': access_token
    }
    
    try:
        # 发送请求
        response = requests.post(url=url, json=form_data, headers=headers)
        result = json.loads(response.content)
        
        if result.get('errorcode') != 0:
            raise Exception(f"API返回错误: {result.get('errmsg')}")
            
        return result
        
    except Exception as e:
        print(f"获取基本信息数据时发生错误: {str(e)}")
        return {'errorcode': -1, 'errmsg': str(e), 'data': None}

if __name__ == "__main__":
    # 从文件读取 A 股代码
    with open('stocks/A_code.txt', 'r') as f:
        A_codes = f.read().strip().split(',')
    
    print(f"总共读取到 {len(A_codes)} 个股票代码")
    
    # 获取涨幅和成交量前50的股票
    result = get_high_volume_and_change_stocks(A_codes, top_n=50)
    
    print("\n高成交量和高涨幅股票结果:")
    print("涨幅前50:")
    for i, stock in enumerate(result['top_change'], 1):
        print(f"{i}. {stock['code']} - {stock['name']} (市盈率: {stock['pe']})")
    
    print("\n成交量前50:")
    for i, stock in enumerate(result['top_volume'], 1):
        print(f"{i}. {stock['code']} - {stock['name']} (市盈率: {stock['pe']})")
    
    print("\n同时在涨幅和成交量前50的股票:")
    for i, stock in enumerate(result['intersection'], 1):
        print(f"{i}. {stock['code']} - {stock['name']} (市盈率: {stock['pe']})")