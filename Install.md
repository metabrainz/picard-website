# Installation Steps

* Begin by cloning the repository

`git clone https://github.com/musicbrainz/picard-website/`

* cd into the directory

`cd picard-website`

* Create a python virtualenv 

*Tested on Python 2.6.5 and 2.7*

`virtualenv env/`

* Now install all the dependencies

`env/bin/pip install -r requirements.txt`

* Clone the plugins repository

*Make sure the folder name is 'plugins'*

`git clone https://github.com/musicbrainz/picard-plugins/`

* Change to admin directory and run the generate script

`cd admin`

`generate.py`

*This will generate the json data and zip files*

Don't forget to come back up...

`cd ..`

* Generate CSS from our less file

` lessc static/less/styles.less static/css/styles.css`

*This requires the less to css compiler, so you might need to download that first.*

* Create a file named 'picard.fcgi' 

`vi picard.fcgi`

...and copy the following contents

```python
#!/home/dufferzafar/picard-website/env/bin/python

import sys
sys.path.insert(0, '/home/dufferzafar/picard-website')

from flup.server.fcgi import WSGIServer
from werkzeug.debug import DebuggedApplication
from app import app
from views import *
from errors import *

app = DebuggedApplication(app, evalex=True)

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/home/dufferzafar/picard-website/fcgi.sock', umask=0).run()
```

*Make sure you replace 'dufferzafar' with your username*

`:wq!`

* Run, Forrest, Run!

`env/bin/python picard.fcgi`

* Bye!

`exit`
