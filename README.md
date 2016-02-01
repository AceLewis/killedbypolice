#### killedbypolice
A Python script to process data from http://killedbypolice.net and display the statistics.

#### Introduction
The data used is solely from http://killedbypolice.net however the data is displayed in a big table and the statistics are not shown at all. This Python script takes the data and looks at the number of people that were killed by the USA police force and shows the percentages nicely. This code was used to make infographics on the race, gender, age, day of the week and cause of death.

#### Limitations
The data on http://killedbypolice.net is in a table but it is not 100% consistent on the layout and the HTML of the tables is difficult to parse. I had to use Selenium and Firefox to be able to get HTML that was parable for two of the years.

The data on http://killedbypolice.net may not contain all deaths. It also does not contain information on the race of 436 people (14.09%) was unknown, this is a significant amount. http://killedbypolice.net does not contain all causes of deaths, ages or genders however they were not as significant.

![Main infographic](/killed-by-police.png)

#### Other Infographics
All the infographics can be found on the project page https://acelewis.com/project/killedbypolice

#### Licenses
The code is licensed under GPL, the images are licensed under [Creative Commons Attribution-ShareAlike (CC BY-SA 3.0)](https://creativecommons.org/licenses/by-sa/3.0/)
