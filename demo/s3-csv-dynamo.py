
# Created on Wed Apr  3 15:53:10 2019
#

# a function to read csv file from s3 return as a pandas dataframe
def read_csv_from_s3(bucket, key):
    import boto3
    import pandas as pd
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    df = pd.read_csv(obj.get()['Body'])
    return df

# a function to add a date column to a pandas dataframe and populate it with one day increment per row starting 01-Jan2010 on first row
def add_date_column(df):
    import pandas as pd
    df['date'] = pd.date_range('01-Jan2010', periods=len(df), freq='D')
    return df

# create function called main
def main():
    # call the function read_csv_from_s3
    df = read_csv_from_s3('bharsrid-demo-personal-genai', 'biostats.csv')
    # call the function add_date_column
    df = add_date_column(df)
    print(df)



# create the if main block
if __name__ == '__main__':
    main()