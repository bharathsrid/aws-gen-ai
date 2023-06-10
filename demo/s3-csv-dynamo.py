
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
    # convert the date column to string
    df['date'] = df['date'].astype(str)
    return df

# a function to create a dynamo db table with name passed as parameter and update the passed dataframe as data with date column as the partition key

def create_dynamo_table(table_name, df):
    import boto3
    import pandas as pd
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'date',
                'KeyType': 'HASH'  #Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    table.wait_until_exists()
    table.put_item(Item=df.iloc[0].to_dict())
    return table






# create function called main
def main():
    # call the function read_csv_from_s3
    df = read_csv_from_s3('bharsrid-demo-personal-genai', 'biostats.csv')
    # call the function add_date_column
    df = add_date_column(df)
    # call the function create_dynamo_table
    table = create_dynamo_table('bharsrid-demo-personal-genai-dynamo', df)
    print(df)



# create the if main block
if __name__ == '__main__':
    main()