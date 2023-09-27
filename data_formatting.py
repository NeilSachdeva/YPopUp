import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from os import name


if __name__ == "__main__":
    filepath1 = 'YPUBUP.csv'
    filepath2 = 'YCrushed.csv'
    filepath3 = 'YElements.csv'
    filepath4 = 'YFarm.csv'
    filepath5 = 'YFriends.csv'
    filepath6 = 'YMediterranea.csv'
    filepath7 = 'YMovies.csv'
    filepath8 = 'YPicnic.csv'

    df1 = pd.read_csv(filepath1)
    df1 = df1['email']


    df2 = pd.read_csv(filepath2)
    df2 = df2['Your Yale email address?']

    df3 = pd.read_csv(filepath3)
    df3 = df3['Your Yale email address?']

    df4 = pd.read_csv(filepath4)
    df4 = df4['Your Yale email address?']

    df5 = pd.read_csv(filepath5)
    df5 = df5['Your Yale email address?']

    df6 = pd.read_csv(filepath6)
    df6 = df6['Your Yale email address?']

    df7 = pd.read_csv(filepath7)
    df7 = df7['Your Yale email address?']

    df8 = pd.read_csv(filepath8)
    df8 = df8['Your Yale email address?']



    frames = [df1, df2, df3, df4, df5, df6, df7, df8]
    result = pd.concat(frames)


    times_applied_dict = {}
    for email in np.asarray(result):
        times_applied_dict[email] = times_applied_dict.get(email,0)+1


    emails = list(times_applied_dict.keys())
    times_applied = list(times_applied_dict.values())
    recent_reservation = [0] * len(emails)
    recent_emails = np.asarray(df1)

    for i in range(len(emails)):
        if(emails[i] in recent_emails):
            recent_reservation[i] = 1

    data = {'email': emails,'times_applied': times_applied,'recent_reservation': recent_reservation}

    df = pd.DataFrame(data)
    df = df.set_index('email')  

    dataset = pd.read_csv(filepath1)
    dataset = dataset.set_index('email')

    df1_reset = dataset.reset_index()
    df2_reset = df.reset_index()

    result = pd.merge(df1_reset, df2_reset, on='email', how='left')

    result.to_csv('POPUPdata.zip', index=False)
