# NNPACK YOLOv3
From: http://funofdiy.blogspot.com
# Step 0: prepare Python and Pi Camera

 Log in to Raspberry Pi using SSH or directly in terminal.

 Make sure `pip-install` is included (it should come together with Debian

```
sudo apt-get install python-pip
```

 Install OpenCV. The simplest way on RPI is as follows (do not build from source!):

```
sudo apt-get install python-opencv
```

 Enable pi camera

```
sudo raspi-config
```

 Go to `Interfacing Options`, and enable `P1/Camera`

 You will have to reboot the pi to be able to use the camera

 A few additional words here. In the advanced option of raspi-config, you  can adjust the memory split between CPU and GPU. Although we would like  to allocate more ram to CPU so that the pi can load a larger model, you  will want to allocate at least 64MB to GPU as the camera module would  require it.

# Step 1: Install NNPACK

 NNPACK was used to optimize [Darknet](https://github.com/pjreddie/darknet) without using a GPU. It is useful for embedded devices using ARM CPUs.

 Idein's [qmkl](https://github.com/Idein/qmkl) is  also used to accelerate the SGEMM using the GPU. This is slower than  NNPACK on NEON-capable devices and primarily useful for ARM CPUs without  NEON.

 The NNPACK implementation in Darknet was improved to use transform-based  convolution computation, allowing for 40%+ faster inference performance  on non-initial frames. This is most useful for repeated inferences, ie.  video, or if Darknet is left open to continue processing input instead  of allowed to terminate after processing input.

## Install Ninja (building tool)

 Install [PeachPy](https://github.com/Maratyszcza/PeachPy) and [confu](https://github.com/Maratyszcza/confu)

```
sudo pip install --upgrade git+https://github.com/Maratyszcza/PeachPy
sudo pip install --upgrade git+https://github.com/Maratyszcza/confu
```

 Install [Ninja](https://ninja-build.org/)

```
git clone https://github.com/ninja-build/ninja.git
cd ninja
git checkout release
./configure.py --bootstrap
export NINJA_PATH=$PWD
cd
```

## Install NNPACK

 Install modified [NNPACK](https://github.com/shizukachan/NNPACK)

```
git clone https://github.com/shizukachan/NNPACK
cd NNPACK
confu setup
python ./configure.py --backend auto
```

 If you are compiling for the Pi Zero, change the last line to `python ./configure.py --backend scalar` You can skip the following several lines from the original  darknet-nnpack repos. I found them not very necessary (or maybe I missed  something)

 Build NNPACK with ninja (this might take * *quie* * a while, be patient. In fact my Pi crashed in the first time. Just reboot and run again):

```
$NINJA_PATH/ninja
```

 do a `ls` and you should be able to find the folders `lib` and `include` if all went well:

```
ls
```

 Test if NNPACK is working:

```
bin/convolution-inference-smoketest
```

 In my case, the test actually failed in the first time. But I just ran  the test again and all items are passed. So if your test failed, don't  panic, try one more time.

 Copy the libraries and header files to the system environment:

```
sudo cp -a lib/* /usr/lib/
sudo cp include/nnpack.h /usr/include/
sudo cp deps/pthreadpool/include/pthreadpool.h /usr/include/
```

# Step 2. Using the models

 We have finally finished configuring everything needed. Now simply clone this repository. Note that we are cloning the yolov3 branch. It comes with the python wrapper I wrote, correct makefile, and yolov3 weight:

```
cd ~/
https://github.com/steven-mi/yolov3-road-damage-detection.git
cd yolov3-road-damage-detection/deploy-on-pi-with-nnpack
make
```

 At this point, you can build darknet-nnpack using `make`. Be sure to edit the Makefile before compiling.

# Step 3. Test with YoloV3-tiny

To install picamera using apt simply:

```
$ sudo apt-get update
$ sudo apt-get install python-picamera python3-picamera
```

 To test it, simply run

```
sudo python rpi_video.py
```

 or

```
sudo python rpi_record.py
```

**Note** If you want to use another darknet model then you just have to put the pretrained weights into the main folder and edit the python scripts.
