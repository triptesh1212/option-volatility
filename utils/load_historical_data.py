import pandas as pd 

def get_historical_data() :

    df = pd.read_csv('dataset/spy_2020_2022.csv')

    # Data cleaning
    df.columns = df.columns.str.strip()

    df['lastTradeDate'] = pd.to_datetime(df['[QUOTE_DATE]'])

    df['expiration'] = pd.to_datetime(df['[EXPIRE_DATE]'])

    call_df = df[['[STRIKE]', '[C_LAST]', '[C_BID]', '[C_ASK]', '[C_VOLUME]', '[UNDERLYING_LAST]', 'lastTradeDate', 'expiration']].copy()
    call_df['option_type'] = 'call'
    call_df['lastPrice'] = call_df['[C_LAST]']
    call_df['bid'] = call_df['[C_BID]']
    call_df['ask'] = call_df['[C_ASK]']
    call_df['volume'] = call_df['[C_VOLUME]']
    call_df['strike'] = call_df['[STRIKE]']
    call_df['underlying_price'] = call_df['[UNDERLYING_LAST]']

    call_df = call_df.drop(['[C_LAST]', '[C_BID]', '[C_ASK]', '[C_VOLUME]', '[STRIKE]', '[UNDERLYING_LAST]'], axis=1)

    # Replace empty or whitespace strings with NaN
    call_df = call_df.replace(r'^\s*$', pd.NA, regex=True)

    call_df = call_df.dropna()

    call_df['days_to_expiry'] = (call_df['expiration'] - call_df['lastTradeDate']).dt.days

    # Filter for 2 to 4 weeks to expiry
    filtered_call_df = call_df[(call_df['days_to_expiry'] >= 14) & (call_df['days_to_expiry'] <= 28)]

    # Sort by lastTradeDate
    filtered_call_df = filtered_call_df.sort_values('lastTradeDate')

    # Group by lastTradeDate and pick the largest group
    group_sizes = filtered_call_df['lastTradeDate'].value_counts().sort_values(ascending=False)

    # Choose the top N dates that contribute to about 200k rows
    selected_dates = []
    total_rows = 0
    for date, count in group_sizes.items():
        if total_rows >= 200000:
            break
        selected_dates.append(date)
        total_rows += count

    filtered_call_df = filtered_call_df[filtered_call_df['lastTradeDate'].isin(selected_dates)]

    filtered_call_df = filtered_call_df.sample(n=200000, random_state=42) if len(filtered_call_df) > 200000 else filtered_call_df


    # put_df = df[['[STRIKE]', '[P_LAST]', '[P_BID]', '[P_ASK]', '[P_VOLUME]', '[UNDERLYING_LAST]', 'lastTradeDate', 'expiration']].copy()
    # put_df['option_type'] = 'put'
    # put_df['lastPrice'] = put_df['[P_LAST]']
    # put_df['bid'] = put_df['[P_BID]']
    # put_df['ask'] = put_df['[P_ASK]']
    # put_df['volume'] = put_df['[P_VOLUME]']
    # put_df['strike'] = put_df['[STRIKE]']
    # put_df['underlying_price'] = put_df['[UNDERLYING_LAST]']

    # put_df = put_df.drop(['[P_LAST]', '[P_BID]', '[P_ASK]', '[P_VOLUME]', '[STRIKE]', '[UNDERLYING_LAST]'], axis=1)

    # put_df = put_df.replace(r'^\s*$', pd.NA, regex=True) 

    # put_df = put_df.dropna() 

    # df = pd.concat([call_df, put_df], ignore_index=True)

    df = filtered_call_df

    return df