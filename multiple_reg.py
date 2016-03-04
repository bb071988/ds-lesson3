import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import os.path as osp # makes it so we can substitute forward slash for backslash minimizing character escape headaches
import sys
import statsmodels.formula.api as smf

def fix_rate(data):
    rate = data.rstrip('%')
    rate = float(rate) / 100 
    return rate

def getfile(mypath, filename, url): # filename should be passed in with forward slashes
	
	# See if we have the file locally.  If so use it.  If not go get it. Otherwise stop
	try: 
		df = pd.read_csv(osp.normpath(mypath + filename)) #  index_col=0 - This index statement causes an error when we try to read saved file for some reason?
		return df
	except IOError:
		try:
			df = pd.read_csv(url, index_col=0)
			df.to_csv(osp.normpath(mypath + filename), header=True, index=False)
			return df		
		except:
			print("Sorry - Can't find the input file on disk or online or couldn't write it once found")
			sys.exit(1) # stop processing


def clean_data(raw_data):
	raw_data.dropna(inplace=True) # drop the na rows
	raw_data['New.Rate'] = [fix_rate(data) for index, data in raw_data['Interest.Rate'].iteritems()]
	raw_data['dtir'] = [fix_rate(data) for index, data in raw_data['Debt.To.Income.Ratio'].iteritems()]
	raw_data['FICO'] = map(lambda x: int(x.split('-')[0]), raw_data['FICO.Range']) # clean fico range and get score #ask Kyle why this runs so slow

	print("Shape after clean is {}".format(raw_data.shape))
	return raw_data

def enhance_data(df):
	df['annual_inc'] = df['Monthly.Income'] * 12
	df['Rate'] = df['New.Rate'] # seems silly to have to do this but smf chokes on Interest.Rate - No field named Interest?
	print("Shape after enhance is {}".format(df.shape))
	print("printing head after enhance ******************************")
	print(df.head())
	return df

# def minimize_data(df):  # Thought I would try limiting this to just the fields required in the model - did not help
# 	df = df[['annual_inc','Rate']]
# 	# df1 = df[['a','b']]
# 	return df

	
def linreg_A(df):  #modifying this to refelct the multiple regression exercise
	#Use income (annual_inc) to model interest rates (int_rate).
	intrate = df['Rate']
	annualinc = df['annual_inc']

	# intrate is dependent variable
	y = np.matrix(intrate).transpose()

	# A single independent variable
	x = np.matrix(annualinc).transpose()  ######## error?

	X = sm.add_constant(x)

	linmodel_A = sm.OLS(y,X).fit()
	return linmodel_A

def linreg_B(df):

	# Build the model in statsmodels api
	# copy data and separate predictors and response
	X = df.copy()
	y = X.pop('Rate')  

	linmodel_B = smf.ols(formula='Rate ~ annual_inc', data=df).fit()
	return linmodel_B

def linreg_C(df):
	# Build the model in statsmodels api
	# copy data and separate predictors and response
	X = df.copy()
	y = X.pop('Rate')  

	linmodel_C = smf.ols(formula='annual_inc ~ Rate', data=df).fit() # flipped the variables to see if results made more sense.
	return linmodel_C

def linreg_D(df):
# trying to overfit 

	intrate = df['Interest.Rate']
	loanamt = df['Amount.Requested']
	fico = df['FICO']
	dtir = df['dtir']
	ocl = df['Open.CREDIT.Lines']
	rcb = df['Revolving.CREDIT.Balance']
	i6m = df['Inquiries.in.the.Last.6.Months']
	ai = df['annual_inc']
	# Build the model in statsmodels api
	# copy data and separate predictors and response
	X = df.copy()
	y = X.pop('Rate')  

	linmodel_D = smf.ols(formula='Rate ~ FICO + loanamt + ocl + rcb + i6m + ai', data=df).fit() # flipped the variables to see if results made more sense.
	return linmodel_D	
	

def analyze_it():
	mypath = 'C:/Users/bob071988/thinkful/projects/ds-lesson3/'
	filename = 'loansData.csv'
	url = 'https://spark-public.s3.amazonaws.com/dataanalysis/loansData.csv'
	
	df = getfile(mypath, filename, url)
	df = clean_data(df)
	df = enhance_data(df)
	# df = minimize_data(df)

	linmodel_A = linreg_A(df)
	linmodel_B = linreg_B(df)
	linmodel_C = linreg_C(df)
	linmodel_D = linreg_D(df)

	print(linmodel_A.summary())
	print(linmodel_B.summary())
	print(linmodel_C.summary())
	print(linmodel_D.summary())

	return(df, linmodel_A, linmodel_B, linmodel_C)

	
def main():
    analyze_it()

if __name__ == "__main__":
    main()


### stats model predict vs numpy predict
