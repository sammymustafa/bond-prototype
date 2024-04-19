#!/usr/bin/env python
# coding: utf-8

# Load functions
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from datetime import datetime
import pycountry
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.utils import make_msgid
import ssl
import io
import sys
import os

# Save the current standard output
original_stdout = sys.stdout

# Redirect standard output to the string buffer
sys.stdout = io.StringIO()

# # Conditions
file_path = sys.argv[1]
with open(file_path, 'r') as file:
    data = json.load(file)
    
fname = data['fname']
lname = data['lname']
gender = data['gender']
birthdate = data['birthdate']
condition1 = data['condition1']
condition1snomed = data['condition1snomed']   
condition2 = data['condition2']
condition2snomed = data['condition2snomed']   
condition3 = data['condition3']
condition3snomed = data['condition3snomed']   
condition4 = data['condition4']
condition4snomed = data['condition4snomed']   
condition5 = data['condition5']
condition5snomed = data['condition5snomed']   
city = data['city']
state = data['state']
country = data['country']

# Conditions
def get_snomed_name(snomed_code):
    url = f'https://www.findacode.com/snomed/{snomed_code}.html'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')

    # Find the table with class 'edit-table'
    table = soup.find('table', class_='edit-table')

    if not table:
        return None
    
    # Find the cell that contains 'SNOMED code' and then get the following cell
    for row in table.find_all('tr'):
        header = row.find('th')
        if header and 'SNOMED code' in header.get_text():
            name_cell = row.find_next_sibling('tr').find('td')
            if name_cell:
                return name_cell.get_text(strip=True)
    
    # Return None if the name is not found
    return None

condition_names = [
    get_snomed_name(condition1snomed),
    get_snomed_name(condition2snomed),
    get_snomed_name(condition3snomed),
    get_snomed_name(condition4snomed),
    get_snomed_name(condition5snomed)
]
unique_condition_names = list(set(filter(None, condition_names)))
unique_condition_names.sort(key=len)

condition1 = unique_condition_names[0]
condition1_input = urllib.parse.quote(condition1)
condition2 = unique_condition_names[1]
condition2_input = urllib.parse.quote(condition2)

# Age
def calculate_age(dob_str):
    dob = datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def classify_age_group(dob_str):
    age = calculate_age(dob_str)
    if age <= 17:
        return "child"
    elif 18 <= age <= 64:
        return "adult"
    else:
        return "older"

age_input = classify_age_group(birthdate)

# Sex
def abbr_sex(gender):
    if gender == "Female":
        return "f"
    if gender == "Male":
        return "m"

sex_input = abbr_sex(gender)

# Country
def get_country_full_name(code):
    # First, try looking up by the alpha-2 code
    country = pycountry.countries.get(alpha_2=code)
    if country:
        return country.name
    # If that fails, try the alpha-3 code
    country = pycountry.countries.get(alpha_3=code)
    if country:
        return country.name
    # If both fail, return an error message
    return "Country code not found"

country_full = get_country_full_name(country)
country_input = urllib.parse.quote(country_full)

# State
def get_state_name(state_code):
    states = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    return states.get(state_code.upper(), "State code not found")

state_full = get_state_name(state)
state_input = urllib.parse.quote(state_full)

# City
city_input = urllib.parse.quote(city)


# # Personalized URLs

urls = [
    f'https://clinicaltrials.gov/search?cond={condition1_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&state={state_input}&city={city_input}&limit=100&term={condition2_input}',
       f'https://clinicaltrials.gov/search?cond={condition1_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&state={state_input}&limit=100&term={condition2_input}',
    f'https://clinicaltrials.gov/search?cond={condition1_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&limit=100&term={condition2_input}',
       f'https://clinicaltrials.gov/search?cond={condition1_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&state={state_input}&limit=100',
        f'https://clinicaltrials.gov/search?cond={condition1_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&state={state_input}&city={city_input}&limit=100',
       f'https://clinicaltrials.gov/search?cond={condition2_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&state={state_input}&city={city_input}&limit=100',
       f'https://clinicaltrials.gov/search?cond={condition2_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&state={state_input}&limit=100',
    f'https://clinicaltrials.gov/search?cond={condition1_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&limit=100',
        f'https://clinicaltrials.gov/search?cond={condition2_input}&aggFilters=ages:{age_input},healthy:y,sex:{sex_input},status:rec&country={country_input}&limit=100'
       ]


# # Finding Matching Trials

article_dicts = {}  # Dictionary to hold all article_dicts
base_url = 'https://clinicaltrials.gov/study/'
seen_nct_ids = set()

for index, url in enumerate(urls):
    article_dict = {}  # Reset article_dict for each URL
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    service = webdriver.ChromeService(executable_path='/Applications/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(service=service, options = options)
    driver.implicitly_wait(2)
    driver.get(url)
    section = driver.find_element(By.ID, 'searchResultsIntro')
    section_html = section.get_attribute('outerHTML')
    soup = BeautifulSoup(section_html, 'html.parser')
    
    results_range = soup.find(class_="shown-range font-body-md ng-star-inserted")
    if results_range and results_range.text.strip() == "No results":
        continue
    elif results_range:
        section = driver.find_element(By.CLASS_NAME, 'results-content-area')
        section_html = section.get_attribute('outerHTML')
        soup = BeautifulSoup(section_html, 'html.parser')
        study_cards = soup.find_all('div', class_='usa-card__container')

        for card in study_cards:
            # Find the checkbox input within the card and get its aria-label attribute
            checkbox = card.find('input', {'type': 'checkbox'})
            aria_label = checkbox['aria-label'] if checkbox else 'No title found'
            # Remove the "Select" part from the aria-label to get the title
            title_text = aria_label.replace('Select ', '').strip()
            # Find the div with the NCT ID and extract its text
            nct_id_div = card.find('div', class_='nct-id')
            nct_id = nct_id_div.get_text(strip=True) if nct_id_div else 'No NCT ID found'
            if nct_id not in seen_nct_ids:  # Check if the id is unique
                seen_nct_ids.add(nct_id)  # Add the id to the set of seen titles
                full_url = f'{base_url}{nct_id}'
                article_dict[title_text] = full_url

    driver.quit()

    # Remove duplicates for the current URL
    temp = {val: key for key, val in article_dict.items()}
    output_dict = {val: key for key, val in temp.items()}

    # Add the output_dict to the article_dicts with the index as the key
    article_dicts[f'article_dict_{index + 1}'] = output_dict


# # Formatting Output to User


# Formatting

# Find the first non-empty article_dict and print it with full details
criteria_full = [
    f'Reported diagnoses of {condition1} and {condition2}',
    'Age',
    'Gender identity',
    f'City: Located in {city}',
    f'State: Located in {state_full}',
    f'Country: Located in the {country}'
]

criteria_partials = {
    'article_dict_1': criteria_full,
    'article_dict_2': [  # matches condition1, condition2, age, gender, state, and country
        f'Reported diagnoses of {condition1} and {condition2}',
        'Age',
        'Gender identity',
        f'State: Located in {state_full}',
        f'Country: Located in the {country}'
    ],
    'article_dict_3': [  # matches condition1, condition2, age, gender, and country
        f'Reported diagnoses of {condition1} and {condition2}',
        'Age',
        'Gender identity',
        f'Country: Located in the {country}'
    ],
    'article_dict_4': [  # matches condition1, age, gender, state, and country
        f'Reported diagnosis of {condition1}',
        'Age',
        'Gender identity',
        f'State: Located in {state_full}',
        f'Country: Located in the {country}'
    ],
    'article_dict_5': [  # matches condition1, age, gender, city, state, and country
        f'Reported diagnosis of {condition1}',
        'Age',
        'Gender identity',
        f'City: Located in {city}',
        f'State: Located in {state_full}',
        f'Country: Located in the {country}'
    ],
    'article_dict_6': [  # matches condition2, age, gender, city, state, and country
        f'Reported diagnosis of {condition2}',
        'Age',
        'Gender identity',
        f'City: Located in {city}',
        f'State: Located in {state_full}',
        f'Country: Located in the {country}'
    ],
    'article_dict_7': [  # matches condition2, age, gender, state, and country
        f'Reported diagnosis of {condition2}',
        'Age',
        'Gender identity',
        f'State: Located in {state_full}',
        f'Country: Located in the {country}'
    ],
    'article_dict_8': [  # matches condition1, age, gender, and country
        f'Reported diagnosis of {condition1}',
        'Age',
        'Gender identity',
        f'Country: Located in the {country}'
    ],
    'article_dict_9': [  # matches condition2, age, gender, and country
        f'Reported diagnosis of {condition2}',
        'Age',
        'Gender identity',
        f'Country: Located in the {country}'
    ],
}

def format_criteria(criteria_list):
    # Keep only the first part of the criteria if it contains a colon
    processed_criteria = [criterion.split(':')[0] if ':' in criterion else criterion for criterion in criteria_list]
    if len(processed_criteria) > 2:
        return ', '.join(processed_criteria[:-1]) + ', and ' + processed_criteria[-1]
    else:
        return ' and '.join(processed_criteria)


# Adjust the print_studies function
def print_studies(article_dict, criteria, dict_number):
    # Printing the matching criteria
    print(f'These specific studies match your:')
    for criterion in criteria:
        print(f'  * {criterion}')
    print()

    # Printing the study names and URLs, limiting to the first 10 studies
    for title, study_link in list(article_dict.items())[:10]:
        print(f'* Study: {title} ({study_link})')

# print('The following clinical studies have been carefully curated to match your profile and are actively seeking participants. We recommend exploring these opportunities further to consider your involvement.')
# print('They are ordered by relevance to you/most criteria matches.\n')

# Iterate through the article dictionaries to print their details
for i, (dict_name, articles) in enumerate(article_dicts.items(), start=1):
    if articles:  # Check if the dictionary is not empty
        criteria = criteria_partials[dict_name]
        # Format the criteria in lowercase for subsequent dictionaries
        matched_criteria = format_criteria(list(map(str.lower, criteria)))
        if i == 1:  # For the first dictionary, print full details
            print_studies(articles, criteria, i)
        else:  # For subsequent dictionaries, print partial details
            print(f'These studies align with your {matched_criteria}:')
            # Print the studies, limiting to the first 10
            for title, study_link in list(articles.items())[:10]:
                print(f'* Study: {title} ({study_link})')
        print()  # Add an extra newline for spacing

# Retrieve the output from the string buffer
output = sys.stdout.getvalue()

# Reset the standard output to its original value
sys.stdout = original_stdout

def create_and_send_email(output_text, fname):
    # Set up Automatic Emailing
    smtp_server = "smtp.zoho.com"
    port = 587  # for starttls
    sender_email = "hello@bond-ehr.com"
    password = "Skinnybones73"  # Replace with your password
    receiver_email = "sammushms@gmail.com"
    subject = "Bond: Personalized Clinical Trials"
    
    # Create the root message and fill in the from, to, and subject headers
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email
    
    # Split the whole output into major sections based on "These studies align with your..."
    major_sections = output_text.split("\n\nThese studies align with your reported")

    # The first part will always be your intro section which contains the "These specific studies match your:" part
    intro_section = major_sections[0]
    intro_parts = intro_section.split("Study:")

    # Get intro bullets, exclude the first part as it is the intro text, not a bullet
    intro_bullets = intro_parts[0].strip().split('\n ')[1:]
    intro_bullets_html = "".join(f"<li>{bullet.strip()}</li>" for bullet in intro_bullets)
    intro_bullets_html = intro_bullets_html.replace("* ", "")
    intro_bullets_html = intro_bullets_html.replace("*", "")
    intro_bullets_html = intro_bullets_html.replace("\n\n", "\n")
    
    intro_studies = ""
    intro = [i.replace("*", "") for i in intro_parts[1:]]
    for i in intro:
        intro_study_bullets = "".join(f"<li>{'Study: ' + bullet.strip()}</li>" for bullet in i.split("\n") if bullet.strip())
        intro_studies += f"{intro_study_bullets}"

    # Process the remaining sections which start with "These studies align with your..."
    study_components_html = ""
    for section in major_sections[1:]:
        # Add back the header for each section
        header, *study_bullets = section.split("Study: ")
        study_bullets_html = "".join(f"<li>{'Study: ' + bullet.strip()}</li>" for bullet in study_bullets if bullet.strip())

        # Construct the HTML for this section
        study_components_html += f"<br><p class = 'medium-text'>These studies align with your reported {header.strip()}</p><ul class = 'standard'>{study_bullets_html}</ul><br>"
    study_components_html = study_components_html.replace("*", "")
    
    # Attach the border image
    border_cid = make_msgid(domain='example.com')[1:-1]  # Remove the <> around the ID
    border_path = '/Users/sammymustafa/Desktop/prototype/run/src/images/border.png'
    border_data = open(border_path, 'rb').read()
    border_html = MIMEImage(border_data, name=os.path.basename(border_path))
    border_html.add_header('Content-ID', f"<{border_cid}>")
    message.attach(border_html)
    
    # Attach the logo image
    logo_cid = make_msgid(domain='example.com')[1:-1]  # Remove the <> around the ID
    logo_path = '/Users/sammymustafa/Desktop/prototype/run/src/images/logo.png'
    logo_data = open(logo_path, 'rb').read()
    logo_html = MIMEImage(logo_data, name=os.path.basename(logo_path))
    logo_html.add_header('Content-ID', f"<{logo_cid}>")
    message.attach(logo_html)
        
    # HTML message
    html = f"""\
    <html>
      <head>
        <style>
          body {{
            font-family: trebuchet ms, sans-serif;
            background: #fef4db;
            margin: 0;
            padding: 0;
          }}
          .email-container {{
            background: white;
            width: 80%; /* Adjusted width */
            max-width: 800px; /* Set a maximum width */
            margin: 20px auto;
            border: 1px solid #dcdcdc;
          }}
          .email-container > *:not(.header-image) {{
              padding: 20px;
            }}
          .highlighted-text {{
              font-family: trebuchet ms, sans-serif;
              font-size: 1.2em;
              margin-bottom: 20px;
                }}
          .content-block {{
            margin-bottom: 40px; /* Increased space */
          }}
          .medium-text {{
              font-family: trebuchet ms, sans-serif;
              font-size: 1.14em;
              margin-bottom: 10px;
                }}
          ul.standard {{
          font-family: trebuchet ms, sans-serif;
            padding-left: 20px;
            margin: 0; /* Ensure text is next to bullet point */
            font-size: 1.08em;
          }}
          ul.special {{
          font-family: trebuchet ms, sans-serif;
            padding-left: 20px;
            margin: 0; /* Ensure text is next to bullet point */
            font-size: 1.15em;
          }}
          p {{
          font-family: trebuchet ms, sans-serif;
          }}
          .center-text {{
              text-align: center;
            }}
          li {{
              font-family: trebuchet ms, sans-serif;
            list-style-type: disc;
            margin-left: 10px; /* Ensure bullet points are aligned with text */
          }}
          .footer-text {{
          font-family: trebuchet ms, sans-serif;
            text-align: center;
            margin-top: 40px; /* Added space */
          }}
          .center-aligned {{
            text-align: center;
            margin-top: 20px;
          }}
          .header-image {{
            width: 100%;
            height: auto;
            border: 0;
            display: block;
          }}
          .footer {{
              background-color: #e8e4e4;
              color: #333; 
              padding: 10px 20px; 
              text-align: center;
            }}
          .footer-image {{
            width: 100px;
            height: auto;
            margin: 20px auto;
            display: block;
          }}
          .outer-container {{
              background: #f2f0f0;
              padding: 20px;
            }}
        </style>
      </head>
      <body>
          <div class="outer-container">
            <div class="email-container">
              <img src="cid:{border_cid}" alt="Top Border" class="header-image">
              <div style="padding: 30px;">
                  <h1 >Hi {fname}!</h1>
                  <p class="highlighted-text">The following clinical studies have been carefully curated to match your profile and are actively seeking participants. We recommend exploring these opportunities further to consider your involvement.</p>
                  <br>
                  <p class="highlighted-text">The clinical studies below are ordered by relevance to your patient profile and match your:</p>
                  <ul class = "special">
                    {intro_bullets_html}
                  </ul>
                  <br>
                  <br>
                  <ul class = "standard">
                      {intro_studies}
                  </ul>
                  <br>
                  {study_components_html}
                </div>
                <div style="padding: 30px;">
                <p class="medium-text">Please indicate your most important trial filters (location, condition, etc.) on our website for more curated recommendations in our biweekly emails.</p>
                </div>
            </div>
            <div class="footer-text">
                Please contact us if you would like to update your communication preferences.
                <br>hello@bond-ehr.com
                <br>Bond, 2024
              </div>
            <div class="center-aligned">
                <img src="cid:{logo_cid}" alt="Logo" style="width:100px;height:auto;">
              </div>
           </div> 
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part2 = MIMEText(html, 'html')
    message.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.send_message(message)
            print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


# Call the function with your output
create_and_send_email(output, fname.split()[0])