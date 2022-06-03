import requests 
from bs4 import BeautifulSoup
import json

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
	return ingredients

def get_methods_and_tools(soup_blob):
	pass

def get_directions(soup_blob):
	## based on patterns, directions will be in the following format:
		## <li class="subcontainer instructions-section-item" ... >
	## so we can just extract items that match the following class. 
	directions = []
	pattern_match = soup_blob.find_all("li", "subcontainer instructions-section-item")
	for step in pattern_match:
		directions.append(step.text.strip())
	return directions

def transform(data_struct):
	pass

def get_recipe_json(soup_blob):
	recipe_chunk = json.loads(soup_blob.find("script", type="application/ld+json").text)[1]
	print('='*30, '\nAn overview :)\n', '='*30)
	for k, info in recipe_chunk.items():
		if k in ['prepTime', 'cookTime', 'totalTime', 'recipeYield', 'recipeCategory', 'recipeCuisine']:
			print(k + ':', info)
	print('=' * 30, '\nIngredients :)\n', '=' * 30)
	for k, info in recipe_chunk.items():
		if k in ['recipeIngredient']:
			for ix, step in enumerate(info):
				print('\t-', step)
	print('=' * 30, '\nInstructions :)\n', '=' * 30)
	for k, info in recipe_chunk.items():
		if k in ['recipeInstructions']:
			for ix, step in enumerate(info):
				print('\t' + str(ix + 1) + '. ', step['text'])
	print('=' * 30, '\nNutrition :)\n', '=' * 30)
	for k, info in recipe_chunk.items():
		if k in ['nutrition']:
			for tag, value in info.items():
				print('\t', tag + ':', value)

	return recipe_chunk


def main():
	print("--------------------------------------------------")
	print("This recipe transformer only accepts recipes from AllRecipes.com")
	## Get URL 
	url = input("Please enter the URL for the recipe you want to transform: ")
	get_req = requests.get(url)
	soup = BeautifulSoup(get_req.content,'html.parser')
	#print(soup.prettify())

	## Check URL
	if soup: 
		flag = input("If you'd like to transform this recipe please describe your transformation in the following format: from --> to, otherwise type N/A: ")
		
		## get inredients
		ingredient_list = get_ingredients(soup)

		## get directions
		direction_list = get_directions(soup)

		get_cuisine_type(soup)
		if flag != "N/A":
			##get cuisine type
			cuisine_type = get_cuisine_type(soup)
			
		get_recipe_json(soup)



	else:
		raise ValueError("URL not correct. Please try again.")




if __name__ == '__main__':
	main()