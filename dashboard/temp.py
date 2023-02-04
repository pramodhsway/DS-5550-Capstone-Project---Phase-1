import pandas as pd

df = pd.read_csv('data/train.csv')
df['cfips'] = df['cfips'].apply(lambda x: '{0:0>5}'.format(x))

census_df = pd.read_csv('data/census_starter.csv')
census_df['cfips'] = census_df['cfips'].apply(lambda x: '{0:0>5}'.format(x))

# broadband_df = census_df[['pct_bb_2017', 'pct_bb_2018', 'pct_bb_2019', 'pct_bb_2020', 'pct_bb_2021', 'cfips']]
master_df = pd.merge(census_df, df, how="inner", on=["cfips"])
master_df = master_df.drop_duplicates('cfips')
print(master_df)
number = master_df.shape[0]

bb_df = master_df.filter(regex='pct_bb')
print(bb_df)

bb_stats = bb_df.describe()
print(bb_stats.loc['mean'])
for i in bb_stats.loc['mean']:
    print(i)

