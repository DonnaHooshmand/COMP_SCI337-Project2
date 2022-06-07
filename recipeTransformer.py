import re
import requests 
from bs4 import BeautifulSoup
import json
import copy

class Ingredient:
	base_ingredient = "None"
	unit = "None"
	quantity = 0

	def __init__(self, b, u, q):
		self.base_ingredient = b
		self.unit = u
		self.quantity = q
	
	def pprint(self):
		print("\n\n~ Printing ingredient ~")
		print("="*30)
		print("Base ingredient: ", self.base_ingredient)
		print("="*30)
		print("Unit: ", self.unit)
		print("="*30)
		print("Quantity: ", self.quantity)
		print("\n\n")

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
## recipe object
class recipe():
	def __init__(self, title = "Recipe", ingredients = "None", instructions = "None", nutrition = "None", \
					prepTime = "None", cookTime = "None", totalTime = "None", recipeYield = "None", recipeCategory = "None", \
					recipeCuisine = "None"):
		self.title = title
		self.ingredients = ingredients # list
		self.instructions = instructions # list
		self.nutrition = nutrition # dict
		self.prepTime = prepTime
		self.cookTime = cookTime
		self.totalTime = totalTime
		self.recipeYield = recipeYield
		self.recipeCategory = recipeCategory # 0 or 1 element list
		self.recipeCuisine = recipeCuisine # 0 or 1 element list

	def pprint(self):
		print("~ Printing recipe ~")
		print("="*30)
		print("Title:", self.title)
		print("="*30)
		print("Categories: ")
		print(self.recipeCategory)
		print(self.recipeCuisine)
		print("="*30)
		print("Nutrition:")
		for x, y in self.nutrition.items():
			print("\t- " + x + ": " + y)
		print("="*30)
		print("Prep Time: " + str(self.prepTime))
		print("Cook Time: " + str(self.cookTime))
		print("Total Time: " + str(self.totalTime))
		print("Recipe Yield: " + str(self.recipeYield))
		print("="*30)
		print("Ingredients:")
		for ingredient in self.ingredients:
			print("\t-" + ingredient)
		print("="*30)
		print("Instructions:")
		for i, step in enumerate(self.instructions):
			print("\t"+str(i)+" . "+step)
		print("="*30)

def recipeFromJson(jsonObj):
	# print("PRINTING TOTAL RECIPE CHUNK")
	# print(jsonObj)
	print("DIVIDING INTO SECTIONS")
	title = jsonObj['name']
	ingredients = []
	instructions = []
	nutrition = {}
	for k, info in jsonObj.items():
		if k == 'prepTime':
			prepTime = info
		elif k == 'cookTime':
			cookTime = info
		elif k == 'totalTime':
			totalTime = info
		elif k == 'recipeYield':
			recipeYield = info
		elif k == 'recipeCategory':
			recipeCategory = info
		elif k == 'recipeCuisine':
			recipeCuisine = info
		elif k == 'recipeIngredient': # list
			for ix, step in enumerate(info):
				ingredients.append(step)
		elif k == 'recipeInstructions': # list
			for ix, step in enumerate(info):
				instructions.append(step['text'])
		elif k == 'nutrition':
			for tag, value in info.items():
				if tag and value and tag != "@type":
					nutrition[tag] = value

	return recipe(title = title, ingredients = ingredients, instructions=instructions, prepTime=prepTime, cookTime=cookTime,\
				totalTime=totalTime, recipeYield=recipeYield, recipeCategory=recipeCategory, recipeCuisine=recipeCuisine, nutrition=nutrition)


## Possibly might change get_ingredients and get_directions to take in the flag and do substitutions inside the function

def get_cuisine_type(soup_blob):
	# name = soup_blob.find_all('script')
	# print(name)
	pass

def try_convert_to_float(str):
	try:
		return float(str)
	except:
		return 1
	
def get_ingredients(soup_blob):
	## based on patterns, ingredients will be in the following format:
		## < li class = "ingredients-item" ...> 
	## so we can just extract items that match the following class. 
	ingredients = []
	pattern_match = soup_blob.find_all("li", "ingredients-item")
	for ingredient in pattern_match:

		# print("base ingredient: ", ingredient.input["data-ingredient"])
		# print("unit: ", ingredient.input["data-unit"])
		# print("quantity: ", ingredient.input["data-init-quantity"])

		ingred_obj = Ingredient(ingredient.input["data-ingredient"], \
											ingredient.input["data-unit"], try_convert_to_float(ingredient.input["data-init-quantity"]))
		ingredients.append(ingred_obj)
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

def toVeg(recipeObj):
	f = open("veggieSubs.json")
	substitutions = json.load(f)
	f.close()
	print("PRINTING VEGGIE SUBSTITUTIONS PULLED FROM JSON FILE:")
	print(substitutions)
	newRecipe = copy.deepcopy(recipeObj)
	# transform ingredients
	for i, ingredient in enumerate(newRecipe.ingredients):
		for sub in substitutions.keys():
			if sub in ingredient:
				newRecipe.ingredients[i] = ingredient.replace(sub, substitutions[sub])

	# transform instructions
	for i, instruction in enumerate(newRecipe.instructions):
		for sub in substitutions.keys():
			if sub in instruction:
				newRecipe.instructions[i] = instruction.replace(sub, substitutions[sub])
		
	return newRecipe

def toNonVeg(recipeObj):
	f = open("veggieSubs.json")
	substitutions = json.load(f)
	f.close()
	print("PRINTING VEGGIE SUBSTITUTIONS PULLED FROM JSON FILE:")
	print(substitutions)
	print("REVERSING SUBSTITUTIONS")
	substitutions = {v: k for k, v in substitutions.items()}
	print(substitutions)
	newRecipe = copy.deepcopy(recipeObj)
	# transform ingredients
	for i, ingredient in enumerate(newRecipe.ingredients):
		for sub in substitutions.keys():
			if sub in ingredient:
				newRecipe.ingredients[i] = ingredient.replace(sub, substitutions[sub])

	# transform instructions
	for i, instruction in enumerate(newRecipe.instructions):
		for sub in substitutions.keys():
			if sub in instruction:
				newRecipe.instructions[i] = instruction.replace(sub, substitutions[sub])
		
	return newRecipe

def toHealthy(recipeObj):
	pass

def toUnhealthy(recipeObj):
	pass

def transform(recipeObj, transformation):
	if transformation == "->veg":
		return toVeg(recipeObj)
	elif transformation == "->nonVeg":
		return toNonVeg(recipeObj)
	elif transformation == "->healthy":
		return toHealthy(recipeObj)
	elif transformation == "->unhealthy":
		return toUnhealthy(recipeObj)

def get_recipe_json(soup_blob):
	recipe_chunk = json.loads(soup_blob.find("script", type="application/ld+json").text)[1]
	# print('='*30, '\nAn overview :)\n', '='*30)
	# for k, info in recipe_chunk.items():
	# 	if k in ['prepTime', 'cookTime', 'totalTime', 'recipeYield', 'recipeCategory', 'recipeCuisine']:
	# 		print(k + ':', info)
	# print('=' * 30, '\nIngredients :)\n', '=' * 30)
	# for k, info in recipe_chunk.items():
	# 	if k in ['recipeIngredient']:
	# 		for ix, step in enumerate(info):
	# 			print('\t-', step)
	# print('=' * 30, '\nInstructions :)\n', '=' * 30)
	# for k, info in recipe_chunk.items():
	# 	if k in ['recipeInstructions']:
	# 		for ix, step in enumerate(info):
	# 			print('\t' + str(ix + 1) + '. ', step['text'])
	# print('=' * 30, '\nNutrition :)\n', '=' * 30)
	# for k, info in recipe_chunk.items():
	# 	if k in ['nutrition']:
	# 		for tag, value in info.items():
	# 			print('\t', tag + ':', value)
	# chris is the greatest coder ever and commenting out his code is not a comment on its quality

	return recipe_chunk


def main():
	print("--------------------------------------------------")
	print("This recipe transformer only accepts recipes from AllRecipes.com")
	## Get URL 
	url = input("Please enter the URL for the recipe you want to transform, or 'demo' for a demo: ")
	if url == 'demo':
		print("Transforming lasagna to vegetarian lasagna:")
		url = "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')

		## Check URL
		if soup:
			
			jsonRecipe = get_recipe_json(soup)
			lasagna = recipeFromJson(jsonRecipe)
			print("Created recipe object successfully. Printing now:")
			print(type(lasagna))
			lasagna.pprint()

			vegetarianLasagna = transform(lasagna, "->veg")
			print("Recipe transformed, printing revised copy:")
			vegetarianLasagna.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		print("Transforming vegetarian pad thai to meat pad thai:")
		url = "https://www.allrecipes.com/recipe/244716/shirataki-meatless-meat-pad-thai/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')

		## Check URL
		if soup:
			
			jsonRecipe = get_recipe_json(soup)
			padThai = recipeFromJson(jsonRecipe)
			print("Created recipe object successfully. Printing now:")
			padThai.pprint()

			meatPadThai = transform(padThai, "->nonVeg")
			print("Recipe transformed, printing revised copy:")
			meatPadThai.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		print("demo has concluded")

	else: # USER INPUT BASED
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')
		#print(soup.prettify())

		## Check URL
		if soup: 
			flag = input("If you'd like to transform this recipe please describe your transformation in the following format: from --> to, otherwise type N/A: ")

			## get inredients
			ingredient_list = get_ingredients(soup)
			print("gathered ingredients:")
			print("new ingredient list. does it print?")
			[x.pprint() for x in ingredient_list]
			# print(ingredient_list)

			## get directions
			direction_list = get_directions(soup)
			print("gathered directions")
			print(direction_list)

			get_cuisine_type(soup)
			if flag != "N/A":
				##get cuisine type
				cuisine_type = get_cuisine_type(soup)
				
			jsonRecipe = get_recipe_json(soup)
			lasagna = recipeFromJson(jsonRecipe)
			print("Created recipe object successfully. Printing now:")
			lasagna.pprint()

			vegetarianLasagna = transform(lasagna, "->veg")
			print("Recipe transformed, printing revised copy:")
			vegetarianLasagna.pprint()



		else:
			raise ValueError("URL not correct. Please try again.")




if __name__ == '__main__':
	main()