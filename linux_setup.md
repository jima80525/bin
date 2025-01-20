# Setup a new Linux Machine


## fix sudoers file

```
sudo visudo  (had to use "pkexec vi /etc/sudoers" last time)
jima  ALL = NOPASSWD: ALL
```

note that the above line MUST BE THE LAST LINE IN THE FILE
(from: http://maestric.com/doc/unix/ubuntu_sudo_without_password)

## set up cinnamon

https://computingforgeeks.com/how-to-install-cinnamon-desktop-on-ubuntu/


## Run setup_machine.sh

After running:

* change .gitconfig user and email if needed.
* install ssh key on github

## setup starship (get install steps in here, too!)

1. install nerdfont - picked "EnvyCodeR Nerd Font" https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/EnvyCodeR.zip
1.1 - download the font
1.2 - mkdir ~/.local/share/fonts
1.3 - cp Downloads/EnvyCodeR.zip ~/.local/share/fonts
1.4 - cd ~/.local/share/fonts
1.5 - unzip EnvyCodeR.zip
1.6 - rm EnvyCodeR.zip
1.7 - fc-cache -fv
1.8 - set terminal to  use that font :)
2. Install starship
2.1 - curl -sS https://starship.rs/install.sh | sh
2.2 - mkdir -p ~/.config
2.3 - cp ~/bin/startship.toml ~/.config

## Configure Terminal

* right click in text area and show menu bar!
* edit current profile to change size 80x50 and font size to 14

## Configure vim

```
git clone git@github.com:jima80525/vimconfig.git
mv vimconfig .vim
cp .vim/vimrc_move_to_home_dir .vimrc
```

## Apps to install manually

1. VsCode
   - search for this - might change - using microsoft versions directly
2. remember the milk
   - download .deb from rtm site
   - note: fedora == intel, ubuntu == AMD
3. Draw.io
   - sudo apt update
   - sudo apt -y install wget curl
   - curl -s https://api.github.com/repos/jgraph/drawio-desktop/releases/latest | grep browser_download_url | grep '\.deb' | cut -d '"' -f 4 | wget -i -
   - sudo dpkg -i ./draw*
4. slack
   - ~~download .rpt from site~~
   - ~~sudo apt install alien~~
   - ~~sudo alien <package>~~
   - ~~sudo dpkg -i <new deb pkg>~~
   - ~~find all channels~~
   - ~~Download .deb package (link is a bit hidden) and open - it will install from there~~
   - just installed from snap
      - msi - vsa video and external
      - jec
      - rp members
      - rp team
      - pycolorado
      - noco tech?
5. Spotify
   - https://www.spotify.com/us/download/linux/
   - Set up keyboard to pause/play spotify
   - custom keymap (settings->keyboard)
      - `dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause`
6. typora
   - download .deb from site and apt install .deb
7. docker



## Old Stuff

* set up for audiobook-cde
* sudo apt-get install abcde
* sudo apt-get install lame
* sudo pip install eyeD3
