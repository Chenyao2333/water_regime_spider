# Water Regime Spider

A spider crawling the water regime from [xxfb.hydroinfo.gov.cn](http://xxfb.hydroinfo.gov.cn).

# Usage

I meet some problems when trying convert the initial database to git-large-file. So please [download](https://drive.google.com/file/d/0B3c_xXFxUDQwUnVMMmRrbHlSajg/view?usp=sharing) the initial database (the data before 2016.12.30), and put it into the `misc` directory.

I suggest using docker and docker-compose to run it:

* Open the `docker-compose.yml`, replace the host volume folder (in line 10) with you needed
* Run `docker-compose up` or `docker-compose up -d` at the backgroud.

