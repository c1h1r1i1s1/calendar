echo Uninstalling...
loc=$(pwd)
cd /etc/init.d/
sudo ./cald stop
sudo rc-update del cald
sudo rm cald
sudo rm -r $loc
echo "Uninstall complete!"
