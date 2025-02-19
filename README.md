## openplotter-iob

OpenPlotter app app to manage your boat remotely

### Installing

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production**.

#### For production

Install IoB from openplotter-settings app.

#### For development

Install openplotter-iob dependencies:

`sudo apt install openplotter-settings openplotter-signalk-installer`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-iob`

Make your changes and create the package:

```
cd openplotter-iob
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-iob_x.x.x-xxx_all.deb
```

Run post-installation script:

`sudo iobPostInstall`

Run:

`openplotter-iob`

Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://cloudsmith.io/~openplotter/repos/openplotter/packages/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1