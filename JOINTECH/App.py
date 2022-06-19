from numpy import place
import streamlit as st
import pandas as pd
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
import requests
from bs4 import BeautifulSoup # webscrape
from collections import defaultdict # default dictionary: store a list with each key
import pandas as pd # DF
import re # regular expressions
import datetime # format date/time
import nltk
def table_download(df,filename,text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() 
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def read_pdf(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text

def view_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


connection = pymysql.connect(host='localhost',user='root',password='',db='sra')
cursor = connection.cursor()

def data_insert_to_table(name,email,timestamp,skills):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s)"""
    rec_values = (name, email,timestamp,skills)
    cursor.execute(insert_sql)
    connection.commit()

st.set_page_config(
   page_title="JoinTech",
   page_icon='./Logo/Join-Tech-Logo.png',
)
def run():
    img = Image.open('./Logo/Join-Tech-Logo.png')
    img = img.resize((250,250))
    st.image(img)
    st.title("JoinTech Search Engine")
    st.sidebar.markdown("")
    options = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", options)

    

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Skills VARCHAR(300) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if  choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:

            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            view_pdf(save_image_path)
            userresume = ResumeParser(save_image_path).get_extracted_data()
            if userresume:
                ## Get the whole resume data
                resume_text = read_pdf(save_image_path)

                st.header("JoinTech Resumes")
                st.success("Hello "+ userresume['name'])
                st.subheader("Basic info")
                try:
                    st.text('Name: '+userresume['name'])
                    st.text('Email: ' + userresume['email'])
                    st.text('Contact: ' + userresume['mobile_number'])
                    
                except:
                    pass
            

                
                ## Skill shows
                keywords = st_tags(label='Skills',
                text='',
                    value=userresume['skills'],key = '1')

 
                my_form = st.form(key = "form1")
                skillinput = my_form.text_input(label = "What job would you like to search for?").strip()
                placeinput = my_form.text_input('Where is your job location? ').strip()
                my_form.form_submit_button(label = "Submit this form") 
                if my_form.form_submit_button:
                    st.write("Result")
                    
                      # this was used for the person contacting me who had these details for their system
                    headers = {
                    "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

                    # Skills & Place of Work
                    skill = skillinput
                    place = placeinput
                    no_of_pages = 5

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
                            linksurl=i.find('a',{'class':'jcs-JobTitle'})['href']
                            links= "indeed.com"+linksurl
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
                    indeed_jobs_df['Job_Posted_Date']= dates_converted
                    df = pd.DataFrame(indeed_posts,columns=indeed_spec)
                    print(df)
                    st.dataframe(df)
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)
                data_insert_to_table(userresume['name'], userresume['email'], timestamp,
                               str(userresume['skills']))
                connection.commit()
            else:
                st.error('Error')
    else:
        ## Admin Side
        st.success('Welcome to Admin')
        admin_user = st.text_input("Username")
        admin_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if admin_user == 'admin' and admin_password == 'admin':
                st.success("Admin")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("User Data")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Timestamp', 'Skills'])
                st.dataframe(df)
                st.markdown(table_download(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)
            else:
                st.error("Wrong Credentials")
run()