import pandas as pd 

df_weather = pd.read_csv('../source/weather.csv')
#df_weather = pd.read_csv('../source/weather_test.csv')
#df_flights_1 = pd.read_csv('../source/ontime/On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2021_1.csv', low_memory=False)
df_flights_1 = pd.read_csv('../source/ontime/delay_test.csv')


#Plik z pogodą ma w sobie dane dotyczące też innych lat niż 2021, niepotrzebne do reszty zadań
def cutFile(df_weather):
    df_needed_data = df_weather[df_weather['StartTime(UTC)'].str.contains("2021-")]
    return df_needed_data[['Type', 'Severity', 'StartTime(UTC)', 'City']]

def splitDate(df_weather):
    df_weather.rename(columns={'StartTime(UTC)':'FlightDate'}, inplace=True)
    return df_weather
    
#Plik z danymi o lotach ma wiele niepotrzebnych kolumn
def cutFlightData(df):
    return df[['Reporting_Airline', 'OriginCityName', 'DestCityName', 'DepDelay', 'ArrDelay', 'FlightDate', 'DepTime']]

#Zaokroąglanie czasu, żeby porownac godziny
def roundTime(df):
    splitDate = df['FlightDate'].str.split(' ', expand=True)
    splitDate2 = splitDate[1].str.replace(':', '.').str[:5].astype(float).round().astype(str).str.replace('.', ':')
    df['FlightDate'] = splitDate[0] + ' ' + splitDate2
    return df
    
#Miasta mają niepotrzebnie stan
def changeCityValue(df):
   
    splitCities = df['OriginCityName'].str.split(',', expand=True)
    del splitCities[1]
    df['OriginCityName'] = splitCities
    splitCities2 = df['DestCityName'].str.split(',', expand=True)
    del splitCities2[1]
    df['DestCityName'] = splitCities2
    df.rename(columns={'OriginCityName':'City'}, inplace=True)
    return df.dropna()

def editTimeValues(df):
    for i in range(len(df)):
        var = str(df.iloc[i][6]).split('.')[0]
        var = var[:2] + ':' + var[2:]
        df.at[i, 'DepTime'] = var
    return df

#Dodanie godziny do daty
def changeDateColumn(df):
    
     df['FlightDate'] = df['FlightDate'].astype(str) + ' ' + df['DepTime'].astype(str)
     return df

#Liczenie całkowitych opóźnien dla każdego lotu
def totalDelay(df):
   totalDelay = df['DepDelay'] + df['ArrDelay']
   df.insert(7, 'TotalDelay', totalDelay)
   return df
    

#Maksymalne opróźnienia dla każdego miasta
def maxDelayEachCity(df, df_weather):
    df_max_delay = []
    #grupowanie po mieście
    for city, df_city in df.groupby('City'):
        #nowy data frame zawierający maksymalne opóźnienia
        merged = df_city.loc[df['TotalDelay'] == df_city['TotalDelay'].max()].merge(df_weather, on=['City', 'FlightDate'])
        if len(merged) != 0:
            df_max_delay.append(merged)
    return df_max_delay

#Maksymalne opróźnienia dla każdej pogody
def maxDelayWeather(df, df_weather):
    merged = df_weather.merge(df, on=['City', 'FlightDate'])
    print(merged.groupby('Type')['TotalDelay'].max())
    
#Średnie opróźnienia dla każdej pogody
def avgDelay(df, df_weather):
    merged = df_weather.merge(df, on=['City', 'FlightDate'])
    return merged.groupby(['Type', 'Severity'], as_index=False)['TotalDelay'].mean()

#Różnica między faktycznym opóźnieniem a średnim dla danej pogody
def delayDifference(df, avd_delay_weather):
    delay_diff = []
    avg_delay = []
    avd_delay_weather = dict(zip(zip(avd_delay_weather['Type'], avd_delay_weather['Severity']), avd_delay_weather['TotalDelay']))    
    for i in range(len(df)):
        delay = avd_delay_weather[str(df.iloc[i]['Type']), str(df.iloc[i]['Severity'])]
        avg_delay.append(delay)
        delay_diff.append(abs(df.iloc[i]['TotalDelay']-delay))
    df.insert(9, 'DelayDiff', delay_diff)
    df.insert(8, 'AvgDelay', avg_delay)
    return df

#Stosunek opóźnień
def deportToArrival(df):
    quotients = []
    for i in range(len(df)):     
        quotients.append(df.iloc[i]['DepDelay'] / df.iloc[i]['ArrDelay'])
    df.insert(8, 'Dep/Arr', quotients)
    return df

#Pogoda w miejscu wylotu i przylotu
def depArrWeather(df, df_weather):
   df_dest = df.merge(df_weather, left_on=['DestCityName', 'FlightDate'], right_on=['City', 'FlightDate'])[['DepDelay', 'City_x', 'DestCityName',
                                                                                'ArrDelay', 'TotalDelay', 'Dep/Arr', 'Type', 'Severity', 'FlightDate']]
   df_dest.rename(columns={'City_x': 'City'}, inplace=True)
   df_dest=df_dest.merge(df_weather, on=['City', 'FlightDate'])
   df_dest.rename(columns={'Type_x': 'WeatherDep', 'Type_y':'WeatherArr', 'Severity_x':'SeverityDep', 'Severity_y':'SeverityArr'}, inplace=True)
   print(df_dest)
    
    

def main():
    delays = totalDelay(cutFlightData(df_flights_1))
    delays = changeCityValue(delays)
    df_weather2 = cutFile(df_weather)
    df_weather2 = splitDate(df_weather2)
    weatherRound = roundTime(df_weather2)
    editedTime = editTimeValues(delays)
    changedDate = changeDateColumn(editedTime)   
    delayRound = roundTime(changedDate)
   
   
    # maxDelay = maxDelayEachCity(delayRound, weatherRound)
    # df_maxDelay = pd.concat(maxDelay)
    # print(df_maxDelay)
    
    #maxDelayWeather(delayRound, weatherRound)
    # avdDelay_W = avgDelay(delayRound, weatherRound)
    # delaydiff = delayDifference(delayRound.merge(weatherRound, on=['City', 'FlightDate']), avdDelay_W)
    # print(delaydiff)
    
    depArr = deportToArrival(delayRound)
    depArrWeather(depArr, weatherRound)
        
 
    
main()
