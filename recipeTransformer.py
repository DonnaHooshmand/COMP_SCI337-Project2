import re
import requests 
from bs4 import BeautifulSoup
import json
import copy
import math

class Ingredient:
	base_ingredient = "None"
	unit = "None"
	quantity = 0

	def __init__(self, b, u, q):
		self.base_ingredient = b
		self.unit = u
		self.quantity = q

	def pprint(self):
		print("Base ingredient: ", self.base_ingredient)
		print("Unit: ", self.unit)
		print("Quantity: ", self.quantity)
		print("")


## recipe object
class Recipe:
	def __init__(self, title = "Recipe", ingredients = "None", instructions = "None", nutrition = "None", \
					prepTime = "None", cookTime = "None", totalTime = "None", recipeYield = "None", recipeCategory = "None", \
					recipeCuisine = "None", recipeTools = "None", recipeMethods = "None"):
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
		self.recipeTools = recipeTools
		self.recipeMethods = recipeMethods

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
			ingredient.pprint()
		print("="*30)
		print("Instructions:")
		for i, step in enumerate(self.instructions):
			print("\t"+str(i)+" . "+step)
		print("="*30)
		print("Methods:")
		for i in self.recipeMethods:
			print(i)
		print("="*30)
		print("Tools:")
		for i in self.recipeTools:
			print(i)
		print("="*30)


def recipeFromJson(jsonObj, soup):
	# print("PRINTING TOTAL RECIPE CHUNK")
	# print(jsonObj)
	print("DIVIDING INTO SECTIONS")
	title = jsonObj['name']

	# safe init in case certain recipes' webpages omit information chunks
	prepTime, cookTime, totalTime, recipeYield, recipeCategory = "None", "None", "None", "None", "None"
	recipeCuisine, recipeTools, recipeMethods = "None", "None", "None"

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
			ingredients = get_ingredients(soup)
			# for ix, step in enumerate(info):
			# 	ingredients.append(step)
		elif k == 'recipeInstructions': # list
			for ix, step in enumerate(info):
				instructions.append(step['text'])
		elif k == 'nutrition':
			for tag, value in info.items():
				if tag and value and tag != "@type":
					nutrition[tag] = value

	return Recipe(title=title, ingredients=ingredients, instructions=instructions, prepTime=prepTime, cookTime=cookTime,
				  totalTime=totalTime, recipeYield=recipeYield, recipeCategory=recipeCategory,
				  recipeCuisine=recipeCuisine, nutrition=nutrition)


## Possibly might change get_ingredients and get_directions to take in the flag and do substitutions inside the function

def get_cuisine_type(soup_blob):
	# name = soup_blob.find_all('script')
	# print(name)
	pass

def try_convert_to_float(str):
	try:
		return float(str)
	except:
		return 0

def get_ingredients(soup_blob):
	## based on patterns, ingredients will be in the following format:
		## < li class = "ingredients-item" ...>
	## so we can just extract items that match the following class.
	# also extracts the base ingredient, unit, and quantity. E.g. "1/2 cups of olive oil" is parsed to olive oil, cup, and 0.5
	ingredients = []
	pattern_match = soup_blob.find_all("li", "ingredients-item")
	for ingredient in pattern_match:

		ingred_obj = Ingredient(ingredient.input["data-ingredient"], \
											ingredient.input["data-unit"], try_convert_to_float(ingredient.input["data-init-quantity"]))
		ingredients.append(ingred_obj)
	return ingredients

def get_methods_and_tools(recipeObj):
	## There are a few ways to do this.
		## 1. We could use words such as "heat" as indicators of what might be a tool.
			## ex: heat frying pan
			## but that seems like it might not be great...
		## 2. (WHAT WE'RE DOING) Use a list and see what is in the directions.
	## Credit: https://www.cooksmarts.com/cooking-guides/create-a-functional-kitchen/20-must-have-kitchen-tools/
	tool_list = ['pan', 'wok', 'saucepan', 'pot', 'dish', 'whisk', 'bowl', 'plate', 'skillet', 'sauce pan', 'oven', 'air fryer']
	tools_found = []
	for i, instruction in enumerate(recipeObj.instructions):
		for tool in tool_list:
			if tool in instruction.lower():
				if tool not in tools_found:
					tools_found.append(tool)
	recipeObj.recipeTools = tools_found
	## Credit: https://www.unlockfood.ca/en/Articles/Cooking-Food-Preparation/Food-Dictionary--Cooking-Foods-with-Dry-Heat-Methods.aspx
	method_list = ['grill', 'broil', 'bake', 'roast', 'saute', 'sear', 'braise', 'boil', 'steam', 'poach', 'simmer', 'stew', 'cook']
	methods_found = []
	for i, instruction in enumerate(recipeObj.instructions):
		for method in method_list:
			if method in instruction.lower():
				if method not in methods_found:
					methods_found.append(method)
	recipeObj.recipeMethods = methods_found
	print(" tools: ", tools_found )
	print(" methods: ", methods_found )



def get_directions(soup_blob):
	## based on patterns, directions will be in the following format:
		## <li class="subcontainer instructions-section-item" ... >
	## so we can just extract items that match the following class.
	directions = []
	pattern_match = soup_blob.find_all("li", "subcontainer instructions-section-item")
	for step in pattern_match:
		directions.append(step.text.strip())
	return directions

def halve(recipeObj):
	print("HALVING THIS RECIPE")
	newRecipe = copy.deepcopy(recipeObj)
	for i, ingredient in enumerate(newRecipe.ingredients):
		newRecipe.ingredients[i].quantity = ingredient.quantity / 2

	#IF METHOD IS BAKE, SCALE COOKING TIME?

	return newRecipe


def double(recipeObj):
	print("HALVING THIS RECIPE")
	newRecipe = copy.deepcopy(recipeObj)
	for i, ingredient in enumerate(newRecipe.ingredients):
		newRecipe.ingredients[i].quantity = ingredient.quantity * 2

	#IF METHOD IS BAKE, SCALE COOKING TIME?

	return newRecipe


def ingredient_subs(substitutions, newRecipe):
	subsMade={}

	for i, ingredient in enumerate(newRecipe.ingredients):
		for sub in substitutions.keys():
			if sub in ingredient.base_ingredient:
				subsMade[sub] = substitutions[sub]
				newRecipe.ingredients[i].base_ingredient = ingredient.base_ingredient.replace(sub, substitutions[sub])

	# transform instructions
	for i, instruction in enumerate(newRecipe.instructions):
		for sub in substitutions.keys():
			if sub in instruction:
				newRecipe.instructions[i] = instruction.replace(sub, substitutions[sub])

	return subsMade



def ingredTrans(recipeObj, json_file, trans_type):
	f = open(json_file)
	substitutions = json.load(f)
	f.close()
	print(f"PRINTING {trans_type.upper()} SUBSTITUTIONS PULLED FROM JSON FILE:")
	print(substitutions)
	newRecipe = copy.deepcopy(recipeObj)

	subsMade = ingredient_subs(substitutions, newRecipe)

	for sub in subsMade.keys():
		print(f"As a part of a transformation to {trans_type.lower()} cuisine, {sub} was substituted with {substitutions[sub]}.")

	return newRecipe


def toVeg(recipeObj):
	return ingredTrans(recipeObj, "veggieSubs.json", "vegetarian")

def toNonVeg(recipeObj):
	return ingredTrans(recipeObj, "meatSubs.json", "carnivorous")

def toHealthy(recipeObj):
	return ingredTrans(recipeObj, "to_healthy.json", "healthy")


def toUnhealthy(recipeObj):
	return ingredTrans(recipeObj, "to_unhealthy.json", "unhealthy")

def toAirFryer(recipeObj):
	print("transforming this recipe to work with an air fyer instead of an oven.")
	newRecipe = copy.deepcopy(recipeObj)

	backupInstructions = []
	heatF = 0
	#find where instructions mention the oven
	for ix, instruction in enumerate(newRecipe.instructions):
		# print(newRecipe.instructions[ix])
		# print(instruction)
		instruction = instruction.replace("oven", "air fryer")
		instruction = instruction.replace("Oven", "Air fryer")
		# print(newRecipe.instructions[ix])
		# print(instruction)
		if "preheat" in instruction.lower():
			heat = int(re.findall(r'\d\d\d degrees F', instruction)[0][:3])
			# print(heat)
			heat = heat - 25
			# print(re.sub(r'\d\d\d degrees F', str(heat) + ' degrees F', instruction))
			instruction = re.sub(r'\d\d\d degrees F', str(heat) + ' degrees F', instruction)
			heat = math.floor((heat - 32) * 5 / 9)
			# print("C HEAT ", heat)
			# print(re.sub(r'\d\d\d degrees C', str(heat) + ' degrees C', instruction))
			instruction = re.sub(r'\d\d\d degrees C', str(heat) + ' degrees C', instruction)
		y = re.findall(r'(\d+ to \d+ minutes)|(\d+ minutes)|(\d+ hours)', instruction)
		if y:
			# print(y)
			matches = []
			for i in y:
				for j in i:
					if j:
						matches.append(j)
			# print('matches, ',matches)

			times = [re.findall(r'\d+', time) for time in matches]
			# print(times)
			timesList = []
			for time in times:
				for t in time:
					timesList.append(t)
			# print(timesList)
			timeSubs = {}
			for t in timesList:
				timeSubs[t] = str(int(int(t)*4/5))
			# print(timeSubs)

			for sub in timeSubs.keys():
				print("replacing", sub, "with" ,timeSubs[sub])
				instruction = instruction.replace(" "+sub+" ", " "+timeSubs[sub]+" ")
			# print("scaled cooking time")
		newRecipe.instructions[ix] = instruction
		backupInstructions.append(instruction)
	# for inst in newRecipe.instructions:
	# 	print(inst)

	print("Printing cooking time for total recipe")
	# print(newRecipe.cookTime)
	hours = int(newRecipe.cookTime[4:newRecipe.cookTime.find("H")])
	mins = int(newRecipe.cookTime[newRecipe.cookTime.find("H")+1:newRecipe.cookTime.find("M")])
	totalMins = mins+hours*60
	scaledMins = totalMins*4/5
	difference = totalMins - scaledMins
	newRecipe.cookTime = "P0DT"+str(math.floor(scaledMins/60))+"H"+str(scaledMins%60)
	differenceH = math.floor(difference/60)
	differenceM = difference%60
	print(f"Using an air fryer has shaved {str(differenceH)} hours and {str(differenceM)} minutes off of cook time.")
	print("New cook time for recipe:  ", newRecipe.cookTime)
	#replace instances of oven with air fryer
	#scale cooking time, cooking temperature
	return newRecipe

def recipeToCajun(recipe):
	with open('cuisineIngredientTargets.json', encoding='utf-8') as f:
		ingredient_targets = json.load(f)
	with open('cajunIngredients.json', encoding='utf-8') as f:
		cajun_ingredients = json.load(f)
	old_ingredients = {}
	no_match_ingredients = []

	for ingredient_index, ingredient in enumerate(recipe.ingredients):
		ingredient_match = False
		full_string, ingredient_string, class_string = None, None, None
		ingredient_name = ingredient.base_ingredient
		for ingredient_class, class_list in ingredient_targets.items():
			for class_ingredient in class_list:
				if ingredient_name in class_ingredient:
					ingredient_match = True
					full_string, ingredient_string = ingredient_name, ingredient_name
				elif class_ingredient in ingredient_name:
					ingredient_match = True
					full_string, ingredient_string = ingredient_name, class_ingredient

				if ingredient_match:
					class_string = ingredient_class
					if ingredient_class not in old_ingredients:
						old_ingredients[ingredient_class] = []
					old_ingredients[ingredient_class].append(
						{'full_string': full_string, 'ingredient_string': ingredient_string}
					)
					break

			if ingredient_match:
				break
		if not ingredient_match:
			no_match_ingredients.append(ingredient_name)
		else:
			if ingredient_string in cajun_ingredients[class_string]:
				continue
			else:
				if len(cajun_ingredients[class_string]):
					if len(cajun_ingredients[class_string]) > 1:
						new_ingredient = cajun_ingredients[class_string][0]
						cajun_ingredients[class_string] = cajun_ingredients[class_string][1:]
					else:
						new_ingredient = cajun_ingredients[class_string][0]
						cajun_ingredients[class_string] = []

					recipe.ingredients[ingredient_index].base_ingredient = full_string.replace(ingredient_string, new_ingredient)
					if class_string == 'spices':
						old_unit = recipe.ingredients[ingredient_index].unit.strip()
						if old_unit != '':
							for instruction_index, instruction_string in enumerate(recipe.instructions):
								if ' ' + old_unit in instruction_string:
									recipe.instructions[instruction_index] = instruction_string.replace(
										' ' + old_unit, '')
						recipe.ingredients[ingredient_index].unit = 'teaspoon'
						recipe.ingredients[ingredient_index].quantity = '1.0'

					for instruction_index, instruction_string in enumerate(recipe.instructions):
						ingredient_string = ingredient_string.strip()
						if ' ' + ingredient_string in instruction_string:
							recipe.instructions[instruction_index] = instruction_string.replace(' ' + ingredient_string, ' ' + new_ingredient + ' ')
						else:
							old_ingredient_root = ingredient_string.split()[-1]
							ingredient_chunks = ingredient_string.split()
							successful_chunk = ''
							for chunk in reversed(ingredient_chunks):
								if chunk == 'pepper':
									break
								if ' ' + chunk + successful_chunk in instruction_string:
									successful_chunk = ' ' + chunk + successful_chunk
								else:
									break
							if successful_chunk != '':
								recipe.instructions[instruction_index] = instruction_string.replace(successful_chunk, ' ' + new_ingredient)
							else:
								for chunk in reversed(ingredient_chunks[:-1]):
									if ' ' + chunk + successful_chunk in instruction_string:
										successful_chunk = ' ' + chunk + successful_chunk
									else:
										break
								if successful_chunk != '':
									recipe.instructions[instruction_index] = instruction_string.replace(
										successful_chunk, ' ' + new_ingredient)

	return recipe

def transform(recipeObj, transformation):
	if transformation == "->veg":
		return toVeg(recipeObj)
	elif transformation == "->nonVeg":
		return toNonVeg(recipeObj)
	elif transformation == "->healthy":
		return toHealthy(recipeObj)
	elif transformation == "->unhealthy":
		return toUnhealthy(recipeObj)
	elif transformation == "->halve":
		return halve(recipeObj)
	elif transformation == "->double":
		return double(recipeObj)
	elif transformation == "->airFryer":
		return toAirFryer(recipeObj)
	elif transformation == "->cajun":
		return recipeToCajun(recipeObj)

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
		print(" 1. Transforming lasagna to vegetarian lasagna:")
		url = "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')

		## Check URL
		if soup:

			jsonRecipe = get_recipe_json(soup)
			lasagna = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(lasagna)
			print("Created recipe object successfully. Printing now:")
			print(type(lasagna))
			lasagna.pprint()


			vegetarianLasagna = transform(lasagna, "->veg")
			get_methods_and_tools(vegetarianLasagna)
			print("Recipe transformed, printing revised copy:")
			vegetarianLasagna.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		input("Ready for next experiment?")
		print(" 2. Transforming vegetarian pad thai to meat pad thai:")
		url = "https://www.allrecipes.com/recipe/244716/shirataki-meatless-meat-pad-thai/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')

		## Check URL
		if soup:

			jsonRecipe = get_recipe_json(soup)
			padThai = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(padThai)
			print("Created recipe object successfully. Printing now:")
			padThai.pprint()

			meatPadThai = transform(padThai, "->nonVeg")
			get_methods_and_tools(meatPadThai)
			print("Recipe transformed, printing revised copy:")
			meatPadThai.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		input("Ready for next experiment?")
		print(" 3. Transforming Beef Bourguignon to healthy:")
		url = "https://www.allrecipes.com/recipe/16167/beef-bourguignon-i/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')

		## Check URL
		if soup:

			jsonRecipe = get_recipe_json(soup)
			beef = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(beef)
			print("Created recipe object successfully. Printing now:")
			beef.pprint()

			healthyBeef = transform(beef, "->healthy")
			get_methods_and_tools(healthyBeef)
			print("Recipe transformed, printing revised copy:")
			healthyBeef.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		input("Ready for next experiment?")
		print(" 4. Transforming Salmon to Unhealthy:")
		url = "https://www.allrecipes.com/recipe/228285/teriyaki-salmon/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')

		## Check URL
		if soup:

			jsonRecipe = get_recipe_json(soup)
			salmon = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(salmon)
			print("Created recipe object successfully. Printing now:")
			salmon.pprint()

			unhealthySalmon = transform(salmon, "->nonVeg")
			get_methods_and_tools(unhealthySalmon)
			print("Recipe transformed, printing revised copy:")
			unhealthySalmon.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		input("Ready for next experiment?")
		print(" 5--extra 1--Transforming Mexican rice to Cajun Creole rice:")
		url = "https://www.allrecipes.com/recipe/73303/mexican-rice-iii/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content, 'html.parser')

		## Check URL
		if soup:
			jsonRecipe = get_recipe_json(soup)
			mexicanRice = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(mexicanRice)
			print("Created recipe object successfully. Printing now:")
			mexicanRice.pprint()

			cajunRice = recipeToCajun(mexicanRice)
			print("Recipe transformed to Cajun, printing revised copy:")
			get_methods_and_tools(cajunRice)
			cajunRice.pprint()

		input("Ready for next experiment?")
		print(" 6--extra 2--Transforming Oven tiramisu to air fryer tiramisu:")
		url = "https://www.allrecipes.com/recipe/7757/tiramisu-cheesecake/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content, 'html.parser')

		## Check URL
		if soup:

			jsonRecipe = get_recipe_json(soup)
			tiramisu = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(tiramisu)
			print("Created recipe object successfully. Printing now:")
			tiramisu.pprint()

			transformedTiramisu = transform(tiramisu, "->airFryer")
			get_methods_and_tools(transformedTiramisu)
			print("Recipe transformed, printing revised copy:")
			transformedTiramisu.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		input("Ready for next experiment?")
		print(" 7--extra 3--Doubling Mexican Rice:")
		url = "https://www.allrecipes.com/recipe/73303/mexican-rice-iii/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content, 'html.parser')

		## Check URL
		if soup:

			jsonRecipe = get_recipe_json(soup)
			rice = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(rice)
			print("Created recipe object successfully. Printing now:")
			rice.pprint()

			bigRice = transform(rice, "->double")
			get_methods_and_tools(bigRice)
			print("Recipe transformed, printing revised copy:")
			bigRice.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")

		input("Ready for next experiment?")
		print(" 7--extra 3--Halving Mexican Rice:")
		url = "https://www.allrecipes.com/recipe/229293/korean-saewoo-bokkeumbap-shrimp-fried-rice/"
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content, 'html.parser')

		## Check URL
		if soup:

			jsonRecipe = get_recipe_json(soup)
			kRice = recipeFromJson(jsonRecipe, soup)
			get_methods_and_tools(kRice)
			print("Created recipe object successfully. Printing now:")
			kRice.pprint()

			smallRice = transform(kRice, "->halve")
			get_methods_and_tools(smallRice)
			print("Recipe transformed, printing revised copy:")
			smallRice.pprint()

		else:
			raise ValueError("URL not correct. Please try again.")


		print("demo has concluded")



	else: # USER INPUT BASED
		get_req = requests.get(url)
		soup = BeautifulSoup(get_req.content,'html.parser')
		#print(soup.prettify())

		## Check URL
		if soup:
			flag = input("If you'd like to transform this recipe please describe your transformation from the following options: '->veg', '->nonVeg', '->healthy', '->unhealthy', '->halve', '->double'; otherwise type N/A: ")

			## get inredients
			ingredient_list = get_ingredients(soup)
			print("gathered ingredients:")
			[x.pprint() for x in ingredient_list]

			## get directions
			direction_list = get_directions(soup)
			print("gathered directions")
			print(direction_list)

			get_cuisine_type(soup)
			if flag != "N/A":
				##get cuisine type
				cuisine_type = get_cuisine_type(soup)

			jsonRecipe = get_recipe_json(soup)
			recipe_obj = recipeFromJson(jsonRecipe, soup)
			print("Created recipe object successfully. Printing now:")
			recipe_obj.pprint()

			transformed_recipe_obj = transform(recipe_obj, flag)
			print("Recipe transformed, printing revised copy:")
			transformed_recipe_obj.pprint()



		else:
			raise ValueError("URL not correct. Please try again.")




if __name__ == '__main__':
	main()