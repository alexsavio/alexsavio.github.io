Title: How to use Byobu
Date: 2014-07-06 10:00:00
Category: SysAdmin
Tags: terminal, config, ssh, multi-tasking
Slug: how-to-byobu
Author: Alexandre M. Savio
Email: alexsavio@gmail.com
Summary: A short manual for Byobu and a list of its advantages.


[Byobu](http://byobu.co), in the same way as [tmux](http://tmux.sourceforge.net/), allows to
manage many terminals through just one. In summary, it is a terminal-based terminal multiplexer and session manager.

It can be very helpful when working with a server through SSH. Instead of opening a terminal
and connecting to your server every time you nedd another terminal, you can
setup your server to run Byobu or tmux at the beginning of your session and have as many terminals as you need. Byobu also keeps terminal sessions alive after detaching from them.

Byobu is an enhancement that connects to and uses Screen or tmux (you choose), but offers useful statistics and easy-to-use hotkeys for the basic commands.



## Installing Byobu

In Ubuntu:

    :::bash
    apt-get install byobu.

Else take a look at <http://byobu.co/downloads.html>



## Start Byobu

    :::bash
    byobu



## Configure Ubuntu to run Byobu from the beginning

    :::bash
    byobu-config

Feel free to change anything.

The important setting to change is: "*Byobu currently launches at login (toggle on)*". Select that and press return.

Now you can go back to the menu and exit byobu-config (tab to the exit choice and hit return).



## Resume previous sessions

    :::bash
    byobu –r session_title



## Hotkeys

Byobu has easy keybindings that use the function keys:

* **F2**: Create a new window
* **F3**: Move to previous window
* **F4**: Move to next window
* **F5**: Reload profile
* **F6**: Detach from this session
* **F7**: Enter copy/scrollback mode
* **F8**: Re-title a window
* **F9**: Configuration Menu, can also be summoned by **Ctrl+a**, **Ctrl+@**
* **F12**: Lock current session



## How detaching works or How to maintain a session

Perform a short demo. Issue the command:

    :::bash
    echo hello

Now exit the session by pressing **F6** to detach from Byobu and then run: *exit*.

Now SSH back into your machine.
You can notice that the *echo hello* command is still on the screen.

Detaching does not end your session, it gives you access to another session.
That means you can log in, run a long running task, and then detach and come back later when you;ve finished the task.



## Note for vim users:

You might find now a strange behaviour when using **Ctrl-Left** and **Ctrl-Right** keys to skip words using vim and also other programs.

The best solution I found was:

    :::bash
    echo ':set term=xterm' >> ~/.vim/vimrc

>

    :::bash
    echo 'unbind-key -n C-Left' >> ~/.byobu/keybindings.tmux
    echo 'unbind-key -n C-Right' >> ~/.byobu/keybindings.tmux

>

    :::bash
    echo 'set-window-option -g xterm-keys on' >> ~/.byobu/.tmux.conf
    echo "set -g terminal-overrides 'xterm*:smcup@:rmcup@'" >> ~/.byobu/.tmux.conf



### References

[1] <http://www.saltycrane.com/blog/2012/10/how-start-long-running-process-screen-and-detach-it/>

[2] <http://tmux.sourceforge.net/>

[3] <http://byobu.co/documentation.html>

[4] <http://www.howtogeek.com/58487/how-to-easily-multitask-in-a-linux-terminal-with-byobu/>

[5] <http://blog.smartlogicsolutions.com/2010/01/22/ubuntu-byobu-landscape/>
