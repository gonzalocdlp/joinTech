import requests
from bs4 import BeautifulSoup # webscrape
from collections import defaultdict # default dictionary: store a list with each key
import pandas as pd # DF
import re # regular expressions
import datetime # format date/time

def webscraper():
    # this was used for the person contacting me who had these details for their system
    headers = {
    "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

    # Skills & Place of Work
    skill = input('Enter your Skill: ').strip()
    place = input('Enter the location: ').strip()
    no_of_pages = int(input('Enter the # of pages to scrape: '))

    indeed_posts=[]

    for page in range(no_of_pages):
        url = 'https://www.indeed.com/jobs?q=' + skill + \
        '&l=' + place + '&sort=date' +'&start='+ str(page * 10)
        response = requests.get(url, headers=headers)
        html = response.text

    # Scrapping the Web
        soup = BeautifulSoup(html, 'lxml')
        

    # Outer Most Entry Point of HTML:
        outer_most_point=soup.find('div',attrs={'id': 'mosaic-provider-jobcards'})
    # "UL" lists where the data are stored:
        for i in outer_most_point.find('ul'):

            # Job Title:
            job_title=i.find('h2',{'class':'jobTitle jobTitle-color-purple jobTitle-newJob'})
            # print(job_title)
            if job_title != None:
            jobs=job_title.find('a').text


    


            # Company Name:
            if i.find('span',{'class':'companyName'}) != None:
            company=i.find('span',{'class':'companyName'}).text
            # Links:
            if i.find('a') != None:
            links=i.find('a',{'class':'jcs-JobTitle'})['href']
            # Salary if available:
            if i.find('div',{'class':'attribute_snippet'}) != None:
            salary=i.find('div',{'class':'attribute_snippet'}).text
            else:
            salary='No Salary'

        # Job Post Date:

            if i.find('span', attrs={'class': 'date'}) != None:
                post_date = i.find('span', attrs={'class': 'date'}).text

            # Put everything together in a list of lists for the default dictionary
            indeed_posts.append([company,jobs,links,salary, post_date])
            print(indeed_posts)
        # put together in list

        # (create a dictionary with keys and a list of values from above "indeed_posts")

    indeed_dict_list=defaultdict(list)

    # Fields for our DF

    indeed_spec=['Company','job','link','Salary','Job_Posted_Date']


    import re # regular expressions
    import datetime # format date/time

    # Let's deal with fixing posting dates using Regular Expressions

    indeed_jobs_df = pd.DataFrame(indeed_posts,columns=indeed_spec)


    dates_converted=[]

    for i in indeed_jobs_df['Job_Posted_Date']:

        if re.findall(r'[0-9]',i):
        # if the string has digits convert each entry to single string: ['3','0']->'30'
            b=''.join(re.findall(r'[0-9]',i))
        # convert string int to int and subtract from today's date and format
            g=(datetime.datetime.today()-datetime.timedelta(int(b))).strftime('%m-%d-%Y')

            dates_converted.append(g)
        # if i.find('today') or i.find('just posted'):
        # p=(datetime.datetime.today().strftime('%m-%d-%Y'))
        # v.append(p)
        else: # this will contain strings like: 'just posted' or 'today' etc before convert
            dates_converted.append(datetime.datetime.today().strftime('%m-%d-%Y'))
        dates_converted
    indeed_jobs_df['Job_Posted_Date']= dates_converted

    df = pd.DataFrame(indeed_posts,columns=indeed_spec)
    st.dataframe(df)