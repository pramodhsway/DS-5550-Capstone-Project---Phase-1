import argparse
import json
import logging
import os
import sys
import pandas as pd
from scipy.stats import boxcox
from scipy.special import inv_boxcox
from prophet import Prophet
from tqdm import tqdm


def preprocess_data(args):
    train_path = os.path.join(args.source_dir, args.train_file)
    test_path = os.path.join(args.source_dir, args.test_file)
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    train_df[args.time_column] = pd.to_datetime(train_df[args.time_column], format = "%Y-%m-%d")

    # We add a small delta to 0's to perform the transformation
    train_df[args.target_column].replace({0:0.0000001}, inplace=True)

    # Rename the columns to ds and y as per prophet standards
    rename_columns = {args.time_column: "ds", args.target_column: "y"}

    train_df.rename(columns = rename_columns, inplace=True)


    return train_df, test_df


def run_prophet_model(args, train_df, test_df):

    # Perform Boxcox transformation on target column
    train_df['y'], lam = boxcox(train_df['y'])

    # Add a placeholder target for test_df 

    test_df[args.target_column] = 0

    print(test_df)

    for cfip in tqdm(train_df['cfips'].unique()[:10]):
        print(cfip)
    
        # Initialise model
        model = Prophet(seasonality_mode = args.seasonality_mode,
                        weekly_seasonality=False,
                        yearly_seasonality=False,
                        daily_seasonality=False,
                        n_changepoints=10,
                        changepoint_prior_scale=0.5,
                        growth='linear')
        
        # cfips_df = train_df[['ds', 'y']].loc[train_df['cfips'] == cfip]
                
        # # Fit model for the county
        # model.fit(cfips_df)
            
    #     # Get the predictions and stores them in the dataframe       
    #     future = model.make_future_dataframe(periods=8, freq='MS')    
    #     forecasts = model.predict(future)    
    #     acc_forecasts = inv_boxcox(forecasts['yhat'].tail(8), lam) 
    #     test_df['microbusiness_density'].loc[test_df['cfips'] == cfip] = acc_forecasts.values

    #     print(test_df.head())
        
    return None



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--source_dir", type=str)
    parser.add_argument("--train_file", type=str)
    parser.add_argument("--test_file", type=str)
    parser.add_argument("--seasonality_mode", choices=["additive", "multiplicative"], default="additive",
    )
    parser.add_argument("--time_column", type=str)
    parser.add_argument("--target_column", type=str)


    args, _ = parser.parse_known_args()

    #Set up logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.getLevelName("INFO"),
        handlers=[logging.StreamHandler(sys.stdout)],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Running the prophet model")

    train_df, test_df = preprocess_data(args)

    run_prophet_model(args, train_df, test_df)





