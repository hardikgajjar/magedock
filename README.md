# Magedock

Magedock is a small python based tool to assist with handling of Magento 2.x projects. Some of the
 main functionality include:
* Setup a new Magento2 project
* Run the project within docker containers
* Provide handy commands to do all common tasks of developer 


# Installation

This tool supports OSX and Linux distributions. No Windows support is planned.

### Dependencies
##### OSX
Install docker, docker-compose and node using Homebrew 

    $ brew install docker docker-compose
    $ brew install node
    

Install "dinghy" tool: https://github.com/codekitchen/dinghy#install

##### Linux
Install docker and docker-compose, following is the reference for Ubuntu 16.04
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

### Installation

Simply run:

    $ pip install magedock

# Usage

To use it:

    $ magedock --help
    
To get usage of individual command:

    $ magedock <command> --help
