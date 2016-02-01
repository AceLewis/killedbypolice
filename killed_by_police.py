# 2015/11/14 - Alexander Lewis (AceLewis) https://AceLewis.com/projects/killedbypolice

import re
import math
from datetime import datetime
from collections import Counter
import operator
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
import requests

def open_browser():
    "Open the browser"
    driver = webdriver.Firefox()
    # Return driver so it can be used
    return driver

def get_html_selenium(driver, url):
    "Use selenium to get the html"
    driver.get(url)
    return driver.page_source

def get_html_requests(url):
    "Use requests to get the html"
    html_data = requests.get(url)
    return html_data.content

def tabularize_data(HTML):
    "Put data into a table so it is easy to process"
    # html5lib parser is lenient enough to not mess up
    soup = BeautifulSoup(HTML, 'html5lib')
    # Find the table
    table_body = soup.find_all("tbody")
    # Find all rows in the table
    rows = table_body[0].find_all_next("tr")

    # Initialise array
    table_array = []
    # Iterate through each row
    for row in range(1, len(rows)-1):
        cells = rows[row].find_all("td")
        # If 7 cells exist then it is a person else it is a month start
        if len(cells) == 7:
            # Find date
            date = cells[0]
            # Find state by state code
            state = cells[1].text.strip()
            # Extract text for the sex and race
            sex_race = cells[2].text.strip()
            # Initialise sex and race
            sex = []
            race = []

            # A for loop is needed as in some incidents the police kill more than one person
            # and theirfore more than one person's death will be in a cell

            # Find the sex and race if they are known
            for sex_race_str in cells[2].stripped_strings:
                sex_race = sex_race_str.split('/')
                # The race or sex may not be known so now to see what information is known
                if len(sex_race) == 0:
                    # Nothing is known
                    sex.append('?')
                    race.append('?')
                elif len(sex_race) == 1:
                    # Either race or sex is known
                    if sex_race[0] in ['M', 'F', 'T']:
                        sex.append(sex_race[0])
                        race.append('?')
                    else:
                        sex.append('?')
                        race.append(sex_race[0])
                elif len(sex_race) == 2:
                    # Both are known
                    sex.append(sex_race[0])
                    race.append(sex_race[1])

            # Initialise name and age
            name = []
            age = []
            # Again the name and age are not known for all people
            for name_string in cells[3].stripped_strings:
                # I could use the comma to seperate the name and age as the usual format is;
                # FirstName LastName, Age
                # However in very few cases the comma has been omitted by error so I chose to split
                # the name and age this way
                name_age = name_string.replace(',', '')
                name_age = name_age.split(' ')

                # See if age is known
                if name_age[-1].isdigit() and len(name_age) > 0:
                    age.append(name_age[-1])
                    name_age.pop()
                else:
                    age.append('?')

                # Construct name
                name_string = ' '.join(name_age)

                if len(name_string) > 0:
                    name.append(name_string)
                else:
                    name.append('?')

            how = []
            for how_string in cells[4].stripped_strings:
                if len(how_string) > 0:
                    how.append(how_string)
                else:
                    how.append('?')

            for i, this_date in enumerate(date.stripped_strings):
                # date_ = this_date.split(')')[1].strip()

                # The abouve code should work but for a few dates there is no
                # number in brackets, namely on the 10 August 5, 2015 and
                # January 14, 2015 so have to use this RegEx
                date_ = re.findall(r'([A-Z][0-9a-z ,]*)', this_date)[0].strip()
                sex_  = sex[i]  if i < len(sex)  else '?'
                race_ = race[i] if i < len(race) else '?'
                name_ = name[i] if i < len(name) else '?'
                age_  = age[i]  if i < len(age)  else '?'
                how_  = how[i]  if i < len(how)  else '?'

                table_array.append([date_, state, sex_, race_, name_, age_, how_])

    return table_array

def print_table(table):
    "Prints the table of data"
    for item in table:
        print("{:18s} State:{:2s} Sex:{} Race:{} Name:{:35s} Age: {:2s} How:{}"
              .format(item[0], item[1], item[2], item[3], item[4], item[5], item[6]))

def process_data(table):
    "Process data to get percentages and number of people killed for each thing"
    # Days of the week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Initialise arrays
    date = []
    weekday = []
    sex = []
    race = []
    age = []
    how = []

    # Put all data into the arrays
    for row in table:
        date.append(datetime.strptime(row[0], '%B %d, %Y'))
        weekday.append(days[datetime.strptime(row[0], '%B %d, %Y').weekday()])
        sex.append(row[2])
        race.append(row[3])
        if not row[5] == '?':
            age.append(int(row[5]))
        else:
            age.append(row[5])
        how.append(row[6])

    # Count all the sexes and races
    weekday_count = Counter(weekday)
    sex_count = Counter(sex)
    race_count = Counter(race)
    age_count = Counter(age)
    how_count = Counter(how)

    # Rename how letter to name
    how_names = {
        'G':'Gunshot',
        'V':'Vehicular',
        'R':'Restrainment',
        'T':'Taser',
        'C':'Custody'
        }
    how_count_named = Counter()

    for how_name in how_count:
        how_count_named.update({how_names.get(how_name, 'Unknown'): how_count[how_name]})

    # Sort the how in order of most killed to least
    sorted_how = sorted(how_count_named.items(), key=operator.itemgetter(1), reverse=True)

    # Catagorise small races in other
    race_count['O'] = race_count.pop('O', 0) + race_count.pop('PI', 0)+\
        race_count.pop('I', 0) + race_count.pop('A', 0) + race_count.pop('PK', 0)

    race_names = {
        'W':'White',
        'B':'Black',
        'L':'Latino',
        # 'PI':'Pasific Islands',
        # 'I':'Native American',
        # 'A':'Asian',
        'O':'Other'
    }

    race_count_named = Counter()

    for race_name in race_count:
        race_count_named.update({race_names.get(race_name, 'Unknown'): race_count[race_name]})

    # Sort the races in order of most killed to least
    sorted_race = sorted(race_count_named.items(), key=operator.itemgetter(1), reverse=True)

    return sex_count, sorted_race, sorted_how, date, weekday_count, age, age_count

def make_pie_chart(numbers, labels):
    "Function to make a pie chart"
    def make_autopct(values):
        "Nicely label the plot"
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return '{p:.2f}%  ({v:d})'.format(p=pct, v=val)
        return my_autopct
    # Plot the pie chart in a figure
    fig = plt.figure()
    fig.add_subplot(111, aspect='equal')
    plt.pie(numbers, labels=labels,
            autopct=make_autopct(numbers), shadow=True,)
    plt.show()

# Url's in 2016 the 2015 url will probably be simmilar to the 2013, 2014
# and that url will probably point to the 2016
url_2015 = "http://www.killedbypolice.net"
url_2014 = "http://www.killedbypolice.net/kbp2014.html"
url_2013 = "http://www.killedbypolice.net/kbp2013.html"

# Unfoutunatly the html.parse, and lxml parsers don't work for 2014
# and even worse the html5lib does not work for 2013 and 2015 so I
# had to find a work around using Firefox and Selenium it is a horrible
# hack and I want to find a way without using Selenium.
browser = open_browser()
html_2015 = get_html_selenium(browser, url_2015)
html_2014 = get_html_requests(url_2014)
html_2013 = get_html_selenium(browser, url_2013)
browser.close()

# Make tables from the html
table_2015 = tabularize_data(html_2015)
table_2014 = tabularize_data(html_2014)
table_2013 = tabularize_data(html_2013)

# Combine the years
table = table_2015 + table_2014 + table_2013

# Process the data
sex_count, race_count, how_count, date, weekday_count, age, age_count = process_data(table)

known_age = [x for x in age if x != '?']

bin_size = 10
max_age = max(known_age)
num_bins = math.ceil(max(known_age)/bin_size) + 1
max_bin = (num_bins-1)*bin_size + 1

# Put the ages into appropriate bins
binned_ages = np.histogram(known_age, bins=np.linspace(1, max_bin, num=num_bins))

total_killed = len(age)

known_race_count = [x for x in race_count if x[0] != 'Unknown']
total_known_race = sum([x[1] for x in known_race_count])

# Print the data nicely
print("In total there were {} people killed".format(total_killed))
print("The oldest person to be killed was {}".format(max_age))

print("The youngest person to be killed was {}\n".format(min(known_age)))

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

print("There were {} males killed and {} females, {} genders were unknown."
      .format(sex_count['M'], sex_count['F'], sex_count['?']+sex_count['T']))

print("\nThe races killed were:")
print("Race        |Number| Percent")
for _race, _nums in race_count:
    print("{:12s}:{:5d} :  {:.2%}".format(_race, _nums, _nums/total_killed))

print("\nThe known races killed were:")
print("Race        |Number| Percent")
for _race, _nums in known_race_count:
    print("{:12s}:{:5d} :  {:.2%}".format(_race, _nums, _nums/total_known_race))

print("\nHow the people were killed:")
print("How         |Number| Percent")
for _how, _nums in how_count:
    print("{:12s}:{:5d} :  {:.2%}".format(_how, _nums, _nums/total_killed))

print("\nThe days people were killed were:")
print("Weekday    | Num killed | Percent")
for weekday in weekdays:
    print("{:11s}:{:11d} : {:.2%}".format(weekday, weekday_count[weekday],
                                          weekday_count[weekday]/total_killed))

print("\nThe ages of the people killed were:")
print("Age range|Num killed|Percent")
for i, num in enumerate(binned_ages[0]):
    print("{:3d}-{:3d}  : {:8d} : {:.2%}".format(i*bin_size + 1, (i+1)*bin_size,
                                                 num, num/total_killed))

# Plot age of people killed
plt.hist(known_age, bins=np.linspace(0, 110, num=23))
plt.title("Age of people killed")
plt.xlabel("Age")
plt.ylabel("Number of people killed")
plt.show()
