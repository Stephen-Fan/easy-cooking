# Module 1 Group Assignment

CSCI 5117, Fall 2024, [assignment description](https://canvas.umn.edu/courses/460699/pages/project-1)

## App Info:

* Team Name: 20245117
* App Name: Easy Cooking
* App Link: <https://project-1-20245117.onrender.com/>

### Students

* Qinghong Fan, fan00123@umn.edu
* Linghe Wang, wang9257@umn.edu
* Zhiyuan Lin, lin00905@umn.edu
* Abdullahi Nor, nor00003@umn.edu


## Key Features

**Describe the most challenging features you implemented
(one sentence per bullet, maximum 4 bullets):**

* Retrieving all recipe data from the database and displaying them based on the filter selected or similar keywords
* The logged-in users can create, edit, and delete their own recipes
* Checklist enables users to save the recipes they are interested in and print the ingredients in a PDF file
* Evaluating the nutrition information of each recipe through nutritional API and printing the info in a table on each recipe page

## Testing Notes

**Is there anything special we need to know in order to effectively test your app? (optional):**

* N/A


## Screenshots of Site

**[Add a screenshot of each key page (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository)
along with a very brief caption:**

On this Recipe page, users can explore all recipes, and filter recipes based on the style from the sidebar or the filters selected in the filters block. Users can click on any recipe to view the recipe details as well as the nutrition info.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/easy_cooking/static/images/recipesPage.png "Recipes page")


Users can type keywords on this Search page to search for recipes. All the recipes related to the keywords will be shown at the bottom. Users can also use the filter to obtain the recipes they want. 
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/easy_cooking/static/images/searchPage.png "Search page")


On the portal page, users can create their own recipes. When the users click on an existing recipe, they should be able to edit the info and then update, or delete this recipe. Users can only edit/delete their own recipes, but not the ones created by others.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/easy_cooking/static/images/portalPage.png "Portal page")


When the users browse the recipe details, they can add this recipe (or multiple recipes) to the checklist if they want. In the checklist, the users can check/uncheck the ingredients if they are interested in them (e.g. want to buy them later). A PDF version of the checklist can also be printed out via the button.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/easy_cooking/static/images/cartPage.png "Cart page")

## Mock-up 

There are a few tools for mock-ups. Paper prototypes (low-tech, but effective and cheap), Digital picture edition software (gimp / photoshop / etc.), or dedicated tools like moqups.com (I'm calling out moqups here in particular since it seems to strike the best balance between "easy-to-use" and "wants your money" -- the free teir isn't perfect, but it should be sufficient for our needs with a little "creative layout" to get around the page-limit)

In this space please either provide images (around 4) showing your prototypes, OR, a link to an online hosted mock-up tool like moqups.com

**[Add images/photos that show your paper prototype (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository) along with a very brief caption:**

This is the home page of the website.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/HomePage.jpg?raw=true "home page")

This is the recipe page that shows all recipes based on user choice.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/GeneralRecipe.jpg?raw=true "recipe page")

The next two pages are for the specific recipe including all information about this recipe.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/SpecificRecipe1_1.jpg?raw=true "recipe_1")
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/SpecificRecipe1_2.jpg?raw=true "recipe_2")

This is the sign-up page where the user can create an account.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/SignUp.jpg?raw=true "sign up")

This is the login page.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/LoginPage.jpg?raw=true "login page")

This is the user portal page. After the user has logged in, the user can review, create, edit, and delete the recipes owned by the user.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/UserPortal.jpg?raw=true "user portal")

This is the page where the user edits the specific recipe.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/EditNewRecipe.jpg?raw=true "edit recipe")

This is the search page.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/Search.jpg?raw=true "search page")

This shows all relevant recipes based on keywords typed in the search bar.
![Alt text](https://github.com/csci5117f24/project-1-20245117/blob/main/low-fidelity-prototype/DoSearch.jpg?raw=true "do search page")

![](https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif)


## External Dependencies

**Document integrations with 3rd Party code or services here.
Please do not document required libraries. or libraries that are mentioned in the product requirements**

* The Edamam Nutrition Analysis API [link](https://developer.edamam.com/edamam-nutrition-api-demo)

**If there's anything else you would like to disclose about how your project
relied on external code, expertise, or anything else, please disclose that
here:**

...
