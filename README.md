# MEDIA SUITE (CLARIAH)

## Installation

### Dependencies

The CLARIAH media suite is roughly made up of these two main parts:

* Server: Flask (Python) webserver
* Client: The [component library](https://github.com/beeldengeluid/labo-components)

To function properly the media suite requires access to running instances of each of the following APIs:

* The [search API](https://github.com/beeldengeluid/labs-search-api) (private repo)
* The [annotation API](https://github.com/beeldengeluid/labs-annotation-api) (private repo)

**Note**: In order to get access to one of these, please contact the owner of this repository.

### The webserver

This project runs on Python 2.7 and uses [Flask](http://flask.pocoo.org/) to serve the web content

The best practice is to create a virtualenv and then install the requirements. To make this easy we recommend `[pipenv](https://github.com/pypa/pipenv)`. `cd` into the master directory and try this:

```bash
pipenv install -r requirements.txt --two
```

This way all the necessary Python packages (including Flask) will be installed.

Now the only thing to do is to create a settings.py by copying the settings-example.py file:

```
cp settings-example.py settings.py
```

After that you can activate the virtualenv using:

```bash
pipenv shell
```

Following this it should already be possible to start the Flask webserver using

```
python server.py
```

If you're seeing debug messages you can open up the mediasuite in your favourite browser by going to `[http://localhost:5304/](http://localhost:5304/)`. The styling will not be available, for that you need to install the Javascript packages. Read on!

**Note**: check the comments in settings-example.py on how to completely configure the media suite.

### Client application

Now that the webserver is setup, it is necessary to obtain all of the required Javascript packages. The main package is the [labo-components](https://github.com/beeldengeluid/labo-components) library maintained by Beeld en Geluid, which contains all of the web components that are used for building the different apps (a.k.a. recipes) within the media suite.

Make sure [npm](https://www.npmjs.com/) is installed, then go into /src/static (containing package.json) and run:

```bash
npm install
```

<!-- Really? 
**Note**: You might need to be sudo for this.
-->

After installation the styles will automatically be compiled.

#### Styling the media suite

[SASS](http://sass-lang.com/) is used to generate the main stylesheet (/src/static/css/main.css).

Whenever you want to change the overall styling you need to run the watcher using a `npm` command

```bash
npm run watch
```

While the watcher is running any changes to the `*.scss` files in the `/static/sass` folder will be compiled into `/src/static/css/main.css`

## Creating a new recipe

The best way to learn how the media suite works is by creating a new recipe, which will give you the opportunity to start assembling your own choice of components from the [component library](http://github.com/beeldengeluid/labo-components). 

Before starting, it's good to realise there are several ways of using the component library, but there is a recommended one for integration in the media suite, which we'll discuss right away.

### Adding a recipe to the recipes page (recommended)

By following the recommended approach, your custom recipe will appear in the recipes page of the media suite.

#### Step 1: Create a recipe JSON file

The recipes.html file is the template that renders certain (manually chosen) recipes from the [resources/recipes](https://github.com/CLARIAH/wp5_mediasuite/tree/master/src/resources/recipes) folder in blocks on the page to choose from.

To make your recipe appear on this page, first you need to add a new JSON file (with a meaningful name reflecting the functionality of the recipe) in **/resources/recipes**:

```
{
	"id" : "my_recipe",
	"name" : "Your own recipe!",
	"type" : "my_recipe",
	"phase" : "recipe-building",
	"description" : "Your recipe that does very cool things. Aim for world peace!",
	"ingredients" : {
		"key1" : "value1",
		"key2" : "value2"
	}
}
```
**Note** There is also an example.json you can copy and modify for convenience

The ```name``` is used as the title of your recipe on the recipes page

The ```description``` is used as the description for your recipe on the recipes page

The ```type``` parameter is used to load the correct recipe ```*.jsx``` file from the labo-component's [index.jsx](https://github.com/beeldengeluid/labo-components/blob/master/app/index.jsx) file, which is the main interface for using the component library, but more on that later on.

The ```phase``` is used to place your recipe in the right category on the recipes page. Please use one of the already existing values to reflect the intended research phase your recipe is suitable for. If it's something new, please make up a meaningful label.

The ```ingredients``` are basically any key/value pairs you'd like to use to easily configure your recipe.

Since hot loading does not work yet, you have to restart the server to make you recipe JSON load into server memory. 

After that you can finally make your recipe appear in the recipes.html by insert a block of HTML like this:

```
<!-- EXAMPLE  -->
<div id="{{recipes['my_recipe'].id}}" class="col-sm-6 col-md-4">
	<div class="panel panel-default">
		<div class="panel-heading">
			<h3 class="panel-title"><i class="fa fa-rocket"></i>&nbsp; {{recipes['my_recipe'].name}}</h3>
		</div>
		<div class="panel-body">
			{{recipes['my_recipe'].description}}
		</div>
		<div class="panel-footer text-right"><a href="{{recipes['my_recipe'].url}}">View recipe</a></div>
	</div>
</div>
```

#### Step 2: Create the *.jsx file in the component library

Currently the [component library](http://github.com/beeldengeluid/labo-components) also contains the application specific recipes as top-level React components. In a later version, the media suite recipes will probably be moved into this repo.

Since you've only created a JSON file and want to create a whole new recipe type, you now have to create a new ```*.jsx``` file for your recipe and map your recipe in the index.jsx of the labo-components.

Open the labo-components code in your editor and add a new ```*.jsx``` file to the [/app](https://github.com/beeldengeluid/labo-components/tree/master/app) directory. The easiest is to copy ExampleRecipe.jsx and rename it (and its class name!) to whatever you like. Otherwise your recipe code should contain the following as the bare minimum:

```
import IDUtil from './util/IDUtil';

class MyRecipe extends React.Component {

	constructor(props) {
		super(props);
		this.state = {}
	}
	
	render() {
			return (
				<div className={IDUtil.cssClassName('example-recipe')}>

				</div>
			)
		}
	}

}

export default MyRecipe;
```

Following this, make sure to map the recipe type to your React class in [index.jsx](https://github.com/beeldengeluid/labo-components/blob/master/app/index.jsx) by extending the cookRecipe function as follows:

```
else if(recipe.type === 'myRecipe.type') {
	render(
		<MyRecipe recipe={recipe} params={params} user={user}/>,
		document.getElementById(elementId)
	);
}
```
Now to compile your changes please run the following command in the main directory of the labo-components code:

```
npm run dev
```

This will watch for any changes you make in the code (within the ```/app``` directory) and will try to build the code. If it fails it will print in what part of the code the error originates.

After you've managed a succesfull build, you need to do one more thing to make your new recipe work: edit the recipe.html (template that imports the labo-components library and is responsible for rendering recipes in the media suite) as follows:

```
<!--<script type="text/javascript" src="/static/node_modules/labo-components/dist/labo-components.js"></script>-->
<script src="/PATH_TO_YOUR_DEVELOPMENT_VERSION_OF_LABO_COMPONENTS/dist/labo-components.js" type="text/javascript"></script>
```

This makes sure the media suite code does not look for the component library in the node_modules, but looks for the development version you've just built. 

Now (possibily after clearing your browser cache) you can now click on your recipe in the recipes.html and go to a working dummy recipe!

### Manual integration

TODO write this


## Who do I talk to? ###

* Jaap Blom
