
# coding: utf-8

# In[1]:


#I import the libraries I may need

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn as skl
import json
import gzip


# #### Loading and preparing the dataset

# In[2]:


f = gzip.open("C:/Users/Marta/Desktop/AppDataScience_data.gz", "rb")
print(type(f))


# In[3]:


#Opening the file, it is a string 
with gzip.open("C:/Users/Marta/Desktop/AppDataScience_data.gz", "rb") as f:
    data = json.loads(json.dumps(f.read().decode("ascii")))
type(data)


# In[4]:


#Lets have a look. It is a string, we want to end up with a list of dictionaries
print(data[0:600])
print('\n')
print(data[-600:-1])


# In[5]:


#We split into a list
datalist = data.split('\n')


# In[6]:


#Lets check the beggining and the end; we do not like the end.
print(datalist[0],'\n',datalist[-1])


# In[7]:


#Removing the last one, and checking it looks ok now
datalist = datalist[:-1]
print(datalist[0],'\n',datalist[-1])


# In[8]:


#We change the data to a list of dictionaries
import ast 
dictlist = [ast.literal_eval(i) for i in datalist]


# In[9]:


#Checking all is at it should...
print(dictlist[0],'\n',dictlist[-1])


# In[10]:


#going to dataframe and having a first look
dataframe = pd.DataFrame(dictlist)
print(dataframe.head(5),'\n\n', dataframe.tail(5),'\n')
print(type(dataframe),'\n',dataframe.shape,'\n',dataframe.dtypes)


# In[11]:


#Lets check if there are missing values, null, na or nan. There are not! 
dataframe.isnull().sum().sum()


# In[12]:


#We have 1664 distinct client ids 
len(dataframe.client_id.unique())


# In[13]:


#And those are the distinct event types
print(dataframe.event_type.unique(),'\n',len(dataframe.event_type.unique()))


# ## First question: 
# A toplist of different event_types where we count number of unique
# client_ids per event_type

# In[14]:


clients_per_event = dataframe.groupby('event_type')['client_id'].nunique()
type(clients_per_event)


# In[15]:


#Here are the distinct event types sorted per number of distinct client id 
clients_per_event.sort_values(ascending= False)


# In[16]:


# A top 10 list in proportion 
sortedlist = clients_per_event.sort_values(ascending= False)/len(dataframe.client_id.unique())
sortedlist.head(10)


# ## Second question:
# For how long does the median user use the app?

# In[17]:


#what I made up for puting 0 as the first event we have from a particular user, as example
anuser = dataframe[dataframe['client_id']=='f64a315b07']['timestamp']
anuser_normsort = ((anuser-anuser.min())/3600000.0).sort_values()
anuser_normsort.hist(bins=60 ,xlabelsize=10)
plt.show()


# In[18]:


#I want to put it in an array, and take the difference in time between actions
anuser_array = anuser_normsort.values
diff = anuser_array[1:]-anuser_array[:-1]


# In[19]:


#Now, for an user, I can obtain the mean time in the app, considering that no action during 30 min implies no use
#Without kwoing more details about the app, I can not judge if 30 minutes is reasonable; maybe 10 o even 5 minutes of 
#no activity is already a new login, and the results can change a lot... alterate the command "sep" with the number 
#of minutes you consider reasonable for a "new use of the app"
j = 1
smallsum = 0
bigsum = 0
sep = 30 
for i in diff:
    if i < (sep/60):
        smallsum=smallsum+i
    else:
        bigsum=bigsum+smallsum
        j=j+1
        smallsum=0
usermean=(bigsum+smallsum)/j
print(usermean*60)#This is in minutes

#To see the differences in time
pd.Series(diff).hist(bins=244 ,xlabelsize=10)
plt.show()


# The previous was a particular case for me to understand the data and identify potential problems. Now, we generalize:

# In[20]:


dataframe['client_id'].unique()


# In[21]:


#for any particular user
#As a rule of thumb and with some robutness criterias, I have end up considering inactivity of more than 5 minutes
#as new ussage
usermeanlist = []
for i in dataframe['client_id'].unique():
    anuser = dataframe[dataframe['client_id']== i ]['timestamp']
    anuser_normsort = ((anuser-anuser.min())/3600000.0).sort_values()
    anuser_array = anuser_normsort.values
    diff = anuser_array[1:]-anuser_array[:-1]
    j = 1
    smallsum = 0
    bigsum = 0
    sep = 5 #This parameter is the numer of minutes of innactivity we allow until consider "new ussage"
    for k in diff:
        if k < (sep/60):
            smallsum=smallsum+k
        else:
            bigsum=bigsum+smallsum
            j=j+1
            smallsum=0
    usermean=(bigsum+smallsum)/j
    usermeanlist.append(usermean*60) #to have it in minutes


# In[22]:


#I calculate the mean and standard deviation, to have an idea of the scale and robustness
a = np.array(usermeanlist).mean()
b = np.array(usermeanlist).std()
print(a,b)


# In[23]:


#To see the differences in time. It is exponential, that was expected.
pd.Series(usermeanlist).hist(bins=80 ,xlabelsize=10)
plt.show()


# In[24]:


#This is the median time an user uses the app, in minutes
print('Median time an user uses the app: ',np.median(usermeanlist), ' minutes')

