# Building Python 0.9.8 in Ubuntu 16.04 in 2017

There are a number of notes, but this is a start-up set of notes:

- Install 32 bit compiler & libraries:
  - `sudo apt install gcc-multilib`
  - On Ubuntu 17.04 you may also need to:
    `sudo apt install gcc-6-multilib`

- You should be able to successfully run Configure.py with python2.7.**14

![](https://github.com/yarko/python-0.9.8/blob/main/PTF-Source.jpeg)
![](https://github.com/yarko/python-0.9.8/blob/main/PTF-Source-listing.jpeg)

Thanks to Dave Beazley for bringing up this topic back in 2017, which made me immediately pull out my old subscription items of Prime Time Freeware, and this 0.9.8 version of Python.  Thanks to Christopher Neugebauer for raising this topic again, which spurred me to make this public repository (thread):
https://social.coop/@chrisjrn/113164664973079269

See the `git log` for the initial commit of the Prime Time Freeware archive of this, and the steps I took in 2017 to compile and run this in a "modern" context.

Have lot's of fun, try backporting features - it's a readble, nice codebase.
