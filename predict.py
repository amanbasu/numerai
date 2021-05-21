import pandas as pd
import lightgbm as lgb
import numpy as np
import joblib
import numerapi
import pickle
import traceback
import os

test = False                # prevents from submissions during testing
logs = None                 # file for logging
chunksize = 500000  
neutralize_proportion = 0.45
dtype_dict = joblib.load('dtype_dict.joblib')
tournament_path = 'latest_numerai_tournament_data.csv.xz'
model_path = ['model/model_1.json', 'model/model_2.pkl']
model_keys = ['model/model_1_keys.joblib', 'model/model_2_keys.joblib']

def logging(line):
    logs.write(str(line) + '\n')
    print(line)

def get_model(num=1):
    logging('NUMERAI-INFO: getting model {} files'.format(num))
    if num == 1:
        try:
            model = lgb.Booster(model_file=model_path[0])
            keys = joblib.load(model_keys[0])
            logging('NUMERAI-INFO: model 1 info')
            return model, keys
        except Exception as e:
            logging('NUMERAI-ERROR: failed to get model 1 info')
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            logging(traceback_str)
    else:
        try:
            with open(model_path[1], 'rb') as file:
                model = pickle.load(file)
            keys = joblib.load(model_keys[1])
            logging('NUMERAI-INFO: model 2 info')
            return model, keys
        except Exception as e:
            logging('NUMERAI-ERROR: failed to get model 2 info')
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            logging(traceback_str)

def neutralize(series, by):
    scores = series
    exposures = by.values

    # constant column to make sure the series is completely neutral to exposures
    exposures = np.hstack((exposures, np.array([np.mean(scores)] * len(exposures)).reshape(-1, 1)))
    correction = neutralize_proportion * exposures.dot(np.linalg.pinv(exposures).dot(scores))
    corrected_scores = scores - correction
    corrected_scores = corrected_scores / corrected_scores.std()

    neutralized = pd.Series(corrected_scores.ravel(), index=series.index)
    return neutralized

def unif(df):
    x = (df.rank(method="first") - 0.5) / len(df)
    return pd.Series(x, index=df.index)

def get_prediction(model):
    logging('NUMERAI-INFO: getting predictions from model')
    og_ids = pd.DataFrame()
    preds = pd.DataFrame()
    # make prediction in chunks
    try:
        for idx, df in enumerate(pd.read_csv(tournament_path, chunksize=chunksize, iterator=True, dtype=dtype_dict)):
            logging('NUMERAI-INFO: prediction {} - chunk size {}'.format(idx+1, df.shape[0]))
            og_ids = pd.concat([og_ids, df['id']])
            feature_list = df.columns.drop('id').drop('era').drop('data_type').drop('target')
            df["predictions"] = model.predict(df[feature_list])
            
            # neutralize predictions
            logging('NUMERAI-INFO: neutralizing predictions')
            neut = pd.DataFrame()
            for _, x in df.groupby("era"):
                series = neutralize(pd.Series(unif(x["predictions"])), x[feature_list])
                df_ = pd.DataFrame({'id': x['id'], 'prediction_kazutsugi': series})
                neut = pd.concat([neut, df_])
            preds = pd.concat([preds, neut])

            # don't make complete predictions in test mode
            if test:
                break
            
    except Exception as e:
        logging('NUMERAI-ERROR: failed to make predictions')
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        logging(traceback_str)

    logging('NUMERAI-INFO: preparing prediction_kazutsugi dataframe')
    preds = preds.set_index('id')
    preds = preds.reindex(index=og_ids[0])
    preds = preds.reset_index()

    min_pre, max_pre = preds['prediction_kazutsugi'].min(), preds['prediction_kazutsugi'].max()
    preds['prediction_kazutsugi'] = (preds['prediction_kazutsugi'].values - min_pre) / (max_pre - min_pre)
    preds = preds.rename(columns={0: 'id'})

    logging('NUMERAI-INFO: dataframe - shape {}'.format(preds.shape))
    logging(preds.head(5))

    return preds

def make_submission(num=1):
    model, keys = get_model(num)
    predictions = get_prediction(model)
    
    # upload predictions
    predictions.to_csv("predictions.csv", index=False)
    napi = numerapi.NumerAPI(public_id=keys['public_id'], secret_key=keys['secret_key'])
    
    # do not submit in test mode
    if test:
        logging('NUMERAI-INFO: test successful')
        return

    submission_id = napi.upload_predictions("predictions.csv", model_id=keys['model_id'])
    logging('NUMERAI-INFO: submitted predictions from model {}'.format(num))

if __name__ == "__main__":
    logs = open('logs.txt', 'w+')
    test = False
    
    try:
        make_submission(num=1)
    except Exception as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        logging(traceback_str)

    try:
        make_submission(num=2)
    except Exception as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        logging(traceback_str)

    logs.close()

