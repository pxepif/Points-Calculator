import os
from dotenv import load_dotenv
from geopy.distance import geodesic 
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
import pandas as pd

def writePingList(df, submissions):
    pingList = df["PingList"].tolist()
    submissionsUsers = [s[2] for s in submissions]
    for elem in pingList:
        if elem not in submissionsUsers:
            print("@"+elem)
    #end for
    return None

def writeBonusList(submissions):
    bonusList1000 = []
    bonusList750 = []
    bonusList500 = []
    bonusList = []
    for s in submissions:
        if s[4] == 1000:
            bonusList1000.append(s[2])
        elif s[4] == 750:
            bonusList750.append(s[2])
        elif s[4] == 500:
            bonusList500.append(s[2])
        elif s[4] == 250:
            bonusList.append(s[2])
            
    if (len(bonusList1000) > 0):
        print(f"+1000 points for finding the location first: @{bonusList1000[0]}")
    if (len(bonusList750) > 0):
        print(f"+750 points for finding the location second @{bonusList750[0]}", )
    if (len(bonusList500) > 0):
        print(f"+500 points for finding the location third @{bonusList500[0]}")
    if (len(bonusList) > 0):
        print(f"+250 points for finding the location:", end=" ")
        for i in range(len(bonusList)):
            print(f"@{bonusList[i]}", end = " ")
    return None

def calculatePoints(sheet):
    location = (-22.82961006324438, -43.00524615174737) #location for round

    #the first element is the coordinates, second is distance (to be calculated), third is username
    #fourth is whether they have submitted every round, fifth is bonus points.
    #  
    submissions = [
        [[-33.98904, 151.23584], 0, "user1", True, 0],
        [[-45.03512, 168.65204], 0, "user2", True, 0],
        [[38.78764, -9.39078], 0, "user3", True, 0], 
        [[20.62411, -87.07409], 0, "user4", True, 0], 
        [[16.83791, -25.05519], 0, "user5", True, 0], 
        [[16.83791, -25.05519], 0, "user6", False, 0], 
        [[24.95919, -80.57115], 0, "user7", True, 750],
        [[43.9472, 4.53404], 0, "user8", True, 0], 
        [[-23.76355, -65.47675], 0, "user9", True, 0], 
        [[24.86336, -80.67991], 0, "user10", True, 0],
        [[28.25816, -80.6038], 0, "user11", True, 0], 
        [[-22.98658, -43.24592], 0, "user12", True, 0], 
        [[-12.04413, -77.02702], 0, "user13", True, 0],
        [[-13.53713, -71.94379], 0, "user14", True, 0], 
        [[32.72145, -17.15727], 0, "user15", True, 0], 
        [[32.14026, -80.74921], 0, "user16", True, 0], 
        [[21.8185, -72.1477], 0, "user17", True, 0], 
        [[14.9108, -23.49961], 0, "user18", True, 1000], 
        [[47.56218, -52.70923], 0, "user19", True, 0], 
        [[41.23825, -8.67198], 0, "user20", False, 0],
        [[28.3032, -16.8158], 0, "user21", True, 0], 
        [[-22.8987, -43.20203], 0, "user22", True, 0], 
        [[18.3545, -64.57214], 0, "user23", False, 0],
        [[28.0549, -16.73041], 0, "user24", True, 0], 
        [[50.06599, -5.71477], 0, "user25", True, 0], 
        [[60.40056, 5.31619], 0, "user26", True, 0],
        [[24.89559, -80.66434], 0, "user27", False, 0], 
        [[18.41059, -77.11063], 0, "user28", False, 0],
        [[43.73513, 15.89073], 0, "user29", False, 0],
        [[43.66577, 7.20711], 0, "user30", False, 0]
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
    #casting to float to avoid implicit conversion error in future 
    df["Points"] = df["Points"].astype(float)
    df["Distance"] = df["Distance"].astype(float)
    
    bonusFlag = False #only make this true if I am actually updating the leaderboard.
    if (bonusFlag):
        while True:
            print("Type in 'CONFIRM' to proceed with updating bonuses:")
            userInput = input()
            if (userInput == "CONFIRM"):
                break
            else:
                print("Input not recognized, try again.")
        #end while
    for i in range(len(submissions)):
        print("Score for player " + submissions[i][2]+" is", end = " ")
        score = 0.25*((40000/2)-submissions[i][1])+5000*((len(submissions)-i-1)/(len(submissions)-1))+submissions[i][4]
        if (i==0):
            score+=3000
        elif (i==1):
            score+=2000
        elif (i==2):
            score+=1000
        #small area around antipode of the location for round where score would be negative, manually set to 0
        if (score < 0):
            score = 0
        print(round(score, 2), end = ", ")
        print("position " + str(i+1)+", distance "+str(round(submissions[i][1], 2)))

        df.at[submissions[i][2], "Points"] = round(score, 2) 
        if bonusFlag:
            df.at[submissions[i][2], "Total Bonuses"] += submissions[i][4]

        df.loc[df["Name2"] == submissions[i][2], "Distance"] = round(submissions[i][1], 2)
    #end for
    
    return df

def main():
    load_dotenv()  # loads variables from .env variable in actual code: not included for security reasons
    json_path = os.getenv("GOOGLE_SA_KEY")
    creds = gspread.service_account(filename=json_path)
    sheet = creds.open("TestSheet").sheet1

    data = calculatePoints(sheet)

    set_with_dataframe(sheet, data, col = 2)

    df2 = get_as_dataframe(sheet)
    print(df2)

if __name__ == "__main__":
    main()
