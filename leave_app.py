"""
This API file will generate Leave Type, Start Date and End Date.

App route with there functions:

/predict_leave -> Generate Json object with predicted leave type, start date and end date.
"""

import spacy
from spacy.tokens import DocBin
# from tqdm import tqdm
from datetime import datetime,date, timedelta
import re
import json
from flask import Flask, request, jsonify, render_template

"""
Loading NER models for dates and leave type prediction.

"""
date_prediction = spacy.load('./model-best-dates')
leavetype_prediction = spacy.load('./model-best-leavetype')

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """
    Frontend file will load here.
    """
    return render_template('index.html')

@app.route('/predict_leave', methods=['POST'])
def predict_leave():
    """
    From the frontend user will give query and stored in data variable.

    query will undergo in 2 ner models for leave prediction and dates.

    doc1 will store details for leave type prediction and doc will store details for dates predictions.

    1. data variable will go in leavetype_prediction and stored the detected leave type in list.
       From list we will retrieve leave type and stored in variable leave_type

    2. Now, data will go in date_prediction.
       a) data is having today keyword in query it will go in if statement and calculate start date and if no. of days is provided will calculate end date.
          If no. of days is not given we will give start date and end date null.

       b) In data if dates are not provided, it will give start date and end date will be null

       c) If dates are detected from data it will store in date_str list and extract start date and end date.
          It will validate if start date and end date is greater than today or not. If not greater than today it will provide none in start and end date.
          It will check whether end date is greater than start date or not. If not than again gives start and end dates null.
          After, checking above conditions if every conditions is false it will give detected start date and end date.

    return:
           json object that contains leave type, start date and end date.
    """
    #data = request.form.get('leaveQuery')
    d = request.get_json()
    data = d['leave_query']
    final_data = convert_date_format(data)
    print('')
    doc1 = leavetype_prediction(final_data)
    print(doc1)
    doc = date_prediction(final_data)
    # print(doc)
    # display = spacy.displacy.render(doc,style="ent",jupyter=True)
    # print(display)

    #Predicting Leave type
    try:   
        abc_str = []
        print(doc1.ents)
        for n in doc1.ents:
            abc_str.append(str(n))
        
        leave_type1 = abc_str[0]

    except Exception as e:
        print(e)
        return "Leave type not found",400
    # print("line 32: " + leave_type1)
    
    #Predicting Dates
    # keyword = 'Today'
    # found = re.findall(keyword, data, flags=re.IGNORECASE)
      # if found == "Today" or found == "today":
      #   Start,End = today_given(data)  
    try:
        if "today" in final_data.lower():
            Start,End = today_given(final_data)

        elif "tomorrow" in final_data.lower():
            Start,End = tomorrow_given(final_data)
    
        elif len(doc.ents)== 1 or len(doc.ents)== 0:
            Start,End= None, None
    
        #If user has provided dates then it will go in else
        else:
            date_str = []
            for n in doc.ents:
                date_str.append(str(n))      # tuples is converted to list
    
            start_date = datetime.strptime(date_str[0], '%d/%m/%Y').date()
            end_date = datetime.strptime(date_str[1], '%d/%m/%Y').date()
            start_3 = start_date .strftime('%d/%m/%Y')   #s100
            end_3 = end_date .strftime('%d/%m/%Y')    #e100
            
            if not validate_dates(start_date, end_date):
                Start, End= None,None
    
            else:
            # Check is start date is less than end date or not
                if(start_date > end_date):
                    Start, End = None, None
                    # ans6,ans16 = date_confirmation(start5,start5)
                    # return Start,End
    
            # if start date is less than end date than else will be executed
                else:
                    date6 = start_3 +","+ end_3
                    split_date_6 = date6.split(",")
                    Start = split_date_6[0]
                    End = split_date_6[1]
                    # ans7,ans17 = date_confirmation(Start,End)
                    # return Start,End
    except Exception as e:
        return "Dates invalid",400
            
    response = {
            "Leave Type": leave_type1,
            "Start Date": Start,
            "End Date": End
        }
    
    json_object = json.dumps(response, indent = 4) 
    # print(json_object)    
    return json_object

#if user provided dates in text so start date and end date both will be verified simultaneouly
def validate_dates(start_date, end_date):
    """
    We will check provided dates are greater than today or not.
    """
    today = datetime.today().date()
    if start_date < today or end_date < today:
        return False
    return True

def today_given(final_data):
    """
    We will calculate today's date and if no. of days provided we will calculate end date.

    No. of days no provided we will give start and end dates none.
    """
    number = re.findall(r'\d+', final_data)
    if len(number) == 0:
        if "tomorrow" in final_data.lower():
            Start = datetime.today()
            End = Start + timedelta(days=1)
            Start_final = Start.strftime('%d/%m/%Y')
            End_final = End.strftime('%d/%m/%Y')

        else:
            Start = datetime.today()
            End = datetime.today()
            Start_final = Start.strftime('%d/%m/%Y')
            End_final = End.strftime('%d/%m/%Y')
        
    else:
        num_days = int(number[0])
        Start = datetime.today()
        End = Start + timedelta(days=num_days)
        Start_final = Start.strftime('%d/%m/%Y')
        End_final = End.strftime('%d/%m/%Y')
        
    return Start_final, End_final

def tomorrow_given(final_data):
    """
    We will calculate today's date and if no. of days provided we will calculate end date.

    No. of days no provided we will give start and end dates none.
    """
    number = re.findall(r'\d+', final_data)
    if len(number) == 0:
        todaydate = datetime.today()
        Start = todaydate + timedelta(days=1)
        End = todaydate + timedelta(days=1)
        Start_final = Start.strftime('%d/%m/%Y')
        End_final = End.strftime('%d/%m/%Y')
        
    else:
        num_days = int(number[0])
        todaydate = datetime.today()
        Start = todaydate + timedelta(days=1)
        End = Start + timedelta(days=num_days)
        Start_final = Start.strftime('%d/%m/%Y')
        End_final = End.strftime('%d/%m/%Y')
        
    return Start_final, End_final
def convert_date_format(sentence):
    # Define the pattern to match dates like "14th May 2024" and "May 16 2024"
    try: 
        final_sentence = sentence.lower()
        pattern = r'(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})|(\w+)\s+(\d{1,2})(?:st|nd|rd|th)\s+(\d{4})'
        # Define a mapping of month names to numbers
        month_map = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12"
        }
        
        def replace_date(match):
            if match.group(1):  # Matches the first date format
                day = match.group(1).zfill(2)
                month = month_map[match.group(2)]
                year = match.group(3)
            else:  # Matches the second date format
                day = match.group(5).zfill(2)
                month = month_map[match.group(4)]
                year = match.group(6)
            return f'{day}/{month}/{year}'
            

    # Replace all dates in the sentence using the defined pattern and replacement function
        result = re.sub(pattern, replace_date, final_sentence)
        return result
        
    except Exception as e:
        # result = "Invalid Date format"
        return "Invalid Date format",400


if __name__ == '__main__':
    app.run(host="10.170.80.113",port="8039",debug=True)