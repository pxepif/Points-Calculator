import math
from geopy.distance import geodesic 
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
import pandas as pd
from google.oauth2.service_account import Credentials

#note: what to do next, how to clear the previous element in a name if there's no submission for said person
def calculatePoints(sheet):
    location = (-22.82961006324438, -43.00524615174737) #location for round

    #will just copy and paste from that sheet into the real leaderboard for points.
    submissions = [
                #[[-33.98904, 151.23584], 0, "user1", True, 0],
                #[[-45.03512, 168.65204], 0, "user2", True, 0],
                #[[38.78764, -9.39078], 0, "insomnia", True, 0], 
                #[[20.62411, -87.07409], 0, "Dr.Clive", True, 0], 
                #[[16.83791, -25.05519], 0, "Jonexo", True, 0], 
                #[[16.83791, -25.05519], 0, "Geospot", False, 0], 
                #[[24.95919, -80.57115], 0, "OkObern", True, 750],
                #[[43.9472, 4.53404], 0, "vegetal", True, 0], 
                #[[-23.76355, -65.47675], 0, "Talking Nonsense", True, 0], 
                #[[24.86336, -80.67991], 0, "Tones", True, 0],
                #[[28.25816, -80.6038], 0, "Chicago Geographer", True, 0], 
                #[[-22.98658, -43.24592], 0, "maplemanatee", True, 0], 
                #[[-12.04413, -77.02702], 0, "rhoticity", True, 0],
                #[[-13.53713, -71.94379], 0, "BD82", True, 0], 
                #[[32.72145, -17.15727], 0, "DjinN", True, 0], 
                #[[32.14026, -80.74921], 0, "Arctic94", True, 0], 
                #[[21.8185, -72.1477], 0, "Jack", True, 0], 
                #[[14.9108, -23.49961], 0, "Muik", True, 1000], 
                #[[47.56218, -52.70923], 0, "Mina", True, 0], 
                #[[41.23825, -8.67198], 0, "Bobio", False, 0],
                #[[28.3032, -16.8158], 0, "Finland Taipan", True, 0], 
                #[[-22.8987, -43.20203], 0, "alexaletorneau", True, 0], 
                #[[18.3545, -64.57214], 0, "el", False, 0],
                #[[28.0549, -16.73041], 0, "blastoform", True, 0], 
                #[[50.06599, -5.71477], 0, "Flex06", True, 0], 
                #[[60.40056, 5.31619], 0, "FurkanSevim", True, 0],
                #[[24.89559, -80.66434], 0, "Major Bajor", False, 0], 
                #[[18.41059, -77.11063], 0, "maccem", False, 0],
                #[[43.73513, 15.89073], 0, "bcz_idk", False, 0],
                #[[43.66577, 7.20711], 0, "Arcturus", False, 0]
            ]

    for i in range(len(submissions)):
        submissions[i][1] = geodesic(submissions[i][0], location).km

    submissions.sort(key = lambda x: x[1]) #sorts submissions by distance (x[1])

    for i in range(len(submissions)):
        print(submissions[i][0], submissions[i][1])

    # read current sheet into a DataFrame
    df = get_as_dataframe(sheet, evaluate_formulas=True)
    df.set_index("Name", inplace=True)

    #resets points to 0 before updating
    df["Distance"] = 0
    df["Points"] = 0
    
    flag = False #only make this true if I am actually updating the leaderboard.
    for i in range(len(submissions)):
        print("Score for player " + submissions[i][2]+" is", end = " ")
        score = 0.25*((40000/2)-submissions[i][1])+5000*((len(submissions)-i-1)/(len(submissions)-1))+submissions[i][4]
        if (i==0):
            score+=3000
        elif (i==1):
            score+=2000
        elif (i==2):
            score+=1000
        print(round(score, 2), end = ", ")
        print("position " + str(i+1)+", distance "+str(round(submissions[i][1], 2)))

        df.at[submissions[i][2], "Points"] = round(score, 2)
        if flag:
            df.at[submissions[i][2], "Total Bonuses"] += submissions[i][4]

        df.loc[df["Name2"] == submissions[i][2], "Distance"] = round(submissions[i][1], 2)
    #end for
    
    return df

def main():
    #Note: make sure to hide the actual account name if i push this to github to show. 
    creds = gspread.service_account("insertGspreadAccountName.json")
    sheet = creds.open("TestSheet").sheet1

    data = calculatePoints(sheet)

    set_with_dataframe(sheet, data, col = 2)

    df2 = get_as_dataframe(sheet)
    print(df2)

if __name__ == "__main__":
    main()
