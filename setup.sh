sudo apt-get install python-numpy python-scipy python-matplotlib libsndfile1-dev lame libjpeg8-dev postgresql-server-dev-all libxml2-dev libxslt1-dev
sudo apt-get install build-essential libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev python-dev libsamplerate0-dev libtag1-dev python-numpy-dev
virtualenv env
. env/bin/activate
pip install --upgrade setuptools
pip install --upgrade pip
pip install python-dateutil
ln -s /usr/lib/python2.7/dist-packages/numpy env/lib/python2.7/site-packages
ln -s /usr/share/pyshared/numpy-1.6.1.egg-info env/lib/python2.7/site-packages
ln -s /usr/lib/python2.7/dist-packages/scipy* env/lib/python2.7/site-packages
ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so* env/lib
ln -s /usr/lib/x86_64-linux-gnu/libz.so* env/lib
ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so* env/lib
ln -s /usr/lib/pymodules/python2.7/matplotlib* env/lib/python2.7/site-packages/
ln -s /usr/lib/pymodules/python2.7/pylab* env/lib/python2.7/site-packages/
pip install -r requirements

pushd ..
git clone git@github.com:CompMusic/essentia.git
pushd essentia
git checkout -t origin/deploy
./waf configure --mode=release --with-python --prefix=/srv/dunya/env
./waf -j4
./waf install
