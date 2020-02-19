## 2020-02-17 \| Hacking Python


In an effort to run a simple python script in the CGA classroom, I opted to create an example python script that showcases a basic class structure that can be easily manipulated.
The hope was to use this as a launching point towards writing a python-based toolbox for the first part of this class.

Of course, Python 3 does not run from the command line on the classroom's machines, even though a version of Python 3 is installed.

A first ditch effort was to add to the user's environment variables the path to the Python 3 executable, which completely and utterly failed.
*Caveat, a student adeptly pointed out that by changing the executable's name from Python.exe to Python3.exe, you can totally call it from the command line.*
Rather, I went through the arduous process of hacking into ArcGIS Pro's python environment, which is a three-step process:

1. Clone the original Python 3 environment used by ArcGIS Pro
2. Append the path to the ArcGIS/Pro/bin/Python/Scripts folder to the user environments
3. Activate the cloned python environment from the command line

This seems completely ridiculous at first glance; however, in my opinion, programming works best when the testing environment is separate from the working environment.

### Jekyll Updates
Well, I have finally decided to read through some of the Jekyll documentation and in doing so, I have created my blog.
This required creating a \_posts directory that contains very specifically named markdown files and creating a blog.md (with a proper YAML header) that uses Liquid tags to read each markdown file in my \_posts directory and prints them in reverse chronological order.

Finally.

The other success story was removing the `overflow=hidden` property from my navigation menu; now I can see all my buttons in a tiny window!
I also added a responsive element to the CSS to make the navigation bar twice the height when the screen size is small.

I feel that I have reached some small level of nirvana.
It has only taken several weeks and many lost hours of development to get here.
