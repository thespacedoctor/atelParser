# atelParser

<!-- INFO BADGES -->  

[![](https://img.shields.io/pypi/pyversions/atelParser)](https://pypi.org/project/atelParser/)  
[![](https://img.shields.io/pypi/v/atelParser)](https://pypi.org/project/atelParser/)  
[![](https://img.shields.io/github/license/thespacedoctor/atelParser)](https://github.com/thespacedoctor/atelParser)  
[![](https://img.shields.io/pypi/dm/atelParser)](https://pypi.org/project/atelParser/)  

<!-- STATUS BADGES -->  

[![](http://157.245.42.153:8080/buildStatus/icon?job=atelParser%2Fmaster&subject=build%20master)](http://157.245.42.153:8080/blue/organizations/jenkins/atelParser/activity?branch=master)  
[![](http://157.245.42.153:8080/buildStatus/icon?job=atelParser%2Fdevelop&subject=build%20dev)](http://157.245.42.153:8080/blue/organizations/jenkins/atelParser/activity?branch=develop)  
[![](https://cdn.jsdelivr.net/gh/thespacedoctor/atelParser@master/coverage.svg)](https://raw.githack.com/thespacedoctor/atelParser/master/htmlcov/index.html)  
[![](https://readthedocs.org/projects/atelparser/badge/?version=master)](https://atelparser.readthedocs.io/en/master/)  
[![](https://img.shields.io/github/issues/thespacedoctor/atelParser/type:%20bug?label=bug%20issues)](https://github.com/thespacedoctor/atelParser/issues?q=is%3Aissue+is%3Aopen+label%3A%22type%3A+bug%22+)  

*scrape and parse content of ATels posted on The Astronomer's Telegram website, identify individual objects by name and coordinates*.

Documentation for atelParser is hosted by [Read the Docs](https://atelparser.readthedocs.io/en/master/) (last
[stable version](https://atelparser.readthedocs.io/en/development/) and [latest version](https://atelparser.readthedocs.io/en/master/)). The code lives on [github](https://github.com/thespacedoctor/atelParser). Please report any issues you find [here](https://github.com/thespacedoctor/atelParser/issues).

## Features

* Report the latest ATel count
* Download all ATel as raw HTML pages. After a first download, can be run on a regular basis to download only new/missing ATels.
* Parse ATels to extract coordinates and transient source names to indexed MySQL database tables which can then be used in your own projects.



