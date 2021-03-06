from .kv_types import *
from .helpers import *
class KVFile:

	#***************** INITIALIZERS *******************************************#

	def __init__(self, fileIn:str=""):
		""" Initializer that opens a file if provided"""

		self.varsFlat = []
		self.vars1D = []
		self.vars2D = []

		self.header = ""
		self.fileVersion = -1;
		self.error_messages = [];

	#*********************** ADD VARIABLES ***********************************#

	def add(self, newVar, varName:str, desc:str=""):
		""" Add a variable to the object  """

		newItem = KvItem(newVar, varName, desc)

		#Check for errors
		if newItem.type == ERR:
			msg = newItem.val
			self.logErr(f"Failed to add variable '{varName}' ({msg})")
			return False

		if self.checkContains(varName):
			self.logErr(f"Failed to add variable '{varName}' (Variable with given name already exists)")
			return False

		if newItem.dimension == FLAT:
			self.varsFlat.append(newItem)
		elif newItem.dimension == M1D:
			self.vars1D.append(newItem)
		elif newItem.dimension == M2D:
			self.vars2D.append(newItem)
		else:
			msg = f"Variable dimension exceeded 2"
			self.logErr(f"Failed to add variable '{varName}' ({msg})")
			return False

		return True

	#TODO: Add way to edit variables

	#************************ ACCESS VARIABLES ********************************#

	def __call__(self, varName:str):
		""" Access a variable in the class """

		if not self.checkContains(varName):
			self.logErr(f"Variable '{varName}' not present.")
			return None

		for x in self.varsFlat:
			if x.name == varName:
				return x
		for x in self.vars1D:
			if x.name == varName:
				return x
		for x in self.vars2D:
			if x.name == varName:
				return x

		self.logErr(f"Variable 'varName' missed! There's a bug in pykv!")



	#********************** VARIABLE MANAGEMENT ******************************#

	def checkContains(self, varName:str):
		""" Accepts a list of variable names and checks if they're present
		in the list of variables """

		if any(x.name == varName for x in self.varsFlat):
			return True
		if any(x.name == varName for x in self.vars1D):
			return True
		if any(x.name == varName for x in self.vars2D):
			return True

		return False

	def clear(self):
		""" Purges all variables from the object """
		self.varsFlat = []
		self.vars1D = []
		self.vars2D = []

	def numVar(self):
		""" Gets the number of variables currently saved in the object """
		return len(self.varsFlat)+len(self.vars1D)+len(self.vars2D)

	#*************************** ERROR RECORD ********************************#

	def logErr(self, msg:str):
		""" Add error message """
		self.error_messages.append(msg)

	def err(self):
		""" Get last error message"""
		if len(self.error_messages) > 0:
			return self.error_messages[-1]
		else:
			return "No errors"

	#*************************** HEADER ***************************************#

	def setHeader(self, h:str):
		self.header = h

	def getHeader(self):
		return self.header

	def getVersion(self):
		return self.fileVersion

	#************************** FILE I/O **************************************#

	def readKV1_V2(self, fileIn:str, options:str=""):

		with open(fileIn) as file:

			lnum = 0

			while True:
				lnum += 1

				line = file.readline()
				if not line:
					break

				#Remove newline characters
				if line[-1] == '\n':
					line = line[0:-1]

				#Parse words
				words = parseIdx(line, " \t")

				#Skip blank lines
				if len(words) < 1:
					continue

				if words[0].str == "#VERSION": #Version Statement

					#Ensure 2 words present
					if len(words) != 2:
						self.logErr(f"Failed on line {lnum}. Version state requires exactly 2 words")
						return False

					#Read version statement
					try:
						self.fileVersion = float(words[1].str)
					except:
						x = words[1].str
						self.logErr(f"Failed on line {lnum}. Failed to convert version '{x}' to float.")
						return False

				elif words[0].str == "#HEADER":

					self.header = ""; #Clear header
					openedOnLine = lnum

					foundHeader = False

					#Keep reading lines until closing header found
					while True:
						lnum += 1

						line = file.readline()
						if not line:
							break

						#Remove newline characters
						if line[-1] == '\n':
							line = line[0:-1]

						#Parse words
						words = parseIdx(line, " \t")

						if len(words) < 1:
							self.header = self.header + "\n"
							continue

						if words[0].str == "#HEADER":
							foundHeader = True
							break
						else:
							if len(self.header) == 0:
								self.header = line
							else:
								self.header = self.header + "\n" + line

					if not foundHeader:
						self.logErr(f"Failed on line {openedOnLine}, failed to find closing #HEADER statement.")
						return False
				elif words[0].str == '//':
					continue
