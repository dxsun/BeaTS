From Budmonde Duinkhar:

To run your project, you want to run:

`LD_PRELOAD=./libLeap.so python3 my_project.py`

For more resources if you have issues, follow guides at:

https://developer-archive.leapmotion.com/documentation/python/devguide/Project_Setup.html

This link eventually leads to the ubuntu solution for python3 and above here:

https://forums.leapmotion.com/t/leap-motion-sdk-with-python-3-5-in-linux-tutorial/5249

The files I've included in this patch are my compilations that follow the tutorial steps provided above on my Ubuntu 16.04 (Xenial) (x64) for python3.6

Also I should note that this only works after you've figured out how to get the LeapMotion service itself to work on the Linux machine since their official installer doesn't work immediately. The pointer that I used to get it working is this one: https://askubuntu.com/questions/1008964/problems-installing-leap-motion-orion/1009297. Hope this helps.
