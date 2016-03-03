import pandas as pd
import numpy as np
import statsmodels.api as sm
import os.path as osp # makes it so we can substitute forward slash for backslash minimizing character escape headaches
import sys

mypath = 'C:/Users/bob071988/thinkful/projects/U2L5/'

def getfile(filename, url): # filename should be passed in with forward slashes

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

df_adv = getfile('Advertising.csv', 'http://www-bcf.usc.edu/~gareth/ISL/Advertising.csv')

X = df_adv[['TV','Radio']]
y = df_adv['Sales']
print(df_adv.head())

X = df_adv[['TV', 'Radio']]
y = df_adv['Sales']

## fit a OLS model with intercept on TV and Radio
X = sm.add_constant(X)
est = sm.OLS(y,X).fit()

print(est.summary())

# import formula api as alias smf
import statsmodels.formula.api as smf
# import pandas as pd

# formula: response ~ predictor + predictor
# gut reaction is this is easier - no constant - no keeping x and y straight 1 line vs 6
# est = smf.ols(formula='Sales ~ TV + Radio', data=df_adv).fit()
est = smf.ols(formula='Sales ~ TV + Radio', data=df_adv).fit()
print(est.summary())


# Handling categorical variables.

df_heart = getfile('SAheart.data', 'http://statweb.stanford.edu/~tibs/ElemStatLearn/datasets/SAheart.data')

X = df_heart.copy()
y = X.pop('chd')
print(df_heart.head())

# compute percentage of chronic heart disease for famhist
print(y.groupby(X.famhist).mean())

# encode famhist as a numeric via pd.factor
df_heart['famhist_ord'] = pd.Categorical(df_heart.famhist).labels

est = smf.ols(formula="chd ~ famhist_ord", data=df_heart).fit()

print(est.summary())



# 	try: 
# 		df_adv = pd.read_csv(osp.normpath('C:/Users/bob071988/thinkful/projects/U2L5/Advertising.csv'))
# 	except IOError:
# 		try:
# 			df_adv = pd.read_csv('http://www-bcf.usc.edu/~gareth/ISL/Advertising.csv', index_col=0)
# 			df_adv.to_csv(osp.normpath('C:/Users/bob071988/thinkful/projects/U2L5/Advertising.csv'), header=True, index=False)
# 		except:
# 			print("Sorry - Can't find the input file on disk or online or couldn't write it once found")
# 			sys.exit(1) # stop processing



