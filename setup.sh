sudo apt-get install python-numpy python-scipy python-matplotlib libsndfile1-dev lame libjpeg8-dev
virtualenv env
. env/bin/activate
pip install --upgrade pip
pip install python-dateutil
ln -s /usr/local/lib/python2.7/dist-packages/essentia/ env/lib/python2.7/site-packages
ln -s /usr/lib/python2.7/dist-packages/numpy env/lib/python2.7/site-packages
ln -s /usr/share/pyshared/numpy-1.6.1.egg-info env/lib/python2.7/site-packages
ln -s /usr/lib/python2.7/dist-packages/scipy* env/lib/python2.7/site-packages
ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so* env/lib
ln -s /usr/lib/x86_64-linux-gnu/libz.so* env/lib
ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so* env/lib
ln -s /usr/lib/pymodules/python2.7/matplotlib* env/lib/python2.7/site-packages/
ln -s /usr/lib/pymodules/python2.7/pylab* env/lib/python2.7/site-packages/


