import numpy as np
from fdot import fdot 
#from numpy import dot as fdot
from time import time
class dnn():

	def __init__(self, X_train, Y_train, step_size = 0.1, reg = 0.001, h_size = [10], niter = 10000):

		self.X = X_train 
		#self.Y = Y_train

		self.step_size = step_size
		self.reg = reg
		self.h = h_size
		self.h_deep = len(h_size)+1
		self.niter = niter

		self.ndata = np.shape(X_train)[0]
		self.ndim = np.shape(X_train)[1]
		self.nclass = len(np.unique(Y_train))
			
		self.Y = np.zeros((self.ndata,self.nclass))
		self.Y[range(self.ndata),Y_train] = 1

		self.ham_ini = 0.02
		self.ham = {}
		self.const = {}
			
		for i in range(self.h_deep):

			if i == 0:
				size_a = self.ndim
				size_b = self.h[i]

			elif i == self.h_deep-1:
				size_a = self.h[i-1]
				size_b = self.nclass

			else:
				size_a = self.h[i-1]
				size_b = self.h[i]

			self.ham[i] = np.array(self.ham_ini * np.random.randn(size_a, size_b))
			self.const[i] = np.array(np.zeros(size_b))

	
	def model(self,timeflag=True):

		ham = self.ham
		const = self.const
		h_deep =self.h_deep

		fstate = {}
		fstate[0] = self.X

		bstate = {}
		#bstate[h_deep] = self.Y / self.ndata 

		loss = 3
		ti = time()	
		for i in range(self.niter):

			for j in range(h_deep):
				fstate[j+1] = np.maximum(0, fdot(fstate[j], ham[j]) + const[j])

			scores = fstate[h_deep]
			exp_scores = np.exp(scores)
			probs = exp_scores / np.sum(exp_scores, axis = 1, keepdims = True)
			corect_logprobs = -np.log(np.sum(probs*self.Y,axis=1))

			data_loss = np.sum(corect_logprobs)/self.ndata
			reg_loss = 0
			for l in range(h_deep-1):
				reg_loss += .5 * self.reg * np.sum(ham[l]*ham[l])
				reg_loss += .5 * self.reg * np.sum(const[l]*const[l])
			loss_new = data_loss + reg_loss

			if (i%100 == 0 or i == self.niter-1):
				print 'iteration: %d, loss: %f' %(i, loss_new)
			if (timeflag and i%100==0):
					print 'time used: ', time()-ti

			loss = loss_new
			bstate[h_deep] = (probs - self.Y)/self.ndata

			for k in range(h_deep,0,-1):

				bstate[k-1] = fdot(bstate[k], ham[k-1].T)
				bstate[k-1][fstate[k-1] <=0] = 0

				dham = fdot(fstate[k-1].T, bstate[k])
				dconst = np.sum(bstate[k], axis = 0)
							
				dham += self.reg* ham[k-1]
				dconst += self.reg* const[k-1]

				ham[k-1] -=  (self.step_size * dham)
				const[k-1] -=  (self.step_size * dconst)


			self.ham = ham
			self.const = const

		return loss

	def predict(self, X_test):

		ham = self.ham
		const = self.const
		h_deep = self.h_deep

		fstate = {}
		fstate[0] = X_test

		for j in range(h_deep):
			fstate[j+1] = np.maximum(0, fdot(fstate[j], ham[j]) + const[j])
		scores = fstate[h_deep]
		exp_scores = np.exp(scores)
		probs = exp_scores / np.sum(exp_scores, axis = 1, keepdims = True)
		Y_pred = probs.argmax(axis = 1)

		return Y_pred


	def accuracy(self, Y_testset, Y_pred):

		accu_array = [1 if Y_testset[i:i+1]==Y_pred[i:i+1] else 0 for i in range(len(Y_testset)) ]
		accu = sum(accu_array)/np.double(len(Y_testset))
		return accu * 100 , '%'

