import requests 
from bs4 import BeautifulSoup

''' 
functions we need 
	1. get ingredients 
		a. flags for non vegetarian, vegetarian, healthy, unhealthy
		b. transforming functions (from one flag to another)
				non-vegetarian <--> vegetarian 
				unhealthy <--> healthy
				* change one style of cuisine
				[some optionals]
	2. get directions
	3. output functoin --> human readable format 
'''

## Possibly might change get_ingredients and get_directions to take in the flag and do substitutions inside the function

def get_cuisine_type(soup_blob):
	# name = soup_blob.find_all('script')
	# print(name)
	pass
	
def get_ingredients(soup_blob):
	## based on patterns, ingredients will be in the following format:
		## < li class = "ingredients-item" ...> 
	## so we can just extract items that match the following class. 
	ingredients = []
	pattern_match = soup_blob.find_all("li", "ingredients-item")
	for ingredient in pattern_match:
		ingredients.append(ingredient.text.strip())
	print(ingredients)
	return ingredients

def get_methods_and_tools(soup_blob):
	pass

def get_directions(soup_blob):
	pass

def transform(data_struct):
	pass

def main():
	print("--------------------------------------------------")
	print("This recipe transformer only accepts recipes from AllRecipes.com")
	## Get URL 
	url = input("Please enter the URL for the recipe you want to transform: ")
	get_req = requests.get(url)
	soup = BeautifulSoup(get_req.content,'html.parser')
	## Check URL
	if soup: 
		flag = input("If you'd like to transform this recipe please describe your transformation in the following format: from --> to, otherwise type N/A: ")
		
		## get inredients
		get_ingredients(soup)

		get_cuisine_type(soup)
		if flag != "N/A":
			##get cuisine type
			cuisine_type = get_cuisine_type(soup)
			
		



	else:
		raise ValueError("URL not correct. Please try again.")




if __name__ == '__main__':
	main()