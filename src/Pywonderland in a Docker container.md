__Q__: How can I work with pywonderland on my computer without installing all of the required libraries and modules into my operating system?

__A__: Docker will allow you to create a Linux container running Python 3 where we can install pywonderland and all of its dependencies.

__Process__ Steps 1-6 only need to be done once.:

TL;DR:
* `mkdir ~/data_from_docker`
* `docker build -t pywonderland .`
* `docker run -it -v ~/data_from_docker:/data_to_host --rm --name pywonderland pywonderland`
* `source four_images.sh`
* `exit`
* `ls ~/data_from_docker`  # or `open ~/data_from_docker/*` on the Mac.

1. Make sure that [Docker](https://www.docker.com/get-docker) is running on your computer.
    * _I use a Mac but other platforms should also work..._
    * Mac users with homebrew installed can __type:__ `brew install docker`
2. Open a terminal, clone this repo, and `cd` into the repo's `src` directory and then `ls`.
3. To create a local directory that will also be visible from within the Docker container, __type:__ `mkdir ~/data_from_docker`
4. To see the steps that Docker will automatically execute, __type:__ `cat Dockerfile`
	* The Docker build process will:
	    1. Start from the [stock Python 3 container](https://store.docker.com/images/python) from the Docker Store
	    2. `apt-get update` && `apt-get upgrade` to ensure that Linux is up to date
	    3. `apt-get install` the libraries
	    4. `pip install` the Python modules
5. To start the Docker build process, __type:__ `docker build -t pywonderland .`
6. Go get some coffee or walk the dog or watch if you want but the automated process of building the pywonderland Docker container can several minutes.
    * I ignore the `debconf: delaying package configuration, since apt-utils is not installed` error messages because they will not go away even if I install apt-utils beforehand.
    * The `numba` part seems to take an especially long time for a relatively small download and it generates some scary looking error messages that I have just ignored.
7. To start the pywonderland container, __type:__
    * `docker run -it -v ~/data_from_docker:/data_to_host --rm --name pywonderland pywonderland`
8. Your command prompt should change because now you should be running inside the container.
9. To run four of the pywonderland scripts, type, `source four_images.sh`
10. You should see that there are no .png files at the start of this script and four at the end.
11. To get back to Kansas, __type:__ `exit`
12. To verify that the four images have been copied from the Docker container to your computer, __type:__
    * `ls ~/data_from_docker`
    * Mac users can __type:__ `open ~/data_from_docker/*`

__Known Issues__ help wanted:
* Most other pywonderland scripts use Python's built-in tkinter user interface which can be [made to work in Docker](https://hub.docker.com/r/dorakorpar/nsgui) but I have not yet succeeded on my Mac using [XQuartz](https://www.xquartz.org).
* I have not verified pywonderland outside of the misc directory.
* I have not verified that this is the minimal container so there might be extra libraries or modules being installed.
